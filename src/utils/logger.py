"""
logger.py
---------------------------------------
Central logging configuration.
"""

from loguru import logger
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "output" / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "project.log"

# Remove default logger
logger.remove()

# Console Logger
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
)

# File Logger
logger.add(
    LOG_FILE,
    level="DEBUG",
    rotation="5 MB",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
)

__all__ = ["logger"]