# LLM prompts
"""
Prompt templates for LLM interactions
"""

import logging
from typing import Dict, List, Any, Optional
import json

# ✅ Import the LLMPromptsConfig type
from config.settings import LLMPromptsConfig

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompt templates for different LLM tasks, loaded from config"""

    def __init__(self, prompts_config: LLMPromptsConfig):  # ✅ Accept prompts_config
        self.prompts_config = prompts_config
        # Self.templates will now be populated from prompts_config
        self.templates = {
            "chart_type_detection": self.prompts_config.chart_type_detection_template,
            "column_suggestion": self.prompts_config.column_suggestion_template,
            "insights_description": self.prompts_config.insights_description_template,
            "chart_explanation": self.prompts_config.chart_explanation_template,
            "data_quality_check": self.prompts_config.data_quality_check_template,
            "followup_questions": self.prompts_config.followup_questions_template,
        }
        logger.info("PromptManager initialized with templates from configuration.")

    def get_chart_type_detection_prompt(
        self, request: str, columns: List[str], table_name: str
    ) -> str:
        """Get prompt for chart type detection"""
        columns_str = ", ".join(columns)
        return self.templates["chart_type_detection"].format(
            request=request, table_name=table_name, columns=columns_str
        )

    def get_column_suggestion_prompt(
        self, chart_type: str, columns: List[Dict[str, str]], request: str
    ) -> str:
        """Get prompt for column mapping suggestions"""
        columns_info = []
        for col in columns:
            columns_info.append(f"{col['name']} ({col['type']})")

        columns_str = ", ".join(columns_info)
        return self.templates["column_suggestion"].format(
            chart_type=chart_type, columns=columns_str, request=request
        )

    def get_insights_description_prompt(
        self, chart_type: str, data_summary: Dict[str, Any], insights: Dict[str, Any]
    ) -> str:
        """Get prompt for insights description"""
        return self.templates["insights_description"].format(
            chart_type=chart_type,
            data_summary=json.dumps(data_summary, indent=2),
            insights=json.dumps(insights, indent=2),
        )

    def get_chart_explanation_prompt(
        self,
        chart_type: str,
        column_mappings: Dict[str, str],
        data_preview: List[Dict[str, Any]],
    ) -> str:
        """Get prompt for chart explanation"""
        # Limit data preview for prompt
        preview = data_preview[:5] if len(data_preview) > 5 else data_preview

        return self.templates["chart_explanation"].format(
            chart_type=chart_type,
            column_mappings=json.dumps(column_mappings, indent=2),
            data_preview=json.dumps(preview, indent=2),
        )

    def get_data_quality_prompt(
        self,
        columns: List[Dict[str, str]],
        sample_data: List[Dict[str, Any]],
        basic_stats: Dict[str, Any],
    ) -> str:
        """Get prompt for data quality analysis"""
        return self.templates["data_quality_check"].format(
            columns=json.dumps(columns, indent=2),
            sample_data=json.dumps(sample_data[:10], indent=2),  # Limit sample size
            basic_stats=json.dumps(basic_stats, indent=2),
        )

    def get_followup_questions_prompt(
        self,
        chart_type: str,
        chart_context: str,
        insights: Dict[str, Any],
        available_columns: List[str],
    ) -> str:
        """Get prompt for generating follow-up questions"""
        return self.templates["followup_questions"].format(
            chart_type=chart_type,
            chart_context=chart_context,
            insights=json.dumps(insights, indent=2),
            available_columns=", ".join(available_columns),
        )

    def customize_prompt(self, template_name: str, custom_template: str):
        """Add or update a prompt template"""
        # This method should ideally modify the prompts_config or save to a file
        # For now, it will only update the in-memory templates dict.
        # Consider if you want this to persist or just be for runtime.
        self.templates[template_name] = custom_template
        logger.info(f"Updated prompt template: {template_name}")

    def get_template(self, template_name: str) -> Optional[str]:
        """Get a raw template"""
        return self.templates.get(template_name)

    def list_templates(self) -> List[str]:
        """List available template names"""
        return list(self.templates.keys())
