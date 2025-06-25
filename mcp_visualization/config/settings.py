# code/config/settings.py

# Configuration settings
"""
Configuration management for MCP Data Visualization Server
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Literal
import yaml  # Still needed if you explicitly load YAML in other parts, but not for the main settings load anymore
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

PROJECT_ROOT = Path(__file__).parent.parent.parent
# print(f"Project root set to: {PROJECT_ROOT}")


class ConnectionConfig(BaseSettings):
    """Database connection configuration"""

    model_config = SettingsConfigDict(
        env_prefix="",  # No prefix to avoid conflicts
        case_sensitive=True,  # Case sensitive env vars
        extra="ignore",
    )

    path: Path = Field(
        default=PROJECT_ROOT / "data" / "mcp.duckdb",
        description="Path to the DuckDB database file or ':memory:' for in-memory.",
        env="DUCKDB_DATABASE_PATH",  # Use specific env var
    )
    timeout: int = 30
    read_only: bool = False

    def __post_init__(self):
        """Ensure database directory exists and validate path"""
        # Convert string path to Path object if needed
        if isinstance(self.path, str):
            self.path = Path(self.path)

        # Check if we accidentally got the system PATH
        path_str = str(self.path)
        if ";" in path_str and path_str.count(";") > 5:
            # This is definitely the system PATH, override it
            self.path = PROJECT_ROOT / "data" / "mcp.duckdb"
            print(
                f"⚠️  Detected system PATH in database config, overriding to: {self.path}"
            )

        # Ensure it's an absolute path
        if not self.path.is_absolute():
            self.path = PROJECT_ROOT / self.path

        # Create directory if it doesn't exist
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)

        print(f"✅ Database path: {self.path}")
        print(f"✅ Database directory exists: {self.path.parent.exists()}")


class DatabaseSettings(BaseSettings):
    """Specific DuckDB settings"""

    memory_limit: str = "1GB"
    threads: int = 4
    enable_extensions: bool = True


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    type: str = "duckdb"
    connection: ConnectionConfig = ConnectionConfig()
    settings: DatabaseSettings = DatabaseSettings()


class OllamaConfig(BaseSettings):
    """Ollama LLM configuration"""

    base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    model: str = Field(default="qwen2:0.5b", env="OLLAMA_MODEL")
    timeout: int = Field(default=30, env="OLLAMA_TIMEOUT")
    max_tokens: int = 2048
    temperature: float = 0.1
    is_enabled: bool = Field(
        default=True, description="Enable or disable Ollama LLM integration"
    )


class LLMPromptsConfig(BaseSettings):
    """LLM Prompt templates configuration"""

    chart_type_detection_template: str = Field(
        default="""Analyze this data visualization request and determine the most appropriate chart type.

REQUEST: "{request}"
TABLE: {table_name}
AVAILABLE COLUMNS: {columns}

Consider the following chart types and their use cases:
- bar: Compare categorical data, show totals/counts across groups
- line: Show trends over time or continuous data, connect data points
- scatter: Show relationships between two numeric variables, find correlations
- pie: Show proportions or percentages of a whole, categorical breakdown
- histogram: Show distribution of a single numeric variable, frequency analysis
- box: Show distribution with quartiles and outliers
- heatmap: Show correlation matrix or 2D data relationships
- area: Show cumulative values or filled trend analysis

Respond with ONLY a valid JSON object in this exact format:
{{"chart_type": "bar|line|scatter|pie|histogram|box|heatmap|area", "confidence": 0.8, "reasoning": "explanation of why this chart type fits the request"}}
""",
        description="Prompt for detecting chart type from user request.",
        alias="chart_type_detection",
    )
    column_suggestion_template: str = Field(
        default="""For a {chart_type} chart with the following columns, suggest the most appropriate column mappings.

COLUMNS: {columns}
REQUEST CONTEXT: "{request}"

