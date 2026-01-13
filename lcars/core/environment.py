"""
Environment Manager - handles Geant4 and system environment configuration
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages Geant4 environment setup and configuration"""
    
    def __init__(self):
        self.geant4_path: Optional[str] = None
        self.project_root: Path = Path(__file__).parent.parent.parent.parent
        self.env_vars: Dict[str, str] = {}
        self.config_file = self.project_root / "config" / "environment.json"
        self.load_config()
    
    def load_config(self):
        """Load environment configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.geant4_path = config.get("GEANT4_PATH")
                    self.env_vars = config.get("env_vars", {})
                    logger.info(f"Loaded environment config from {self.config_file}")
            else:
                self.auto_detect_geant4()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.auto_detect_geant4()
    
    def auto_detect_geant4(self):
        """Auto-detect Geant4 installation"""
        common_paths = [
            "C:\\geant4",
            "C:\\Program Files\\geant4",
            "C:\\Program Files (x86)\\geant4",
            os.path.expandvars("%ProgramFiles%\\geant4"),
            os.path.expandvars("%LocalAppData%\\geant4"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                self.geant4_path = path
                logger.info(f"Auto-detected Geant4 at: {path}")
                return
        
        logger.warning("Geant4 not found in common locations")
    
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "GEANT4_PATH": self.geant4_path,
            "env_vars": self.env_vars,
        }
        
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved environment config to {self.config_file}")
    
    def set_geant4_path(self, path: str) -> bool:
        """Set and validate Geant4 path"""
        if os.path.exists(path):
            self.geant4_path = path
            self.save_config()
            logger.info(f"Set Geant4 path to: {path}")
            return True
        logger.error(f"Path does not exist: {path}")
        return False
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables for subprocess execution"""
        env = os.environ.copy()
        
        if self.geant4_path:
            env["GEANT4_PATH"] = self.geant4_path
            # Add to PATH
            bin_path = os.path.join(self.geant4_path, "bin")
            if os.path.exists(bin_path):
                env["PATH"] = bin_path + ";" + env.get("PATH", "")
        
        env.update(self.env_vars)
        return env
    
    def get_status(self) -> Dict[str, any]:
        """Get environment status"""
        return {
            "geant4_detected": bool(self.geant4_path),
            "geant4_path": self.geant4_path,
            "project_root": str(self.project_root),
            "env_vars_count": len(self.env_vars),
        }
