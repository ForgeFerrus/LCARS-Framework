"""
Logging configuration
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(log_dir: Optional[Path] = None, level: int = logging.INFO) -> None:
    """Setup logging configuration"""
    
    if log_dir is None:
        log_dir = Path("logs")
    
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "lcars_framework.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