Chart type requirements:
- bar: needs x_axis (categorical), y_axis (numeric), optional color (categorical)
- line: needs x_axis (continuous/temporal), y_axis (numeric), optional color (grouping)
- scatter: needs x_axis (numeric), y_axis (numeric), optional color/size (any type)
- pie: needs category (categorical), values (numeric)
- histogram: needs column (numeric)
- box: needs column (numeric), optional groupby (categorical)
- heatmap: needs multiple numeric columns
- area: needs x_axis (continuous), y_axis (numeric), optional color (grouping)

Respond with ONLY a valid JSON object:
{{"suggestions": {{"x_axis": "column_name", "y_axis": "column_name", "explanation": "why these columns work well together"}}}}
""",
        description="Prompt for suggesting column mappings based on chart type.",
        alias="column_suggestion",
    )
    insights_description_template: str = Field(
        default="""Generate a clear, concise description of the insights from this data visualization.

CHART TYPE: {chart_type}
DATA SUMMARY: {data_summary}
CALCULATED INSIGHTS: {insights}

Write 2-3 sentences describing:
1. What the chart shows
2. Key findings from the data
3. Notable patterns or trends

Be specific about numbers and use accessible language.
""",
        description="Prompt for generating insights description.",
        alias="insights_description",
    )
    chart_explanation_template: str = Field(
        default="""Explain what this chart visualization shows and how to interpret it.

CHART TYPE: {chart_type}
COLUMN MAPPINGS: {column_mappings}
SAMPLE DATA: {data_preview}

Provide a brief explanation that:
1. Describes what is being compared or analyzed
2. Explains how to read the chart
3. Points out any notable patterns in the sample data

Keep it under 100 words and use clear, non-technical language.
""",
        description="Prompt for explaining charts.",
        alias="chart_explanation",
    )
    data_quality_check_template: str = Field(
        default="""Analyze this dataset for potential data quality issues that might affect visualization.

COLUMNS: {columns}
SAMPLE DATA: {sample_data}
BASIC STATS: {basic_stats}

Check for:
- Missing values
- Outliers
- Inconsistent formatting
- Potential data type issues
- Visualization challenges

Provide brief recommendations for data preparation if needed.
""",
        description="Prompt for data quality checks.",
        alias="data_quality_check",
    )
    followup_questions_template: str = Field(
        default="""Based on this {chart_type} chart and the insights found, suggest 3 relevant follow-up questions that would lead to deeper analysis.

CHART CONTEXT: {chart_context}
INSIGHTS FOUND: {insights}
AVAILABLE DATA: {available_columns}

Generate questions that:
1. Explore different dimensions of the data
2. Look for additional patterns or relationships
3. Could lead to actionable insights

