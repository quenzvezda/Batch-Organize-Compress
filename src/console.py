import os
import logging
from datetime import datetime

# Setup log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure standard logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)

logger = logging.getLogger("AppLog")


def print_header(title):
    """Log a major section header."""
    logger.info(f"=== {title} ===")


def print_step(step_idx, total_steps, title):
    """Log a processing step."""
    logger.info(f"Step {step_idx}/{total_steps}: {title}")


def print_success(message):
    """Log a success message."""
    logger.info(f"[SUCCESS] {message}")


def print_error(message):
    """Log an error message."""
    logger.error(f"[ERROR] {message}")
