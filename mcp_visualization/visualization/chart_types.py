# Chart type definitions
"""
Chart type definitions and validation
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Supported chart types"""

    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    AREA = "area"


class InsightType(Enum):
    """Available insight types"""

    MAX = "max"
    MIN = "min"
    MEAN = "mean"
    MEDIAN = "median"
    DISTINCT_COUNT = "distinct_count"
    TOTAL_COUNT = "total_count"
    CORRELATION = "correlation"
    TREND = "trend"
    OUTLIERS = "outliers"
    DISTRIBUTION = "distribution"


@dataclass
class ColumnRequirement:
    """Defines column requirements for a chart type"""

    name: str
    required: bool
    data_types: List[str]  # numeric, categorical, temporal, any
    description: str


@dataclass
class ChartDefinition:
    """Complete definition of a chart type"""

    chart_type: ChartType
    name: str
    description: str
    use_cases: List[str]
    column_requirements: List[ColumnRequirement]
    supported_insights: List[InsightType]
    min_columns: int
    max_columns: Optional[int] = None


class ChartTypeRegistry:
    """Registry of chart type definitions and validation"""

    def __init__(self):
        self.chart_definitions: Dict[ChartType, ChartDefinition] = {}
        self._initialize_definitions()

    def _initialize_definitions(self):
        """Initialize chart type definitions"""

        # Bar Chart
        self.chart_definitions[ChartType.BAR] = ChartDefinition(
            chart_type=ChartType.BAR,
            name="Bar Chart",
            description="Compare values across different categories",
            use_cases=[
                "Compare sales by region",
                "Show counts by category",
                "Display rankings",
                "Compare performance metrics",
            ],
            column_requirements=[
                ColumnRequirement(
                    "x_axis", True, ["categorical"], "Categories to compare"
                ),
                ColumnRequirement("y_axis", True, ["numeric"], "Values to display"),
                ColumnRequirement(
                    "color", False, ["categorical"], "Additional grouping dimension"
                ),
            ],
            supported_insights=[
                InsightType.MAX,
                InsightType.MIN,
                InsightType.MEAN,
                InsightType.TOTAL_COUNT,
                InsightType.DISTINCT_COUNT,
            ],
            min_columns=2,
        )

        # Line Chart
        self.chart_definitions[ChartType.LINE] = ChartDefinition(
            chart_type=ChartType.LINE,
            name="Line Chart",
            description="Show trends and changes over continuous data",
            use_cases=[
                "Show trends over time",
                "Display continuous relationships",
                "Track changes in metrics",
                "Compare multiple series",
            ],
            column_requirements=[
                ColumnRequirement(
                    "x_axis",
                    True,
                    ["numeric", "temporal"],
                    "Continuous or time-based data",
                ),
                ColumnRequirement("y_axis", True, ["numeric"], "Values to track"),
                ColumnRequirement("color", False, ["categorical"], "Series grouping"),
            ],
            supported_insights=[
                InsightType.TREND,
                InsightType.MAX,
                InsightType.MIN,
                InsightType.MEAN,
                InsightType.CORRELATION,
            ],
            min_columns=2,
        )

        # Scatter Plot
        self.chart_definitions[ChartType.SCATTER] = ChartDefinition(
            chart_type=ChartType.SCATTER,
            name="Scatter Plot",
            description="Explore relationships between two numeric variables",
            use_cases=[
                "Find correlations between variables",
                "Identify clusters and outliers",
                "Explore data relationships",
                "Show data distribution patterns",
            ],
            column_requirements=[
                ColumnRequirement(
                    "x_axis", True, ["numeric"], "First numeric variable"
                ),
                ColumnRequirement(
                    "y_axis", True, ["numeric"], "Second numeric variable"
                ),
                ColumnRequirement(
                    "color", False, ["categorical", "numeric"], "Point coloring"
                ),
                ColumnRequirement("size", False, ["numeric"], "Point sizing"),
            ],
            supported_insights=[
                InsightType.CORRELATION,
                InsightType.OUTLIERS,
                InsightType.DISTRIBUTION,
                InsightType.MAX,
                InsightType.MIN,
                InsightType.MEAN,
            ],
            min_columns=2,
        )

        # Pie Chart
        self.chart_definitions[ChartType.PIE] = ChartDefinition(
            chart_type=ChartType.PIE,
            name="Pie Chart",
            description="Show proportions and parts of a whole",
            use_cases=[
                "Show market share breakdown",
                "Display category proportions",
                "Show budget allocation",
                "Demonstrate composition",
            ],
            column_requirements=[
                ColumnRequirement(
                    "category", True, ["categorical"], "Categories for slices"
                ),
                ColumnRequirement(
                    "values", True, ["numeric"], "Values for slice sizes"
                ),
            ],
            supported_insights=[
                InsightType.TOTAL_COUNT,
                InsightType.DISTINCT_COUNT,
                InsightType.MAX,
                InsightType.MIN,
            ],
            min_columns=2,
        )

        # Histogram
        self.chart_definitions[ChartType.HISTOGRAM] = ChartDefinition(
            chart_type=ChartType.HISTOGRAM,
            name="Histogram",
            description="Show distribution of a numeric variable",
            use_cases=[
                "Analyze data distribution",
                "Find data patterns",
                "Identify skewness",
                "Check for normality",
            ],
            column_requirements=[
                ColumnRequirement(
                    "column", True, ["numeric"], "Numeric column to analyze"
                )
            ],
            supported_insights=[
                InsightType.DISTRIBUTION,
                InsightType.MEAN,
                InsightType.MEDIAN,
                InsightType.MAX,
                InsightType.MIN,
                InsightType.OUTLIERS,
            ],
            min_columns=1,
        )

        # Box Plot
        self.chart_definitions[ChartType.BOX] = ChartDefinition(
            chart_type=ChartType.BOX,
            name="Box Plot",
            description="Show distribution with quartiles and outliers",
            use_cases=[
                "Compare distributions across groups",
                "Identify outliers",
                "Show data spread and skewness",
                "Statistical distribution analysis",
            ],
            column_requirements=[
                ColumnRequirement(
                    "column", True, ["numeric"], "Numeric column for distribution"
                ),
                ColumnRequirement(
                    "groupby", False, ["categorical"], "Grouping variable"
                ),
            ],
            supported_insights=[
                InsightType.OUTLIERS,
                InsightType.DISTRIBUTION,
                InsightType.MEDIAN,
                InsightType.MAX,
                InsightType.MIN,
            ],
            min_columns=1,
        )

        # Heatmap
        self.chart_definitions[ChartType.HEATMAP] = ChartDefinition(
            chart_type=ChartType.HEATMAP,
            name="Heatmap",
            description="Show patterns in 2D data or correlation matrix",
            use_cases=[
                "Display correlation matrices",
                "Show patterns across two dimensions",
                "Visualize intensity data",
                "Compare values across grid",
            ],
            column_requirements=[
                ColumnRequirement(
                    "x_axis", True, ["categorical", "numeric"], "First dimension"
                ),
                ColumnRequirement(
                    "y_axis", True, ["categorical", "numeric"], "Second dimension"
                ),
                ColumnRequirement("values", False, ["numeric"], "Values for intensity"),
            ],
            supported_insights=[
                InsightType.CORRELATION,
                InsightType.MAX,
                InsightType.MIN,
                InsightType.MEAN,
                InsightType.DISTRIBUTION,
            ],
            min_columns=2,
        )

        # Area Chart
        self.chart_definitions[ChartType.AREA] = ChartDefinition(
            chart_type=ChartType.AREA,
            name="Area Chart",
            description="Show cumulative values and filled trends",
            use_cases=[
                "Show cumulative totals over time",
                "Display stacked categories",
                "Emphasize magnitude of change",
                "Show contribution to total",
            ],
            column_requirements=[
                ColumnRequirement(
                    "x_axis", True, ["numeric", "temporal"], "Continuous data axis"
                ),
                ColumnRequirement("y_axis", True, ["numeric"], "Values to fill"),
                ColumnRequirement(
                    "color", False, ["categorical"], "Series for stacking"
                ),
            ],
            supported_insights=[
                InsightType.TREND,
                InsightType.TOTAL_COUNT,
                InsightType.MAX,
                InsightType.MIN,
                InsightType.MEAN,
            ],
            min_columns=2,
        )

    def get_chart_definition(self, chart_type: ChartType) -> Optional[ChartDefinition]:
        """Get definition for a chart type"""
        return self.chart_definitions.get(chart_type)

    def get_all_chart_types(self) -> List[ChartType]:
        """Get all supported chart types"""
        return list(self.chart_definitions.keys())

    def get_chart_requirements(self, chart_type: ChartType) -> List[ColumnRequirement]:
        """Get column requirements for a chart type"""
        definition = self.get_chart_definition(chart_type)
        return definition.column_requirements if definition else []

    def get_supported_insights(self, chart_type: ChartType) -> List[InsightType]:
        """Get supported insights for a chart type"""
        definition = self.get_chart_definition(chart_type)
        return definition.supported_insights if definition else []

    def validate_chart_configuration(
        self,
        chart_type: ChartType,
        column_mappings: Dict[str, str],
        available_columns: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Validate if column mappings satisfy chart requirements"""
        definition = self.get_chart_definition(chart_type)
        if not definition:
            return {"valid": False, "error": f"Unknown chart type: {chart_type}"}

        # Create column lookup
        column_lookup = {col["name"]: col for col in available_columns}

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_required": [],
            "invalid_types": [],
        }

        # Check each requirement
        for req in definition.column_requirements:
            mapped_column = column_mappings.get(req.name)

            if req.required and not mapped_column:
                validation_result["missing_required"].append(req.name)
                validation_result["errors"].append(
                    f"Required column '{req.name}' not specified"
                )
                continue

            if mapped_column and mapped_column in column_lookup:
                column_info = column_lookup[mapped_column]
                column_type = self._categorize_column_type(column_info["type"])

                if "any" not in req.data_types and column_type not in req.data_types:
                    validation_result["invalid_types"].append(
                        {
                            "requirement": req.name,
                            "expected": req.data_types,
                            "actual": column_type,
                            "column": mapped_column,
                        }
                    )
                    validation_result["errors"].append(
                        f"Column '{mapped_column}' for '{req.name}' should be {'/'.join(req.data_types)}, "
                        f"but is {column_type}"
                    )

        # Check minimum columns
        required_mappings = len(
            [req for req in definition.column_requirements if req.required]
        )
        provided_mappings = len([v for v in column_mappings.values() if v])

        if provided_mappings < definition.min_columns:
            validation_result["errors"].append(
                f"Chart requires at least {definition.min_columns} columns, "
                f"but only {provided_mappings} provided"
            )

        validation_result["valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def _categorize_column_type(self, sql_type: str) -> str:
        """Categorize SQL type into visualization-relevant categories"""
        sql_type_upper = sql_type.upper()

        # Numeric types
        if any(
            t in sql_type_upper
            for t in [
                "INTEGER",
                "BIGINT",
                "DOUBLE",
                "FLOAT",
                "DECIMAL",
                "NUMERIC",
                "REAL",
            ]
        ):
            return "numeric"

        # Temporal types
        if any(t in sql_type_upper for t in ["DATE", "TIMESTAMP", "TIME"]):
            return "temporal"

        # Categorical/text types
        if any(t in sql_type_upper for t in ["VARCHAR", "TEXT", "STRING", "CHAR"]):
            return "categorical"

        # Boolean
        if "BOOLEAN" in sql_type_upper or "BOOL" in sql_type_upper:
            return "categorical"

        # Default to categorical
        return "categorical"

    def suggest_chart_types(
        self, available_columns: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Suggest appropriate chart types based on available columns"""
        suggestions = []

        # Categorize available columns
        column_types = {}
        for col in available_columns:
            col_type = self._categorize_column_type(col["type"])
            if col_type not in column_types:
                column_types[col_type] = []
            column_types[col_type].append(col["name"])

        numeric_count = len(column_types.get("numeric", []))
        categorical_count = len(column_types.get("categorical", []))
        temporal_count = len(column_types.get("temporal", []))

        # Generate suggestions based on data characteristics
        for chart_type, definition in self.chart_definitions.items():
            score = 0
            reason_parts = []

            # Check if requirements can be satisfied
            can_satisfy = True
            for req in definition.column_requirements:
                if req.required:
                    available_for_req = 0
                    for req_type in req.data_types:
                        if req_type == "any":
                            available_for_req = len(available_columns)
                            break
                        available_for_req += len(column_types.get(req_type, []))

                    if available_for_req == 0:
                        can_satisfy = False
                        break

                    score += min(available_for_req, 3)  # Cap contribution

            if not can_satisfy:
                continue

            # Bonus points for good fits
            if chart_type == ChartType.SCATTER and numeric_count >= 2:
                score += 2
                reason_parts.append(
                    f"good for exploring relationships between {numeric_count} numeric columns"
                )

            if (
                chart_type == ChartType.LINE
                and temporal_count > 0
                and numeric_count > 0
            ):
                score += 3
                reason_parts.append("excellent for time-based trends")

            if (
                chart_type == ChartType.BAR
                and categorical_count > 0
                and numeric_count > 0
            ):
                score += 2
                reason_parts.append("ideal for comparing categories")

            if (
                chart_type == ChartType.PIE
                and categorical_count > 0
                and numeric_count > 0
            ):
                # Lower score for pie charts (often overused)
                score += 1
                reason_parts.append("shows proportions well")

            if chart_type == ChartType.HISTOGRAM and numeric_count > 0:
                score += 2
                reason_parts.append("great for understanding data distribution")

            if score > 0:
                suggestions.append(
                    {
                        "chart_type": chart_type.value,
                        "name": definition.name,
                        "score": score,
                        "description": definition.description,
                        "reason": (
                            "; ".join(reason_parts)
                            if reason_parts
                            else definition.description
                        ),
                        "use_cases": definition.use_cases[:2],  # Top 2 use cases
                    }
                )

        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:5]  # Top 5 suggestions


# Global registry instance
chart_registry = ChartTypeRegistry()


# Convenience functions
def get_chart_definition(chart_type: ChartType) -> Optional[ChartDefinition]:
    """Get chart definition"""
    return chart_registry.get_chart_definition(chart_type)


def validate_chart_config(
    chart_type: ChartType,
    column_mappings: Dict[str, str],
    available_columns: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Validate chart configuration"""
    return chart_registry.validate_chart_configuration(
        chart_type, column_mappings, available_columns
    )


def suggest_charts(available_columns: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Suggest appropriate chart types"""
    return chart_registry.suggest_chart_types(available_columns)
