"""
Statistical insights calculation for visualizations
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats

# Import config_manager and the relevant config types
from ..config.settings import config_manager, InsightsConfig, Settings
from .chart_types import InsightType

logger = logging.getLogger(__name__)


class InsightsCalculator:
    """Calculate statistical insights from data"""

    def __init__(self):
        # Update to use config_manager
        self.settings: Settings = config_manager.get_settings()
        self.config: InsightsConfig = self.settings.insights

    def _assess_distribution_type(self, series: pd.Series) -> str:
        """Assess the type of distribution"""
        try:
            skewness = stats.skew(series)
            kurtosis = stats.kurtosis(series)

            if abs(skewness) < 0.5:
                if abs(kurtosis) < 0.5:
                    return "approximately normal"
                elif kurtosis > 0.5:
                    return "heavy-tailed"
                else:
                    return "light-tailed"
            elif skewness > 0.5:
                return "right-skewed"
            else:
                return "left-skewed"

        except Exception:
            return "unknown"

    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        try:
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = series[(series < lower_bound) | (series > upper_bound)]

            return {
                "count": len(outliers),
                "percentage": round((len(outliers) / len(series)) * 100, 2),
                "lower_bound": self._format_value(lower_bound),
                "upper_bound": self._format_value(upper_bound),
                "outlier_values": [
                    self._format_value(v) for v in outliers.head(10).tolist()
                ],  # Show first 10
                "has_outliers": len(outliers) > 0,
            }

        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return {"error": str(e)}

    def _calculate_correlations(
        self, df: pd.DataFrame, columns: List[str]
    ) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns"""
        try:
            # Filter to numeric columns only
            numeric_columns = []
            for col in columns:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    numeric_columns.append(col)

            if len(numeric_columns) < 2:
                return {"error": "Need at least 2 numeric columns for correlation"}

            # Calculate correlation matrix
            corr_matrix = df[numeric_columns].corr()

            # Convert to nested dict format
            correlations = {}
            for col1 in numeric_columns:
                correlations[col1] = {}
                for col2 in numeric_columns:
                    corr_value = corr_matrix.loc[col1, col2]
                    correlations[col1][col2] = self._format_value(corr_value)

            # Find strong correlations
            strong_correlations = []
            threshold = self.config.correlation_threshold

            for i, col1 in enumerate(numeric_columns):
                for col2 in numeric_columns[i + 1 :]:  # Avoid duplicates
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) >= threshold:
                        strong_correlations.append(
                            {
                                "column1": col1,
                                "column2": col2,
                                "correlation": self._format_value(corr_value),
                                "strength": self._interpret_correlation_strength(
                                    abs(corr_value)
                                ),
                                "direction": (
                                    "positive" if corr_value > 0 else "negative"
                                ),
                            }
                        )

            return {
                "matrix": correlations,
                "strong_correlations": strong_correlations,
                "threshold": threshold,
            }

        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {"error": str(e)}

    def _interpret_correlation_strength(self, abs_corr: float) -> str:
        """Interpret correlation strength"""
        if abs_corr >= 0.8:
            return "very strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very weak"

    def _analyze_trends(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Analyze trends in the data"""
        try:
            trends = {}

            # Look for time-based columns
            temporal_columns = []
            numeric_columns = []

            for col in columns:
                if col not in df.columns:
                    continue

                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    temporal_columns.append(col)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    numeric_columns.append(col)

            # Analyze trends for time series data
            if temporal_columns and numeric_columns:
                for time_col in temporal_columns:
                    for numeric_col in numeric_columns:
                        trend_info = self._calculate_time_trend(
                            df, time_col, numeric_col
                        )
                        trends[f"{numeric_col}_over_{time_col}"] = trend_info

            # Analyze general trends in numeric data
            elif len(numeric_columns) >= 2:
                # Use first column as x-axis, others as potential trends
                x_col = numeric_columns[0]
                for y_col in numeric_columns[1:]:
                    trend_info = self._calculate_numeric_trend(df, x_col, y_col)
                    trends[f"{y_col}_vs_{x_col}"] = trend_info

            return trends

        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {"error": str(e)}

    def _calculate_time_trend(
        self, df: pd.DataFrame, time_col: str, value_col: str
    ) -> Dict[str, Any]:
        """Calculate trend for time series data"""
        try:
            # Sort by time
            df_sorted = df[[time_col, value_col]].dropna().sort_values(time_col)

            if len(df_sorted) < self.config.trend_detection.min_points:
                return {"error": "Insufficient data for trend analysis"}

            # Convert to numeric for trend calculation
            x = np.arange(len(df_sorted))
            y = df_sorted[value_col].values

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            # Calculate percentage change
            first_value = y[0]
            last_value = y[-1]
            pct_change = (
                ((last_value - first_value) / first_value) * 100
                if first_value != 0
                else 0
            )

            return {
                "direction": (
                    "increasing"
                    if slope > 0
                    else "decreasing" if slope < 0 else "stable"
                ),
                "strength": self._interpret_correlation_strength(abs(r_value)),
                "slope": self._format_value(slope),
                "r_squared": self._format_value(r_value**2),
                "p_value": self._format_value(p_value),
                "percentage_change": self._format_value(pct_change),
                "significant": p_value < self.config.trend_detection.significance_level,
                "start_value": self._format_value(first_value),
                "end_value": self._format_value(last_value),
            }

        except Exception as e:
            logger.error(f"Error calculating time trend: {e}")
            return {"error": str(e)}

    def _calculate_numeric_trend(
        self, df: pd.DataFrame, x_col: str, y_col: str
    ) -> Dict[str, Any]:
        """Calculate trend between two numeric columns"""
        try:
            # Remove NaN values
            df_clean = df[[x_col, y_col]].dropna()

            if len(df_clean) < self.config.trend_detection.min_points:
                return {"error": "Insufficient data for trend analysis"}

            x = df_clean[x_col].values
            y = df_clean[y_col].values

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            return {
                "relationship": (
                    "positive"
                    if slope > 0
                    else "negative" if slope < 0 else "no relationship"
                ),
                "strength": self._interpret_correlation_strength(abs(r_value)),
                "slope": self._format_value(slope),
                "r_squared": self._format_value(r_value**2),
                "p_value": self._format_value(p_value),
                "correlation": self._format_value(r_value),
                "significant": p_value < self.config.trend_detection.significance_level,
            }

        except Exception as e:
            logger.error(f"Error calculating numeric trend: {e}")
            return {"error": str(e)}

    def generate_insights_summary(
        self, insights: Dict[str, Any], chart_type: str
    ) -> str:
        """Generate a human-readable summary of insights"""
        try:
            summary_parts = []

            # Column-specific insights
            for column, column_insights in insights.items():
                if column in ["correlations", "trends", "error"]:
                    continue

                if isinstance(column_insights, dict) and "error" not in column_insights:
                    col_summary = self._summarize_column_insights(
                        column, column_insights
                    )
                    if col_summary:
                        summary_parts.append(col_summary)

            # Correlation insights
            if (
                "correlations" in insights
                and "strong_correlations" in insights["correlations"]
            ):
                corr_summary = self._summarize_correlations(insights["correlations"])
                if corr_summary:
                    summary_parts.append(corr_summary)

            # Trend insights
            if "trends" in insights:
                trend_summary = self._summarize_trends(insights["trends"])
                if trend_summary:
                    summary_parts.append(trend_summary)

            if summary_parts:
                return " ".join(summary_parts)
            else:
                return f"Analysis of your {chart_type} chart shows the selected data relationships."

        except Exception as e:
            logger.error(f"Error generating insights summary: {e}")
            return "Unable to generate insights summary."

    def _summarize_column_insights(self, column: str, insights: Dict[str, Any]) -> str:
        """Summarize insights for a single column"""
        parts = []

        if "max" in insights and "min" in insights:
            parts.append(f"{column} ranges from {insights['min']} to {insights['max']}")

        if "mean" in insights and insights["mean"] != "N/A":
            parts.append(f"average of {insights['mean']}")

        if "distinct_count" in insights:
            parts.append(f"{insights['distinct_count']} unique values")

        if "outliers" in insights and insights["outliers"].get("has_outliers"):
            outlier_count = insights["outliers"]["count"]
            outlier_pct = insights["outliers"]["percentage"]
            parts.append(f"{outlier_count} outliers ({outlier_pct}%)")

        return ". ".join(parts) + "." if parts else ""

    def _summarize_correlations(self, correlations: Dict[str, Any]) -> str:
        """Summarize correlation findings"""
        strong_corrs = correlations.get("strong_correlations", [])

        if not strong_corrs:
            return ""

        if len(strong_corrs) == 1:
            corr = strong_corrs[0]
            return f"Strong {corr['direction']} correlation ({corr['correlation']}) between {corr['column1']} and {corr['column2']}."
        else:
            return f"Found {len(strong_corrs)} strong correlations between variables."

    def _summarize_trends(self, trends: Dict[str, Any]) -> str:
        """Summarize trend findings"""
        trend_summaries = []

        for trend_name, trend_data in trends.items():
            if isinstance(trend_data, dict) and "error" not in trend_data:
                if "direction" in trend_data:
                    direction = trend_data["direction"]
                    if direction != "stable" and trend_data.get("significant", False):
                        trend_summaries.append(
                            f"{trend_name.replace('_', ' ')} shows a significant {direction} trend"
                        )
                elif "relationship" in trend_data:
                    relationship = trend_data["relationship"]
                    if relationship != "no relationship" and trend_data.get(
                        "significant", False
                    ):
                        trend_summaries.append(
                            f"{trend_name.replace('_', ' ')} shows a significant {relationship} relationship"
                        )

        if trend_summaries:
            return ". ".join(trend_summaries) + "."

        return ""

    def calculate_insights(
        self, df: pd.DataFrame, columns: List[str], insight_types: List[InsightType]
    ) -> Dict[str, Any]:
        """Calculate requested insights for specified columns"""
        insights = {}

        try:
            for column in columns:
                if column not in df.columns:
                    logger.warning(f"Column '{column}' not found in data")
                    continue

                column_insights = {}
                series = df[column].dropna()  # Remove NaN values

                if len(series) == 0:
                    column_insights["error"] = "No valid data in column"
                    insights[column] = column_insights
                    continue

                # Basic statistics
                if InsightType.MAX in insight_types:
                    column_insights["max"] = self._safe_calculate(
                        lambda: self._format_value(series.max())
                    )

                if InsightType.MIN in insight_types:
                    column_insights["min"] = self._safe_calculate(
                        lambda: self._format_value(series.min())
                    )

                if InsightType.MEAN in insight_types:
                    column_insights["mean"] = self._safe_calculate(
                        lambda: (
                            self._format_value(series.mean())
                            if pd.api.types.is_numeric_dtype(series)
                            else "N/A"
                        )
                    )

                if InsightType.MEDIAN in insight_types:
                    column_insights["median"] = self._safe_calculate(
                        lambda: (
                            self._format_value(series.median())
                            if pd.api.types.is_numeric_dtype(series)
                            else "N/A"
                        )
                    )

                if InsightType.DISTINCT_COUNT in insight_types:
                    column_insights["distinct_count"] = self._safe_calculate(
                        lambda: int(series.nunique())
                    )

                if InsightType.TOTAL_COUNT in insight_types:
                    column_insights["total_count"] = self._safe_calculate(
                        lambda: int(len(series))
                    )

                # Advanced statistics for numeric data
                if pd.api.types.is_numeric_dtype(series):
                    if InsightType.DISTRIBUTION in insight_types:
                        column_insights["distribution"] = self._analyze_distribution(
                            series
                        )

                    if InsightType.OUTLIERS in insight_types:
                        column_insights["outliers"] = self._detect_outliers(series)

                insights[column] = column_insights

            # Multi-column insights
            if len(columns) > 1:
                if InsightType.CORRELATION in insight_types:
                    insights["correlations"] = self._calculate_correlations(df, columns)

                if InsightType.TREND in insight_types:
                    insights["trends"] = self._analyze_trends(df, columns)

            return insights

        except Exception as e:
            logger.error(f"Error calculating insights: {e}")
            return {"error": str(e)}

    def _safe_calculate(self, calculation_func):
        """Safely execute calculation with error handling"""
        try:
            return calculation_func()
        except Exception as e:
            logger.warning(f"Calculation failed: {e}")
            return "N/A"

    def _format_value(self, value) -> Any:
        """Format numerical values according to configuration"""
        if pd.isna(value):
            return "N/A"

        if isinstance(value, (int, np.integer)):
            return int(value)

        if isinstance(value, (float, np.floating)):
            if abs(value) >= 1e6:
                return f"{value:.2e}"  # Scientific notation for large numbers
            else:
                return round(
                    value, self.config.formatting.decimal_places
                )  # Use new config path

        return value

    def _analyze_distribution(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze the distribution of a numeric series"""
        try:
            distribution_info = {
                "skewness": self._format_value(stats.skew(series)),
                "kurtosis": self._format_value(stats.kurtosis(series)),
                "std_dev": self._format_value(series.std()),
                "variance": self._format_value(series.var()),
                "range": self._format_value(series.max() - series.min()),
            }

            # Quartiles
            quartiles = series.quantile([0.25, 0.5, 0.75])
            distribution_info.update(
                {
                    "q1": self._format_value(quartiles[0.25]),
                    "q2": self._format_value(quartiles[0.5]),
                    "q3": self._format_value(quartiles[0.75]),
                    "iqr": self._format_value(quartiles[0.75] - quartiles[0.25]),
                }
            )

            # Distribution type assessment
            distribution_info["assessment"] = self._assess_distribution_type(series)

            return distribution_info

        except Exception as e:
            logger.error(f"Error analyzing distribution: {e}")
            return {"error": str(e)}


# Convenience functions (these also need to be updated to use the new config_manager)
def calculate_basic_insights(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    """Calculate basic insights for columns"""
    calculator = InsightsCalculator()
    basic_insights = [
        InsightType.MAX,
        InsightType.MIN,
        InsightType.MEAN,
        InsightType.DISTINCT_COUNT,
        InsightType.TOTAL_COUNT,
    ]
    return calculator.calculate_insights(df, columns, basic_insights)


def calculate_advanced_insights(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    """Calculate advanced insights including correlations and trends"""
    calculator = InsightsCalculator()
    all_insights = list(InsightType)
    return calculator.calculate_insights(df, columns, all_insights)
