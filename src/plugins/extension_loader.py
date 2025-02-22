# src/plugins/extension_loader.py
import importlib
import pkgutil
from types import ModuleType
from typing import Dict

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugins: Dict[str, ModuleType] = {}
        self.base_path = plugin_dir
        
    def discover_plugins(self) -> None:
        for finder, name, _ in pkgutil.iter_modules([self.base_path]):
            module = importlib.import_module(f"{self.base_path}.{name}")
            if hasattr(module, "initialize"):
                self.plugins[name] = module
                
    def initialize_plugin(self, name: str, config: dict) -> bool:
        if name in self.plugins:
            return self.plugins[name].initialize(config)
        return False
        
    def execute_hook(self, hook_name: str, *args) -> None:
        for plugin in self.plugins.values():
            if hasattr(plugin, hook_name):
                getattr(plugin, hook_name)(*args)
