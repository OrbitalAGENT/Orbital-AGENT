# config/loader.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = Path(os.getenv("CONFIG_PATH", "/etc/orbital"))
        self.config = {}
        
        config_files = [
            "base.yaml",
            "swarm.yaml", 
            "compliance.yaml",
            "resources.yaml",
            "eventbus.yaml",
            "monitoring.yaml"
        ]
        
        for file in config_files:
            with open(config_path / file) as f:
                self.config.update(yaml.safe_load(f))
        
        self._replace_env_vars()
    
    def _replace_env_vars(self):
        for key, value in self.config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                self.config[key] = os.getenv(env_var, "")

    def get(self, path: str, default=None) -> Any:
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

# Usage example:
# from config.loader import ConfigManager
# cfg = ConfigManager()
# api_endpoint = cfg.get('network.api_endpoint')
