# Database queries
"""
Query builder and common SQL queries for data visualization
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryFilter:
    """Represents a filter condition"""

    column: str
    operator: str  # =, !=, >, <, >=, <=, IN, LIKE
    value: Any
    logical_operator: str = "AND"  # AND, OR


@dataclass
class QueryConfig:
    """Configuration for query building"""

    table_name: str
    columns: Optional[List[str]] = None
    filters: Optional[List[QueryFilter]] = None
    group_by: Optional[List[str]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    aggregations: Optional[Dict[str, str]] = None  # column -> function


class QueryBuilder:
    """Builds SQL queries for visualization purposes"""

    def __init__(self):
        self.safe_operators = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "IN",
            "LIKE",
            "NOT IN",
            "NOT LIKE",
        }
        self.safe_functions = {
            "COUNT",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "MEDIAN",
            "STDDEV",
            "VARIANCE",
            "DISTINCT",
            "ROUND",
            "UPPER",
            "LOWER",
        }

    def build_visualization_query(self, config: QueryConfig) -> str:
        """Build a query optimized for visualization"""
        try:
            # Start with SELECT
            select_parts = []

            if config.columns:
                for col in config.columns:
                    select_parts.append(self._sanitize_column_name(col))
            else:
                select_parts.append("*")

            # Add aggregations
            if config.aggregations:
                for column, function in config.aggregations.items():
                    if function.upper() in self.safe_functions:
                        safe_col = self._sanitize_column_name(column)
                        select_parts.append(
                            f"{function.upper()}({safe_col}) as {function.lower()}_{column}"
                        )

            select_clause = "SELECT " + ", ".join(select_parts)

            # FROM clause
            from_clause = f"FROM {self._sanitize_table_name(config.table_name)}"

            # WHERE clause
            where_clause = ""
            if config.filters:
                conditions = []
                for filter_obj in config.filters:
                    condition = self._build_filter_condition(filter_obj)
                    if condition:
                        conditions.append(condition)

                if conditions:
                    where_clause = "WHERE " + f" {conditions[0]} ".join(
                        [
                            f" {f.logical_operator} {cond}"
                            for f, cond in zip(config.filters[1:], conditions[1:])
                        ]
                    )
                    if len(conditions) == 1:
                        where_clause = f"WHERE {conditions[0]}"

            # GROUP BY clause
            group_by_clause = ""
            if config.group_by:
                safe_columns = [
                    self._sanitize_column_name(col) for col in config.group_by
                ]
                group_by_clause = f"GROUP BY {', '.join(safe_columns)}"

            # ORDER BY clause
            order_by_clause = ""
            if config.order_by:
                safe_columns = [
                    self._sanitize_column_name(col) for col in config.order_by
                ]
                order_by_clause = f"ORDER BY {', '.join(safe_columns)}"

            # LIMIT clause
            limit_clause = ""
            if config.limit and isinstance(config.limit, int) and config.limit > 0:
                limit_clause = f"LIMIT {config.limit}"

            # Combine all parts
            query_parts = [select_clause, from_clause]
            if where_clause:
                query_parts.append(where_clause)
            if group_by_clause:
                query_parts.append(group_by_clause)
            if order_by_clause:
                query_parts.append(order_by_clause)
            if limit_clause:
                query_parts.append(limit_clause)

            query = " ".join(query_parts)
            logger.debug(f"Built query: {query}")
            return query

        except Exception as e:
            logger.error(f"Error building query: {e}")
            raise

    def build_bar_chart_query(
        self,
        table_name: str,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for bar chart data"""
        columns = [x_column, f"SUM({y_column}) as total_{y_column}"]
        group_by = [x_column]

        if color_column:
            columns.insert(1, color_column)
            group_by.append(color_column)

        config = QueryConfig(
            table_name=table_name,
            columns=columns,
            filters=filters,
            group_by=group_by,
            order_by=[f"total_{y_column} DESC"],
        )

        return self.build_visualization_query(config)

    def build_line_chart_query(
        self,
        table_name: str,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for line chart data"""
        columns = [x_column, y_column]
        group_by = [x_column]

        if color_column:
            columns.append(color_column)
            group_by.append(color_column)

        config = QueryConfig(
            table_name=table_name,
            columns=columns,
            filters=filters,
            group_by=group_by,
            order_by=[x_column],
        )

        return self.build_visualization_query(config)

    def build_scatter_plot_query(
        self,
        table_name: str,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        size_column: Optional[str] = None,
        filters: Optional[List[QueryFilter]] = None,
        limit: int = 10000,
    ) -> str:
        """Build query for scatter plot data"""
        columns = [x_column, y_column]

        if color_column:
            columns.append(color_column)
        if size_column:
            columns.append(size_column)

        config = QueryConfig(
            table_name=table_name,
            columns=columns,
            filters=filters,
            limit=limit,  # Limit for performance
        )

        return self.build_visualization_query(config)

    def build_pie_chart_query(
        self,
        table_name: str,
        category_column: str,
        value_column: str,
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for pie chart data"""
        config = QueryConfig(
            table_name=table_name,
            columns=[category_column],
            aggregations={value_column: "SUM"},
            filters=filters,
            group_by=[category_column],
            order_by=[f"sum_{value_column} DESC"],
        )

        return self.build_visualization_query(config)

    def build_histogram_query(
        self,
        table_name: str,
        column: str,
        bins: int = 30,
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for histogram data"""
        # Use DuckDB's histogram function or create bins manually
        query = f"""
        WITH stats AS (
            SELECT 
                MIN({self._sanitize_column_name(column)}) as min_val,
                MAX({self._sanitize_column_name(column)}) as max_val
            FROM {self._sanitize_table_name(table_name)}
            WHERE {self._sanitize_column_name(column)} IS NOT NULL
        ),
        binned_data AS (
            SELECT 
                FLOOR(({self._sanitize_column_name(column)} - stats.min_val) / 
                      ((stats.max_val - stats.min_val) / {bins})) as bin_number,
                stats.min_val + (FLOOR(({self._sanitize_column_name(column)} - stats.min_val) / 
                                ((stats.max_val - stats.min_val) / {bins})) * 
                               ((stats.max_val - stats.min_val) / {bins})) as bin_start,
                COUNT(*) as frequency
            FROM {self._sanitize_table_name(table_name)}, stats
            WHERE {self._sanitize_column_name(column)} IS NOT NULL
            GROUP BY bin_number, bin_start, stats.min_val, stats.max_val
            ORDER BY bin_number
        )
        SELECT bin_start, bin_start + ((SELECT MAX(bin_start) - MIN(bin_start) FROM binned_data) / {bins}) as bin_end, frequency
        FROM binned_data
        """

        return query

    def build_correlation_query(
        self,
        table_name: str,
        columns: List[str],
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for correlation analysis"""
        # Build correlation matrix query
        correlations = []
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i <= j:  # Only upper triangle + diagonal
                    safe_col1 = self._sanitize_column_name(col1)
                    safe_col2 = self._sanitize_column_name(col2)
                    correlations.append(
                        f"CORR({safe_col1}, {safe_col2}) as corr_{col1}_{col2}"
                    )

        query = f"SELECT {', '.join(correlations)} FROM {self._sanitize_table_name(table_name)}"

        # Add filters if provided
        if filters:
            conditions = []
            for filter_obj in filters:
                condition = self._build_filter_condition(filter_obj)
                if condition:
                    conditions.append(condition)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        return query

    def build_summary_stats_query(
        self,
        table_name: str,
        columns: List[str],
        filters: Optional[List[QueryFilter]] = None,
    ) -> str:
        """Build query for summary statistics"""
        stats_columns = []

        for col in columns:
            safe_col = self._sanitize_column_name(col)
            stats_columns.extend(
                [
                    f"'{col}' as column_name",
                    f"COUNT({safe_col}) as count",
                    f"COUNT(DISTINCT {safe_col}) as distinct_count",
                    f"MIN({safe_col}) as min_value",
                    f"MAX({safe_col}) as max_value",
                    f"AVG({safe_col}) as mean_value",
                    f"MEDIAN({safe_col}) as median_value",
                    f"STDDEV({safe_col}) as std_value",
                ]
            )

        # Create UNION query for each column
        union_queries = []
        for col in columns:
            safe_col = self._sanitize_column_name(col)
            select_parts = [
                f"'{col}' as column_name",
                f"COUNT({safe_col}) as count",
                f"COUNT(DISTINCT {safe_col}) as distinct_count",
                f"MIN({safe_col}) as min_value",
                f"MAX({safe_col}) as max_value",
                f"AVG({safe_col}) as mean_value",
                f"MEDIAN({safe_col}) as median_value",
                f"STDDEV({safe_col}) as std_value",
            ]

            query_part = f"SELECT {', '.join(select_parts)} FROM {self._sanitize_table_name(table_name)}"

            # Add filters
            if filters:
                conditions = []
                for filter_obj in filters:
                    condition = self._build_filter_condition(filter_obj)
                    if condition:
                        conditions.append(condition)

                if conditions:
                    query_part += " WHERE " + " AND ".join(conditions)

            union_queries.append(query_part)

        return " UNION ALL ".join(union_queries)

    def _build_filter_condition(self, filter_obj: QueryFilter) -> str:
        """Build a single filter condition"""
        try:
            if filter_obj.operator not in self.safe_operators:
                logger.warning(f"Unsafe operator: {filter_obj.operator}")
                return ""

            safe_column = self._sanitize_column_name(filter_obj.column)

            if filter_obj.operator in ("IN", "NOT IN"):
                if isinstance(filter_obj.value, (list, tuple)):
                    values = ", ".join([f"'{v}'" for v in filter_obj.value])
                    return f"{safe_column} {filter_obj.operator} ({values})"
                else:
                    return f"{safe_column} {filter_obj.operator} ('{filter_obj.value}')"

            elif filter_obj.operator in ("LIKE", "NOT LIKE"):
                return f"{safe_column} {filter_obj.operator} '{filter_obj.value}'"

            else:
                # Handle different value types
                if isinstance(filter_obj.value, str):
                    return f"{safe_column} {filter_obj.operator} '{filter_obj.value}'"
                else:
                    return f"{safe_column} {filter_obj.operator} {filter_obj.value}"

        except Exception as e:
            logger.error(f"Error building filter condition: {e}")
            return ""

    def _sanitize_column_name(self, column_name: str) -> str:
        """Sanitize column name to prevent SQL injection"""
        # Remove or escape potentially dangerous characters
        # DuckDB supports quoted identifiers
        sanitized = column_name.replace('"', '""')  # Escape quotes
        return f'"{sanitized}"'

    def _sanitize_table_name(self, table_name: str) -> str:
        """Sanitize table name to prevent SQL injection"""
        # More restrictive for table names
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        return table_name

    def get_sample_data_query(self, table_name: str, limit: int = 1000) -> str:
        """Get sample data for preview"""
        return f"SELECT * FROM {self._sanitize_table_name(table_name)} LIMIT {limit}"

    def get_data_types_query(self, table_name: str) -> str:
        """Get data types for all columns"""
        return f"DESCRIBE {self._sanitize_table_name(table_name)}"
