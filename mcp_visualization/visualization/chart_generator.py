"""
Chart generation using Plotly for interactive HTML widgets
"""

import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from .chart_types import ChartType
from .insights import InsightsCalculator, InsightType

# Import the config_manager instance directly
from ..config.settings import config_manager

# Import specific config types for type hinting
from ..config.settings import VisualizationConfig


logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate interactive Plotly charts as HTML widgets"""

    def __init__(self):
        # ✅ Get the full settings object from the global config_manager
        self.settings = config_manager.get_settings()
        # ✅ Access the specific Visualization configuration section
        self.visualization_config: VisualizationConfig = self.settings.visualization
        self.insights_calculator = (
            InsightsCalculator()
        )  # Assuming InsightsCalculator doesn't need config directly for now

        # Set default theme using the config
        pio.templates.default = self.visualization_config.default_theme

    def generate_chart(
        self,
        chart_type: ChartType,
        df: pd.DataFrame,
        column_mappings: Dict[str, str],
        insights_requested: List[InsightType] = None,
        title: str = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate chart and insights"""
        try:
            # Validate data
            if df.empty:
                raise ValueError("Dataset is empty")

            # Generate chart based on type
            if chart_type == ChartType.BAR:
                html_widget = self._create_bar_chart(df, column_mappings, title)
            elif chart_type == ChartType.LINE:
                html_widget = self._create_line_chart(df, column_mappings, title)
            elif chart_type == ChartType.SCATTER:
                html_widget = self._create_scatter_plot(df, column_mappings, title)
            elif chart_type == ChartType.PIE:
                html_widget = self._create_pie_chart(df, column_mappings, title)
            elif chart_type == ChartType.HISTOGRAM:
                html_widget = self._create_histogram(df, column_mappings, title)
            elif chart_type == ChartType.BOX:
                html_widget = self._create_box_plot(df, column_mappings, title)
            elif chart_type == ChartType.HEATMAP:
                html_widget = self._create_heatmap(df, column_mappings, title)
            elif chart_type == ChartType.AREA:
                html_widget = self._create_area_chart(df, column_mappings, title)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            # Calculate insights if requested
            insights = {}
            if insights_requested:
                insight_columns = self._get_insight_columns(column_mappings, chart_type)
                insights = self.insights_calculator.calculate_insights(
                    df, insight_columns, insights_requested
                )

            return html_widget, insights

        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {e}")
            raise

    def _create_bar_chart(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create bar chart"""
        x_col = mappings.get("x_axis")
        y_col = mappings.get("y_axis")
        color_col = mappings.get("color")

        if not x_col or not y_col:
            raise ValueError("Bar chart requires x_axis and y_axis columns")

        # Aggregate data if needed
        if color_col and color_col in df.columns:
            # Group by both x and color
            agg_df = df.groupby([x_col, color_col])[y_col].sum().reset_index()
        else:
            # Group by x only
            agg_df = df.groupby(x_col)[y_col].sum().reset_index()

        fig = px.bar(
            agg_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in df.columns else None,
            title=title or f"{y_col} by {x_col}",
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
        )

        fig.update_layout(
            width=self.visualization_config.width,  # ✅ Use self.visualization_config
            height=self.visualization_config.height,  # ✅ Use self.visualization_config
            showlegend=color_col is not None,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id=f"bar_chart_{id(fig)}")

    def _create_line_chart(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create line chart"""
        x_col = mappings.get("x_axis")
        y_col = mappings.get("y_axis")
        color_col = mappings.get("color")

        if not x_col or not y_col:
            raise ValueError("Line chart requires x_axis and y_axis columns")

        # Sort by x-axis for proper line connection
        df_sorted = df.sort_values(x_col)

        fig = px.line(
            df_sorted,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in df.columns else None,
            title=title or f"{y_col} over {x_col}",
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
        )

        fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=6))

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"line_chart_{id(fig)}")

    def _create_scatter_plot(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create scatter plot"""
        x_col = mappings.get("x_axis")
        y_col = mappings.get("y_axis")
        color_col = mappings.get("color")
        size_col = mappings.get("size")

        if not x_col or not y_col:
            raise ValueError("Scatter plot requires x_axis and y_axis columns")

        # Handle size column
        size = None
        if (
            size_col
            and size_col in df.columns
            and pd.api.types.is_numeric_dtype(df[size_col])
        ):
            size = size_col

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in df.columns else None,
            size=size,
            title=title or f"{y_col} vs {x_col}",
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
            opacity=0.7,
        )

        fig.update_traces(marker=dict(size=8 if not size else None))

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"scatter_plot_{id(fig)}")

    def _create_pie_chart(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create pie chart"""
        category_col = mappings.get("category")
        values_col = mappings.get("values")

        if not category_col or not values_col:
            raise ValueError("Pie chart requires category and values columns")

        # Aggregate values by category
        agg_df = df.groupby(category_col)[values_col].sum().reset_index()

        fig = px.pie(
            agg_df,
            names=category_col,
            values=values_col,
            title=title or f"Distribution of {values_col} by {category_col}",
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"pie_chart_{id(fig)}")

    def _create_histogram(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create histogram"""
        column = mappings.get("column")

        if not column:
            raise ValueError("Histogram requires a column to analyze")

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column {column} must be numeric for histogram")

        fig = px.histogram(
            df,
            x=column,
            nbins=30,
            title=title or f"Distribution of {column}",
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
        )

        fig.update_traces(opacity=0.7)

        fig.update_layout(
            width=self.visualization_config.width,  # ✅ Use self.visualization_config
            height=self.visualization_config.height,  # ✅ Use self.visualization_config
            bargap=0.1,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id=f"histogram_{id(fig)}")

    def _create_box_plot(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create box plot"""
        column = mappings.get("column")
        groupby = mappings.get("groupby")

        if not column:
            raise ValueError("Box plot requires a column to analyze")

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column {column} must be numeric for box plot")

        fig = px.box(
            df,
            y=column,
            x=groupby if groupby and groupby in df.columns else None,
            title=title
            or f"Distribution of {column}" + (f" by {groupby}" if groupby else ""),
            color_discrete_sequence=self.visualization_config.color_schemes[
                "categorical"
            ],  # ✅ Use self.visualization_config
        )

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"box_plot_{id(fig)}")

    def _create_heatmap(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create heatmap"""
        x_col = mappings.get("x_axis")
        y_col = mappings.get("y_axis")
        values_col = mappings.get("values")

        if not x_col or not y_col:
            raise ValueError("Heatmap requires x_axis and y_axis columns")

        # If no values column specified, create correlation heatmap
        if not values_col:
            # Select numeric columns for correlation
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                raise ValueError(
                    "Need at least 2 numeric columns for correlation heatmap"
                )

            corr_matrix = df[numeric_cols].corr()

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title=title or "Correlation Matrix",
                color_continuous_scale=self.visualization_config.color_schemes[
                    "diverging"
                ],  # ✅ Use self.visualization_config
            )
        else:
            # Pivot data for heatmap
            try:
                pivot_df = df.pivot_table(
                    index=y_col, columns=x_col, values=values_col, aggfunc="mean"
                )

                fig = px.imshow(
                    pivot_df,
                    text_auto=True,
                    aspect="auto",
                    title=title or f"{values_col} by {x_col} and {y_col}",
                    color_continuous_scale=self.visualization_config.color_schemes[
                        "sequential"
                    ],  # ✅ Use self.visualization_config
                )
            except Exception as e:
                raise ValueError(f"Could not create heatmap pivot: {e}")

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"heatmap_{id(fig)}")

    def _create_area_chart(
        self, df: pd.DataFrame, mappings: Dict[str, str], title: str = None
    ) -> str:
        """Create area chart"""
        x_col = mappings.get("x_axis")
        y_col = mappings.get("y_axis")
        color_col = mappings.get("color")

        if not x_col or not y_col:
            raise ValueError("Area chart requires x_axis and y_axis columns")

        # Sort by x-axis
        df_sorted = df.sort_values(x_col)

        if color_col and color_col in df.columns:
            # Stacked area chart
            fig = px.area(
                df_sorted,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title or f"{y_col} over {x_col}",
                color_discrete_sequence=self.visualization_config.color_schemes[
                    "categorical"
                ],  # ✅ Use self.visualization_config
            )
        else:
            # Single area chart
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df_sorted[x_col],
                    y=df_sorted[y_col],
                    fill="tonexty",
                    mode="lines",
                    name=y_col,
                    line=dict(
                        color=self.visualization_config.color_schemes["categorical"][0]
                    ),  # ✅ Use self.visualization_config
                )
            )

            fig.update_layout(
                title=title or f"{y_col} over {x_col}",
                xaxis_title=x_col,
                yaxis_title=y_col,
            )

        fig.update_layout(
            width=self.visualization_config.width,
            height=self.visualization_config.height,
        )  # ✅ Use self.visualization_config

        return fig.to_html(include_plotlyjs="cdn", div_id=f"area_chart_{id(fig)}")

    def _get_insight_columns(
        self, mappings: Dict[str, str], chart_type: ChartType
    ) -> List[str]:
        """Get relevant columns for insights calculation"""
        columns = []

        # Add all mapped columns that exist
        for mapping_name, column_name in mappings.items():
            if column_name and column_name not in columns:
                columns.append(column_name)

        return columns

    def create_sample_chart(self, chart_type: ChartType = ChartType.BAR) -> str:
        """Create a sample chart for testing"""
        try:
            # Generate sample data
            np.random.seed(42)
            sample_data = {
                "categories": ["A", "B", "C", "D", "E"] * 20,
                "values": np.random.randint(10, 100, 100),
                "values2": np.random.randint(5, 50, 100),
                "dates": pd.date_range("2023-01-01", periods=100),
                "groups": np.random.choice(["Group1", "Group2", "Group3"], 100),
            }

            df = pd.DataFrame(sample_data)

            # Create appropriate mappings based on chart type
            if chart_type == ChartType.BAR:
                mappings = {
                    "x_axis": "categories",
                    "y_axis": "values",
                    "color": "groups",
                }
            elif chart_type == ChartType.LINE:
                mappings = {"x_axis": "dates", "y_axis": "values"}
            elif chart_type == ChartType.SCATTER:
                mappings = {"x_axis": "values", "y_axis": "values2", "color": "groups"}
            elif chart_type == ChartType.PIE:
                mappings = {"category": "categories", "values": "values"}
            else:
                mappings = {"column": "values"}

            html_widget, _ = self.generate_chart(
                chart_type, df, mappings, title="Sample Chart"
            )
            return html_widget

        except Exception as e:
            logger.error(f"Error creating sample chart: {e}")
            return f"<div>Error creating sample chart: {e}</div>"


# Convenience functions
def create_quick_chart(chart_type: str, df: pd.DataFrame, **mappings) -> str:
    """Quick chart creation function"""
    # ✅ Instantiate ChartGenerator directly. It will get its config from config_manager.
    generator = ChartGenerator()
    chart_type_enum = ChartType(chart_type)
    html_widget, _ = generator.generate_chart(chart_type_enum, df, mappings)
    return html_widget


def generate_chart_with_insights(
    chart_type: str,
    df: pd.DataFrame,
    mappings: Dict[str, str],
    insights: List[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Generate chart with insights"""
    # ✅ Instantiate ChartGenerator directly. It will get its config from config_manager.
    generator = ChartGenerator()
    chart_type_enum = ChartType(chart_type)

    insight_types = []
    if insights:
        for insight in insights:
            try:
                insight_types.append(InsightType(insight))
            except ValueError:
                logger.warning(f"Unknown insight type: {insight}")

    return generator.generate_chart(chart_type_enum, df, mappings, insight_types)
