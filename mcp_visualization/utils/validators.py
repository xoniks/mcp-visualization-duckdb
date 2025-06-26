"""
Input validation utilities for security and data integrity
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

from config.settings import SecurityConfig

logger = logging.getLogger(__name__)


def validate_sql_query(query: str, security_config: SecurityConfig) -> bool:
    """
    Validate SQL query for security and policy compliance

    Args:
        query: SQL query string to validate
        security_config: Security configuration with allowed/blocked keywords

    Returns:
        True if query is valid and safe, False otherwise
    """
    try:
        # Basic length check
        if len(query) > security_config.max_query_length:
            logger.warning(
                f"Query too long: {len(query)} > {security_config.max_query_length}"
            )
            return False

        # Parse the SQL query
        parsed = sqlparse.parse(query)
        if not parsed:
            logger.warning("Could not parse SQL query")
            return False

        statement = parsed[0]

        # Extract all keywords from the query
        keywords = []
        for token in statement.flatten():
            if token.ttype is Keyword or token.ttype is DML:
                keywords.append(token.value.upper())

        # Check for blocked keywords
        for keyword in keywords:
            if keyword in [k.upper() for k in security_config.blocked_sql_keywords]:
                logger.warning(f"Blocked SQL keyword found: {keyword}")
                return False

        # Ensure query starts with allowed operation
        first_keyword = None
        for token in statement.tokens:
            if token.ttype is Keyword or token.ttype is DML:
                first_keyword = token.value.upper()
                break

        if first_keyword and first_keyword not in [
            k.upper() for k in security_config.allowed_sql_keywords
        ]:
            logger.warning(f"Query starts with disallowed keyword: {first_keyword}")
            return False

        # Additional security checks
        query_upper = query.upper()

        # Check for SQL injection patterns
        injection_patterns = [
            r";\s*(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|TRUNCATE)",
            r"UNION\s+SELECT",
            r"--\s*[^\r\n]*",  # SQL comments
            r"/\*.*?\*/",  # Block comments
            r"EXEC\s*\(",
            r"SP_\w+",
            r"XP_\w+",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Potential SQL injection pattern found: {pattern}")
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating SQL query: {e}")
        return False


def validate_table_name(table_name: str) -> bool:
    """
    Validate table name for SQL safety

    Args:
        table_name: Name of the table

    Returns:
        True if valid, False otherwise
    """
    # Check format: alphanumeric, underscores, starts with letter or underscore
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    if not re.match(pattern, table_name):
        logger.warning(f"Invalid table name format: {table_name}")
        return False

    # Check length
    if len(table_name) > 64:  # Standard SQL identifier limit
        logger.warning(f"Table name too long: {table_name}")
        return False

    # Check for reserved words (basic check)
    reserved_words = {
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "TABLE",
        "INDEX",
        "VIEW",
        "GRANT",
        "REVOKE",
        "COMMIT",
        "ROLLBACK",
        "UNION",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "FULL",
        "OUTER",
        "ON",
        "AS",
        "GROUP",
        "ORDER",
        "BY",
        "HAVING",
        "DISTINCT",
        "ALL",
        "AND",
        "OR",
        "NOT",
        "NULL",
        "TRUE",
        "FALSE",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
    }

    if table_name.upper() in reserved_words:
        logger.warning(f"Table name is reserved word: {table_name}")
        return False

    return True


def validate_column_name(column_name: str) -> bool:
    """
    Validate column name for SQL safety

    Args:
        column_name: Name of the column

    Returns:
        True if valid, False otherwise
    """
    # Same rules as table names
    return validate_table_name(column_name)


def validate_file_path(file_path: str, allowed_paths: List[str]) -> Tuple[bool, str]:
    """
    Validate file path for security

    Args:
        file_path: Path to validate
        allowed_paths: List of allowed base paths

    Returns:
        Tuple of (is_valid, normalized_path)
    """
    try:
        # Normalize the path
        normalized_path = Path(file_path).resolve()

        # Check if path exists
        if not normalized_path.exists():
            return False, f"File not found: {file_path}"

        # Check if it's a file (not directory)
        if not normalized_path.is_file():
            return False, f"Path is not a file: {file_path}"

        # Check against allowed paths
        for allowed_path in allowed_paths:
            allowed_resolved = Path(allowed_path).resolve()
            try:
                # Check if the file is within an allowed directory
                normalized_path.relative_to(allowed_resolved)
                return True, str(normalized_path)
            except ValueError:
                continue

        return False, f"File path not in allowed directories: {file_path}"

    except Exception as e:
        return False, f"Error validating file path: {e}"


def validate_chart_configuration(
    chart_type: str, column_mappings: Dict[str, str], available_columns: List[str]
) -> Dict[str, Any]:
    """
    Validate chart configuration

    Args:
        chart_type: Type of chart being created
        column_mappings: Mapping of chart roles to column names
        available_columns: List of available column names

    Returns:
        Validation result with errors and warnings
    """
    result = {"valid": True, "errors": [], "warnings": []}

    # Check that all mapped columns exist
    for role, column in column_mappings.items():
        if column and column not in available_columns:
            result["errors"].append(f"Column '{column}' not found in available columns")
            result["valid"] = False

    # Chart-specific validation
    if chart_type == "bar":
        if not column_mappings.get("x_axis") or not column_mappings.get("y_axis"):
            result["errors"].append("Bar chart requires both x_axis and y_axis columns")
            result["valid"] = False

    elif chart_type == "line":
        if not column_mappings.get("x_axis") or not column_mappings.get("y_axis"):
            result["errors"].append(
                "Line chart requires both x_axis and y_axis columns"
            )
            result["valid"] = False

    elif chart_type == "scatter":
        if not column_mappings.get("x_axis") or not column_mappings.get("y_axis"):
            result["errors"].append(
                "Scatter plot requires both x_axis and y_axis columns"
            )
            result["valid"] = False

    elif chart_type == "pie":
        if not column_mappings.get("category") or not column_mappings.get("values"):
            result["errors"].append(
                "Pie chart requires both category and values columns"
            )
            result["valid"] = False

    elif chart_type == "histogram":
        if not column_mappings.get("column"):
            result["errors"].append("Histogram requires a column to analyze")
            result["valid"] = False

    return result


def validate_insight_types(insight_types: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate and filter insight types

    Args:
        insight_types: List of requested insight type strings

    Returns:
        Tuple of (valid_insights, invalid_insights)
    """
    valid_insight_types = {
        "max",
        "min",
        "mean",
        "median",
        "distinct_count",
        "total_count",
        "correlation",
        "trend",
        "outliers",
        "distribution",
    }

    valid_insights = []
    invalid_insights = []

    for insight in insight_types:
        insight_lower = insight.lower().strip()
        if insight_lower in valid_insight_types:
            valid_insights.append(insight_lower)
        else:
            invalid_insights.append(insight)

    return valid_insights, invalid_insights


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """
    Sanitize user input for display and processing

    Args:
        user_input: Raw user input
        max_length: Maximum allowed length

    Returns:
        Sanitized input string
    """
    if not isinstance(user_input, str):
        return str(user_input)

    # Truncate if too long
    if len(user_input) > max_length:
        user_input = user_input[:max_length] + "..."

    # Remove control characters except common whitespace
    sanitized = "".join(
        char for char in user_input if ord(char) >= 32 or char in "\t\n\r"
    )

    # Remove potential script injection
    sanitized = re.sub(
        r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
    )

    return sanitized.strip()


