import logging
import sys
from pathlib import Path

# Constants for logging configuration
LOG_FILE_PATH = Path("logs/agent_traces.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def _setup_logger() -> logging.Logger:
    """Create and configure the central OpenJarvis logger.

    @return: Configured Logger instance.
    """
    # Use 'openjarvis' as the root name for this package's logging hierarchy
    logger = logging.getLogger("openjarvis")
    logger.setLevel(logging.INFO)

    # Avoid adding handlers multiple times if the module is reloaded
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # Standard output handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

        # Persistent file handler
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Export a configured instance
logger = _setup_logger()