Format as a simple numbered list.
""",
        description="Prompt for generating follow-up questions.",
        alias="followup_questions",
    )


class LLMConfig(BaseSettings):
    """LLM configuration"""

    provider: str = "ollama"
    ollama: OllamaConfig = OllamaConfig()
    prompts: LLMPromptsConfig = LLMPromptsConfig()


class FigureSizeConfig(BaseSettings):
    """Figure size configuration for visualizations"""

    width: int = Field(default=800, env="VIZ_WIDTH")
    height: int = Field(default=600, env="VIZ_HEIGHT")


class ChartDefaultsBar(BaseSettings):
    orientation: Literal["v", "h"] = "v"
    text_auto: bool = True
    show_legend: bool = True


class ChartDefaultsLine(BaseSettings):
    mode: str = "lines+markers"
    line_width: int = 2
    marker_size: int = 6


class ChartDefaultsScatter(BaseSettings):
    mode: str = "markers"
    marker_size: int = 8
    opacity: float = 0.7


class ChartDefaultsPie(BaseSettings):
    hole: float = 0.0
    text_info: str = "label+percent"


class ChartDefaultsHistogram(BaseSettings):
    bins: int = 30
    opacity: float = 0.7
    show_distribution: bool = True


class ChartDefaultsConfig(BaseSettings):
    """Default settings for various chart types"""

    bar: ChartDefaultsBar = ChartDefaultsBar()
    line: ChartDefaultsLine = ChartDefaultsLine()
    scatter: ChartDefaultsScatter = ChartDefaultsScatter()
    pie: ChartDefaultsPie = ChartDefaultsPie()
    histogram: ChartDefaultsHistogram = ChartDefaultsHistogram()


class VisualizationConfig(BaseSettings):
    """Visualization configuration"""

    default_theme: str = Field(default="plotly_white", env="VIZ_THEME")
    output_format: str = "html"
    figure_size: FigureSizeConfig = FigureSizeConfig()
    color_schemes: Dict[str, Any] = {
        "categorical": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
        "sequential": "Blues",
        "diverging": "RdBu",
    }
    chart_defaults: ChartDefaultsConfig = ChartDefaultsConfig()
    max_rows_for_charts: int = Field(
        default=100000,
        description="Maximum rows to load into memory for chart generation to avoid OOM.",
    )


class TrendDetectionConfig(BaseSettings):
    """Trend detection settings"""

    min_points: int = 5
    significance_level: float = 0.05


class FormattingConfig(BaseSettings):
    """Formatting settings for insights"""

    decimal_places: int = 2
    percentage_format: str = ".1%"
    large_number_format: str = ".2e"


class InsightsConfig(BaseSettings):
    """Insights configuration"""

    enabled_types: List[str] = [
        "max",
        "min",
        "mean",
        "median",
        "distinct_count",
        "total_count",
        "correlation",
        "trend",
    ]
    correlation_threshold: float = 0.5
    trend_detection: TrendDetectionConfig = TrendDetectionConfig()
    formatting: FormattingConfig = FormattingConfig()


class PreprocessingConfig(BaseSettings):
    """Data preprocessing configuration"""

    auto_detect_types: bool = True
    handle_missing_values: bool = True
    date_formats: List[str] = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]


class SamplingConfig(BaseSettings):
    """Data sampling configuration"""

    large_dataset_threshold: int = 100000
    sample_size: int = 10000
    sampling_method: Literal["random", "systematic", "stratified"] = "random"


class DataConfig(BaseSettings):
    """Data Processing Configuration"""

    max_rows_preview: int = 1000
    max_file_size_mb: int = 100
    supported_formats: List[str] = ["csv", "parquet", "json", "xlsx"]
    preprocessing: PreprocessingConfig = PreprocessingConfig()
    sampling: SamplingConfig = SamplingConfig()


class FileAccessConfig(BaseSettings):
    """File access security configuration"""

    allowed_paths: List[Path] = Field(
        default=[Path("./data/"), Path("./samples/")], env="ALLOWED_PATHS"
    )
    blocked_extensions: List[str] = [".exe", ".bat", ".sh", ".py"]


class SecurityConfig(BaseSettings):
    """Security configuration"""

    max_query_length: int = 10000
    allowed_sql_keywords: List[str] = [
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP BY",
        "ORDER BY",
        "LIMIT",
        "JOIN",
        "INNER JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "AS",
        "ON",
        "AND",
        "OR",
        "IN",
        "NOT IN",
        "LIKE",
        "ILIKE",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
    ]
    blocked_sql_keywords: List[str] = [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "ATTACH",
        "DETACH",
        "COPY",
        "PRAGMA",
        "SET",
        "SYSTEM",
        "EXEC",
        "CALL",
    ]
    file_access: FileAccessConfig = FileAccessConfig()


class SampleDatasetConfig(BaseSettings):
    """Configuration for a single sample dataset"""

    name: str
    file: Path  # This is already Path, which is good


class SampleDataConfig(BaseSettings):
    """Sample data generation configuration"""

    generate_on_startup: bool = Field(default=True, env="GENERATE_SAMPLE_DATA")
    datasets: List[SampleDatasetConfig] = [
        SampleDatasetConfig(name="sales", file=Path("./data/samples/sales_data.csv")),
        SampleDatasetConfig(
            name="customers", file=Path("./data/samples/customers.csv")
        ),
        SampleDatasetConfig(name="products", file=Path("./data/samples/products.csv")),
    ]


class TestingConfig(BaseSettings):
    """Testing specific configuration"""

    use_test_database: bool = True
    test_data_size: int = 100


class DevelopmentConfig(BaseSettings):
    """Development configuration"""

    debug_mode: bool = Field(default=True, env="DEBUG_MODE")
    auto_reload: bool = Field(default=True, env="AUTO_RELOAD")
    sample_data: SampleDataConfig = SampleDataConfig()
    testing: TestingConfig = TestingConfig()


class ServerConfig(BaseSettings):
    """Server configuration"""

    name: str = "data-viz-server"
    version: str = "1.0.0"
    description: str = "Natural Language Data Visualization MCP Server"
    transport: Literal["stdio", "websocket", "http"] = "stdio"
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


# --- Main Settings Class ---
class Settings(BaseSettings):
    """Main settings class"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Added yaml_file and yaml_file_encoding to enable automatic loading
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
    )
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    visualization: VisualizationConfig = VisualizationConfig()
    insights: InsightsConfig = InsightsConfig()
    security: SecurityConfig = SecurityConfig()
    data: DataConfig = DataConfig()
    development: DevelopmentConfig = DevelopmentConfig()


