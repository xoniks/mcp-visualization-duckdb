# Ollama LLM client integration
"""
Ollama LLM client for natural language processing
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
import httpx

# ✅ Import the config_manager instance directly
from config.settings import config_manager

# ✅ OPTIONAL: Import specific config types for type hinting
from config.settings import OllamaConfig, LLMPromptsConfig

# ❌ The following import needs to be adjusted.
# Assuming 'prompts.py' is in the same directory (llm)
# and PromptManager will now take the prompts config directly.
# If PromptManager is a standalone class that loads its own prompts,
# you'll need to pass the prompts configuration to it.
# Let's assume for now it needs the LLMPromptsConfig.
# If PromptManager is meant to load from files, then this import might stay,
# but its __init__ would need to be updated to not use the old config getter.
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama LLM"""

    def __init__(self):
        # ✅ Get the full settings object from the global config_manager
        self.settings = config_manager.get_settings()
        # ✅ Access the specific Ollama configuration section
        self.ollama_config: OllamaConfig = self.settings.llm.ollama
        # ✅ Pass the prompts configuration to PromptManager
        self.prompt_manager = PromptManager(self.settings.llm.prompts)
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(timeout=self.ollama_config.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.ollama_config.timeout)
        return self.client

    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate response from Ollama"""
        try:
            client = await self._get_client()

            payload = {
                "model": model or self.ollama_config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get(
                        "temperature", self.ollama_config.temperature
                    ),
                    "num_predict": kwargs.get(
                        "max_tokens", self.ollama_config.max_tokens
                    ),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                },
            }

            logger.debug(f"Sending request to Ollama: {payload['model']}")

            response = await client.post(
                f"{self.ollama_config.base_url}/api/generate", json=payload
            )

            response.raise_for_status()
            result = response.json()

            generated_text = result.get("response", "")
            logger.debug(f"Received response: {generated_text[:100]}...")

            return generated_text

        except httpx.TimeoutException:
            logger.error("Timeout calling Ollama API")
            return "Error: Request timed out. Please check if Ollama is running and responsive."

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Ollama API: {e}")
            return f"Error: HTTP {e.response.status_code} - {e.response.text}"

        except Exception as e:
            logger.error(f"Unexpected error calling Ollama API: {e}")
            return f"Error: Could not process request with local LLM: {e}"

    async def detect_chart_type(
        self, request: str, columns: List[str], table_name: str
    ) -> Dict[str, Any]:
        """Detect appropriate chart type from natural language request"""
        try:
            prompt = self.prompt_manager.get_chart_type_detection_prompt(
                request=request, columns=columns, table_name=table_name
            )

            response = await self.generate(prompt, temperature=0.1)

            # Try to parse JSON response
            try:
                parsed_response = json.loads(response.strip())

                # Validate response structure
                if "chart_type" in parsed_response:
                    return {
                        "chart_type": parsed_response.get("chart_type", "bar"),
                        "confidence": parsed_response.get("confidence", 0.5),
                        "reasoning": parsed_response.get("reasoning", ""),
                        "success": True,
                    }

            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON from LLM response: {response}")

            # Fallback to keyword-based detection
            return self._fallback_chart_detection(request, columns)

        except Exception as e:
            logger.error(f"Error in chart type detection: {e}")
            return self._fallback_chart_detection(request, columns)

    def _fallback_chart_detection(
        self, request: str, columns: List[str]
    ) -> Dict[str, Any]:
        """Fallback chart type detection using keyword matching"""
        request_lower = request.lower()

        # Chart type keywords
        chart_keywords = {
            "scatter": ["scatter", "correlation", "relationship", "vs", "against"],
            "line": [
                "line",
                "trend",
                "over time",
                "timeline",
                "time series",
                "temporal",
            ],
            "pie": [
                "pie",
                "proportion",
                "percentage",
                "share",
                "distribution",
                "breakdown",
            ],
            "histogram": ["histogram", "distribution", "frequency", "bins"],
            "box": ["box", "boxplot", "quartile", "outlier"],
            "heatmap": ["heatmap", "heat map", "correlation matrix", "matrix"],
            "area": ["area", "filled", "cumulative"],
        }

        # Score each chart type
        scores = {}
        for chart_type, keywords in chart_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                scores[chart_type] = score

        # Determine best chart type
        if scores:
            best_chart = max(scores, key=scores.get)
            confidence = min(scores[best_chart] * 0.3, 0.9)  # Scale confidence
        else:
            # Default based on column analysis
            best_chart = self._default_chart_for_columns(columns)
            confidence = 0.3

        return {
            "chart_type": best_chart,
            "confidence": confidence,
            "reasoning": f"Keyword-based detection (fallback)",
            "success": True,
        }

    def _default_chart_for_columns(self, columns: List[str]) -> str:
        """Choose default chart type based on available columns"""
        if len(columns) >= 2:
            return "scatter"  # Good for exploring relationships
        else:
            return "histogram"  # Good for single column analysis

    async def suggest_column_mappings(
        self, chart_type: str, columns: List[Dict[str, str]], request: str
    ) -> Dict[str, Any]:
        """Suggest appropriate column mappings for a chart type"""
        try:
            prompt = self.prompt_manager.get_column_suggestion_prompt(
                chart_type=chart_type, columns=columns, request=request
            )

            response = await self.generate(prompt, temperature=0.1)

            # Try to parse JSON response
            try:
                parsed_response = json.loads(response.strip())
                return {
                    "suggestions": parsed_response.get("suggestions", {}),
                    "success": True,
                }

            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON from LLM response: {response}")

            # Fallback to rule-based suggestions
            return self._fallback_column_suggestions(chart_type, columns)

        except Exception as e:
            logger.error(f"Error in column suggestion: {e}")
            return self._fallback_column_suggestions(chart_type, columns)

    def _fallback_column_suggestions(
        self, chart_type: str, columns: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Fallback column suggestions using rule-based logic"""
        suggestions = {}

        # Categorize columns by type
        numeric_cols = [
            col["name"]
            for col in columns
            if any(
                t in col["type"].upper()
                for t in ["INTEGER", "BIGINT", "DOUBLE", "FLOAT", "DECIMAL", "NUMERIC"]
            )
        ]

        categorical_cols = [
            col["name"]
            for col in columns
            if any(t in col["type"].upper() for t in ["VARCHAR", "TEXT", "STRING"])
        ]

        temporal_cols = [
            col["name"]
            for col in columns
            if any(t in col["type"].upper() for t in ["DATE", "TIMESTAMP", "TIME"])
        ]

        # Chart-specific suggestions
        if chart_type == "bar":
            if categorical_cols and numeric_cols:
                suggestions["x_axis"] = categorical_cols[0]
                suggestions["y_axis"] = numeric_cols[0]
                if len(categorical_cols) > 1:
                    suggestions["color"] = categorical_cols[1]

        elif chart_type == "line":
            if temporal_cols and numeric_cols:
                suggestions["x_axis"] = temporal_cols[0]
                suggestions["y_axis"] = numeric_cols[0]
            elif numeric_cols and len(numeric_cols) >= 2:
                suggestions["x_axis"] = numeric_cols[0]
                suggestions["y_axis"] = numeric_cols[1]

        elif chart_type == "scatter":
            if len(numeric_cols) >= 2:
                suggestions["x_axis"] = numeric_cols[0]
                suggestions["y_axis"] = numeric_cols[1]
                if len(numeric_cols) > 2:
                    suggestions["size"] = numeric_cols[2]
                if categorical_cols:
                    suggestions["color"] = categorical_cols[0]

        elif chart_type == "pie":
            if categorical_cols and numeric_cols:
                suggestions["category"] = categorical_cols[0]
                suggestions["values"] = numeric_cols[0]

        elif chart_type == "histogram":
            if numeric_cols:
                suggestions["column"] = numeric_cols[0]

        return {"suggestions": suggestions, "success": True, "method": "rule-based"}

    async def generate_insights_description(
        self, chart_type: str, data_summary: Dict[str, Any], insights: Dict[str, Any]
    ) -> str:
        """Generate natural language description of insights"""
        try:
            prompt = self.prompt_manager.get_insights_description_prompt(
                chart_type=chart_type, data_summary=data_summary, insights=insights
            )

            response = await self.generate(prompt, temperature=0.3)
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating insights description: {e}")
            return "Unable to generate insights description."

    async def explain_chart(
        self,
        chart_type: str,
        column_mappings: Dict[str, str],
        data_preview: List[Dict[str, Any]],
    ) -> str:
        """Generate explanation of what the chart shows"""
        try:
            prompt = self.prompt_manager.get_chart_explanation_prompt(
                chart_type=chart_type,
                column_mappings=column_mappings,
                data_preview=data_preview,
            )

            response = await self.generate(prompt, temperature=0.2)
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating chart explanation: {e}")
            return f"This {chart_type} chart shows the relationship between your selected data columns."

    async def check_connection(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.ollama_config.base_url}/api/tags")
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.ollama_config.base_url}/api/tags")
            response.raise_for_status()

            models_data = response.json()
            return [model["name"] for model in models_data.get("models", [])]

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None


# Convenience function for one-off requests
async def quick_generate(prompt: str, model: Optional[str] = None) -> str:
    """Quick generation without context management"""
    # ✅ Instantiate OllamaClient directly. It will get its config from config_manager.
    async with OllamaClient() as client:
        return await client.generate(prompt, model)