def validate_data_types(data_sample: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate and categorize data types from a sample

    Args:
        data_sample: Sample data dictionary

    Returns:
        Dictionary mapping column names to data type categories
    """
    type_mapping = {}

    for column, value in data_sample.items():
        if value is None:
            type_mapping[column] = "unknown"
        elif isinstance(value, bool):
            type_mapping[column] = "boolean"
        elif isinstance(value, int):
            type_mapping[column] = "integer"
        elif isinstance(value, float):
            type_mapping[column] = "float"
        elif isinstance(value, str):
            # Try to detect special string types
            if re.match(r"^\d{4}-\d{2}-\d{2}", value):
                type_mapping[column] = "date"
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
                type_mapping[column] = "datetime"
            elif re.match(r"^\d+\.\d+$", value):
                type_mapping[column] = "numeric_string"
            else:
                type_mapping[column] = "text"
        else:
            type_mapping[column] = "other"

    return type_mapping


class InputValidator:
    """Class for validating various types of input"""

    def __init__(self, security_config: Optional[SecurityConfig] = None):
        self.security_config = security_config

    def validate_mcp_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive validation for MCP tool calls

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool

        Returns:
            Validation result with sanitized arguments
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_arguments": {},
        }

        try:
            # Validate tool name
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", tool_name):
                result["errors"].append(f"Invalid tool name format: {tool_name}")
                result["valid"] = False
                return result

            # Sanitize and validate each argument
            for key, value in arguments.items():
                # Validate argument name
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    result["warnings"].append(f"Unusual argument name: {key}")

                # Sanitize based on argument type and name
                if isinstance(value, str):
                    if key in ["sql_query", "request"]:
                        # Special handling for SQL and user requests
                        sanitized_value = sanitize_user_input(value, max_length=10000)
                    elif key in ["table_name", "column_name"]:
                        # Validate identifier names
                        sanitized_value = value.strip()
                        if not validate_table_name(sanitized_value):
                            result["errors"].append(f"Invalid {key}: {sanitized_value}")
                            result["valid"] = False
                            continue
                    elif key == "file_path":
                        # File path validation
                        sanitized_value = value.strip()
                        if self.security_config:
                            is_valid, message = validate_file_path(
                                sanitized_value, self.security_config.allowed_paths
                            )
                            if not is_valid:
                                result["errors"].append(message)
                                result["valid"] = False
                                continue
                    else:
                        # General string sanitization
                        sanitized_value = sanitize_user_input(value)

                elif isinstance(value, (int, float)):
                    # Validate numeric ranges
                    if key == "limit" and value <= 0:
                        result["warnings"].append(
                            "Limit should be positive, using default"
                        )
                        sanitized_value = 100
                    else:
                        sanitized_value = value

                elif isinstance(value, dict):
                    # Recursively validate dictionary arguments
                    sanitized_value = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            sanitized_value[sub_key] = sanitize_user_input(sub_value)
                        else:
                            sanitized_value[sub_key] = sub_value

                elif isinstance(value, list):
                    # Validate list arguments
                    sanitized_value = []
                    for item in value:
                        if isinstance(item, str):
                            sanitized_value.append(sanitize_user_input(item))
                        else:
                            sanitized_value.append(item)

                else:
                    sanitized_value = value

                result["sanitized_arguments"][key] = sanitized_value

            # Tool-specific validation
            if tool_name == "query_data":
                sql_query = result["sanitized_arguments"].get("sql_query", "")
                if self.security_config and not validate_sql_query(
                    sql_query, self.security_config
                ):
                    result["errors"].append("SQL query failed security validation")
                    result["valid"] = False

            elif tool_name == "configure_chart":
                chart_config_validation = self._validate_chart_configuration_args(
                    result["sanitized_arguments"]
                )
                if not chart_config_validation["valid"]:
                    result["errors"].extend(chart_config_validation["errors"])
                    result["valid"] = False

        except Exception as e:
            logger.error(f"Error validating tool call: {e}")
            result["errors"].append(f"Validation error: {e}")
            result["valid"] = False

        return result

    def _validate_chart_configuration_args(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate chart configuration arguments"""
        result = {"valid": True, "errors": []}

        # Check for required request_id
        if not arguments.get("request_id"):
            result["errors"].append("Missing required request_id")
            result["valid"] = False

        # Validate insights if provided
        if arguments.get("insights"):
            insights_str = arguments["insights"]
            if isinstance(insights_str, str):
                insight_list = [i.strip() for i in insights_str.split(",")]
                valid_insights, invalid_insights = validate_insight_types(insight_list)

                if invalid_insights:
                    result["errors"].append(
                        f"Invalid insight types: {', '.join(invalid_insights)}"
                    )
                    result["valid"] = False

        return result


# Global validator instance
def get_validator(security_config: Optional[SecurityConfig] = None) -> InputValidator:
    """Get a configured input validator"""
    return InputValidator(security_config)


# Convenience functions
def is_safe_sql(query: str, security_config: SecurityConfig) -> bool:
    """Quick SQL safety check"""
    return validate_sql_query(query, security_config)


def is_valid_identifier(name: str) -> bool:
    """Quick identifier validation"""
    return validate_table_name(name)


def clean_user_text(text: str) -> str:
    """Quick text sanitization"""
    return sanitize_user_input(text)
