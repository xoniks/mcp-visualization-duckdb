# Simple fallback for LLM functionality
"""
Simple fallback client that provides chart suggestions without external LLM
Uses rule-based logic for chart type detection and column mappings
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SimpleFallbackClient:
    """Fallback client for chart analysis without external LLM dependency"""

    def __init__(self):
        # Simple initialization without config dependency
        pass

    async def detect_chart_type(
        self, request: str, columns: List[str], table_name: str
    ) -> Dict[str, Any]:
        """Detect appropriate chart type using rule-based logic"""
        return self._fallback_chart_detection(request, columns)

    def _fallback_chart_detection(
        self, request: str, columns: List[str]
    ) -> Dict[str, Any]:
        """Rule-based chart type detection using keyword matching"""
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
            confidence = min(scores[best_chart] * 0.3, 0.9)
        else:
            # Default based on column analysis
            best_chart = self._default_chart_for_columns(columns)
            confidence = 0.3

        return {
            "chart_type": best_chart,
            "confidence": confidence,
            "reasoning": f"Rule-based detection using keyword matching",
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
        """Suggest appropriate column mappings using rule-based logic"""
        return self._fallback_column_suggestions(chart_type, columns)

    def _fallback_column_suggestions(
        self, chart_type: str, columns: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Rule-based column suggestions"""
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
        """Generate simple insights description"""
        try:
            chart_name = chart_type.title()
            description = f"This {chart_name} chart visualizes your data"
            
            if "max" in insights:
                description += f" with a maximum value of {insights['max']:.2f}"
            if "min" in insights:
                description += f" and minimum value of {insights['min']:.2f}"
                
            description += "."
            return description
        except Exception as e:
            logger.error(f"Error generating insights description: {e}")
            return f"This {chart_type} chart shows patterns in your data."

    async def explain_chart(
        self,
        chart_type: str,
        column_mappings: Dict[str, str],
        data_preview: List[Dict[str, Any]],
    ) -> str:
        """Generate simple chart explanation"""
        try:
            chart_name = chart_type.title()
            explanation = f"This {chart_name} chart shows"
            
            if "x_axis" in column_mappings and "y_axis" in column_mappings:
                explanation += f" the relationship between {column_mappings['x_axis']} and {column_mappings['y_axis']}"
            elif "column" in column_mappings:
                explanation += f" the distribution of {column_mappings['column']}"
            else:
                explanation += " your selected data"
                
            explanation += ". Use it to identify patterns and trends in your dataset."
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating chart explanation: {e}")
            return f"This {chart_type} chart shows the relationship between your selected data columns."

    async def check_connection(self) -> bool:
        """Always returns True for fallback client"""
        return True

    async def list_models(self) -> List[str]:
        """Return empty list for fallback client"""
        return []

    async def close(self):
        """No resources to close for fallback client"""
        pass


# Convenience function for one-off requests
async def quick_generate(prompt: str, model: Optional[str] = None) -> str:
    """Quick generation using fallback logic"""
    return "Simple rule-based response (no LLM required)"