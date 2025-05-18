
"""
ROOcode Configuration Module

This module provides configuration settings for the ROOcode system, including
model selection defaults and other system-wide settings.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ROOcode.Config")

class Config:
    """
    Configuration manager for the ROOcode system.
    
    This class loads and provides access to configuration settings for the ROOcode system.
    It supports loading from a YAML file and environment variables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to a configuration file
        """
        self.config = {
            # Default configuration values
            "model": {
                "default": "Claude-3.7-Sonnet",
                "auto_select": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "system": {
                "max_retries": 3,
                "timeout": 60
            }
        }
        
        # Load configuration from file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
        
        # Override with environment variables
        self._load_from_env()
        
        logger.info("Configuration loaded")
    
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    # Update the configuration with values from the file
                    self._update_config(self.config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables should be prefixed with ROOCODE_ and use double underscores
        to indicate nesting, e.g., ROOCODE_MODEL__DEFAULT for model.default.
        """
        prefix = "ROOCODE_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split by double underscore to get the path
                config_path = key[len(prefix):].lower().split("__")
                
                # Update the configuration
                self._set_nested_value(self.config, config_path, value)
        
        logger.debug("Applied environment variable overrides")
    
    def _update_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a nested dictionary.
        
        Args:
            target: The target dictionary to update
            source: The source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                self._update_config(target[key], value)
            else:
                # Update or add the value
                target[key] = value
    
    def _set_nested_value(self, config: Dict[str, Any], path: list, value: str) -> None:
        """
        Set a value in a nested dictionary based on a path.
        
        Args:
            config: The configuration dictionary
            path: The path to the value as a list of keys
            value: The value to set
        """
        if not path:
            return
        
        # Navigate to the correct level
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value, converting to appropriate type
        key = path[-1]
        if value.lower() == "true":
            current[key] = True
        elif value.lower() == "false":
            current[key] = False
        elif value.isdigit():
            current[key] = int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
            current[key] = float(value)
        else:
            current[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key, using dot notation for nested values
            default: The default value to return if the key is not found
            
        Returns:
            The configuration value, or the default if not found
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key, using dot notation for nested values
            value: The value to set
        """
        keys = key.split(".")
        self._set_nested_value(self.config, keys, str(value))
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration.
        
        Returns:
            The complete configuration dictionary
        """
        return self.config

# Create a global configuration instance
config = Config()
