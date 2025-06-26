# Logging utilities
"""
Logging configuration and utilities
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None, enable_rich: bool = True
) -> logging.Logger:
    """
    Set up logging configuration with optional file output and rich formatting

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_rich: Use rich formatting for console output

    Returns:
        Configured logger instance
    """

    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with rich formatting
    if enable_rich:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_width=100,
            tracebacks_extra_lines=3,
        )
        console_format = "%(message)s"
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all messages

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # Create application logger
    app_logger = logging.getLogger("mcp-viz-server")

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    return logging.getLogger(f"mcp-viz-server.{name}")


class LoggerMixin:
    """Mixin class to add logging to any class"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


def log_function_call(func):
    """Decorator to log function calls with arguments"""

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise

    return wrapper


async def log_async_function_call(func):
    """Decorator to log async function calls with arguments"""

    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed: {e}")
            raise

    return wrapper


def log_performance(func):
    """Decorator to log function performance"""
    import time

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise

    return wrapper


def log_data_operations(operation_type: str):
    """Decorator to log data operations with row counts"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.info(f"Starting {operation_type}: {func.__name__}")

            try:
                result = func(*args, **kwargs)

                # Try to extract row count information
                row_info = ""
                if hasattr(result, "__len__"):
                    row_info = f" ({len(result)} rows)"
                elif isinstance(result, dict) and "row_count" in result:
                    row_info = f" ({result['row_count']} rows)"

                logger.info(f"Completed {operation_type}: {func.__name__}{row_info}")
                return result

            except Exception as e:
                logger.error(f"Failed {operation_type}: {func.__name__} - {e}")
                raise

        return wrapper

    return decorator


class StructuredLogger:
    """Logger that outputs structured log data"""

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def log_chart_creation(
        self,
        chart_type: str,
        table_name: str,
        column_count: int,
        row_count: int,
        success: bool,
    ):
        """Log chart creation event"""
        self.logger.info(
            "Chart creation",
            extra={
                "event_type": "chart_creation",
                "chart_type": chart_type,
                "table_name": table_name,
                "column_count": column_count,
                "row_count": row_count,
                "success": success,
            },
        )

    def log_database_operation(
        self, operation: str, table_name: str, duration: float, success: bool
    ):
        """Log database operation"""
        self.logger.info(
            "Database operation",
            extra={
                "event_type": "database_operation",
                "operation": operation,
                "table_name": table_name,
                "duration": duration,
                "success": success,
            },
        )

    def log_llm_request(
        self, model: str, prompt_type: str, response_time: float, success: bool
    ):
        """Log LLM request"""
        self.logger.info(
            "LLM request",
            extra={
                "event_type": "llm_request",
                "model": model,
                "prompt_type": prompt_type,
                "response_time": response_time,
                "success": success,
            },
        )


# Global structured logger instance
structured_logger = StructuredLogger("structured")
