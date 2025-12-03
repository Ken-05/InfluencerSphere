"""
logging_config.py
-----------------
Configures the application's logging format, handlers, and levels using
the standard Python 'logging' module. Ensures consistent, structured output
for debugging and production monitoring.
"""
import logging
import sys
from typing import Dict, Any

# Define standard logging format for structured output
LOGGING_FORMAT = (
    "%(levelname)s [%(asctime)s] "
    "%(name)s:%(module)s:%(lineno)d - "
    "%(message)s"
)


def configure_logging(log_level: str = "INFO"):
    """
    Sets up the root logger configuration for the entire application.
    Args:
        log_level: The minimum level to log (e.g., 'DEBUG', 'INFO', 'WARNING').
    """

    # Root Logger Configuration
    root_logger = logging.getLogger()

    # Set the overall minimum level
    root_logger.setLevel(log_level.upper())

    # Check if handlers are already configured (to prevent duplication in hot-reloading)
    if not root_logger.handlers:
        # Define the Handler (outputs logs to standard error stream)
        handler = logging.StreamHandler(sys.stderr)

        # Define the Formatter
        formatter = logging.Formatter(LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        # Add the handler to the root logger
        root_logger.addHandler(handler)

    print(f"INFO: Logging configured at level: {log_level.upper()}")


# Add a helper to quickly get a service logger
def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance for a specific module or service."""
    return logging.getLogger(name)

# Example: Get a logger for the ML prediction service
# ml_logger = get_logger("ml_prediction_service")