# --- Config Manager to handle YAML and Pydantic ---
_config_manager_logger = logging.getLogger(__name__ + ".ConfigManager")


class ConfigManager:
    """
    Configuration manager that loads settings via Pydantic's BaseSettings.
    It relies on BaseSettings's `model_config` to handle environment variables and YAML files.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "config.yaml"
        self._settings: Optional[Settings] = None

    def get_settings(self) -> Settings:
        """
        Retrieves the application settings.
        Settings are loaded (or reloaded) using Pydantic's built-in mechanisms
        which consult environment variables and the configured YAML file.
        """
        if self._settings is None:
            try:
                # Force the database path from environment variable if set
                db_path = os.getenv("DUCKDB_DATABASE_PATH")
                if db_path:
                    print(f"Using database path: {db_path}")

                self._settings = Settings()

                # Additional safety check for database path
                actual_path = self._settings.database.connection.path
                if ";" in str(actual_path) and str(actual_path).count(";") > 5:
                    # Override with environment variable or default
                    if db_path:
                        self._settings.database.connection.path = Path(db_path)
                    else:
                        self._settings.database.connection.path = (
                            PROJECT_ROOT / "data" / "mcp.duckdb"
                        )
                    print(
                        f"⚠️  Overrode invalid database path to: {self._settings.database.connection.path}"
                    )

                _config_manager_logger.info(
                    f"Settings successfully loaded via Pydantic (from .env and {self.config_path})."
                )
                _config_manager_logger.debug(
                    f"Final database path: {self._settings.database.connection.path}"
                )
            except Exception as e:
                _config_manager_logger.error(
                    f"Error loading settings: {e}. Falling back to default settings."
                )
                # If loading fails, ensure we still have a Settings instance with defaults
                self._settings = Settings()
        return self._settings

    def reload(self):
        """
        Forces a reload of configuration on the next call to get_settings().
        This clears the cached settings object.
        """
        self._settings = None
        _config_manager_logger.info("Configuration marked for reload.")


# Global configuration instance
config_manager = ConfigManager()


def get_server_config() -> Settings:
    """
    Convenience function to get server configuration.
    Returns the complete Settings object.
    """
    return config_manager.get_settings()


def get_development_config() -> DevelopmentConfig:
    """
    Convenience function to get development configuration.
    """
    return config_manager.get_settings().development


def get_database_config() -> DatabaseConfig:
    """
    Convenience function to get database configuration.
    """
    return config_manager.get_settings().database


def get_llm_config() -> LLMConfig:
    """
    Convenience function to get LLM configuration.
    """
    return config_manager.get_settings().llm


def get_visualization_config() -> VisualizationConfig:
    """
    Convenience function to get visualization configuration.
    """
    return config_manager.get_settings().visualization


# For backward compatibility, also expose the global settings instance
settings = config_manager.get_settings()
