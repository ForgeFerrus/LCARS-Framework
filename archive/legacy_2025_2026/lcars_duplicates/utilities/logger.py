"""
Configuration for application-wide logging.
Status: STABLE
Since: 2026-02-15
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

def setup_logging(log_dir: Optional[Path] = None, level: int = logging.WARNING) -> None:
    """Note: Idempotent - safe to call multiple times.
    
    Args:
        log_dir: Directory for log files (default: project_root/logs)
        level: Logging level for console output (default: WARNING)
    """
    # 1. Determine log directory
    if log_dir is None:
        # lcars/utils/logger.py -> lcars/utils -> lcars -> root
        root_dir = Path(__file__).resolve().parent.parent.parent
        log_dir = root_dir / "logs"
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If we can't create logs directory, fallback to stderr and exit early
        print(f"CRITICAL: Could not create log directory at {log_dir}", file=sys.stderr)
        return

    log_file = log_dir / "lcars.log"
    
    # 2. Get the root logger
    root_logger = logging.getLogger()
    # Set level to lowest to capture everything, handlers will filter
    root_logger.setLevel(logging.DEBUG) 

    # 3. Check for existing handlers to prevent duplication
    # We identify our file handler by checking its baseFilename
    has_file_handler = any(
        isinstance(h, logging.handlers.RotatingFileHandler) and 
        getattr(h, 'baseFilename', '') == str(log_file.resolve())
        for h in root_logger.handlers
    )
    
    has_console_handler = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root_logger.handlers
    )

    # 4. Add File Handler (Rotating, UTF-8)
    if not has_file_handler:
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO) # Always log INFO+ to file
            file_fmt = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_fmt)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"WARNING: Failed to setup file logging: {e}", file=sys.stderr)

    # 5. Add Console Handler
    if not has_console_handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level) # Use user-specified level (default WARNING)
        console_fmt = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_fmt)
        root_logger.addHandler(console_handler)

    # 6. Silence noisy libraries if needed
    logging.getLogger("PyQt6").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
