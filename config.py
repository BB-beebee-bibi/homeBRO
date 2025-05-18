"""
Configuration Module

This module contains configuration settings for the homeBRO system.
"""

import os
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("homeBRO.Config")

class Config:
    """
    Configuration class for the homeBRO system.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        logger.info("Configuration initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            The configuration dictionary
        """
        default_config = {
            "chatllm": {
                "api_key": os.getenv("CHATLLM_API_KEY", ""),
                "base_url": "https://api.chatllm.com/v1",
                "default_model": "claude-3-sonnet",
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "orchestrator": {
                "max_concurrent_tasks": 5,
                "task_timeout": 300,  # seconds
                "retry_attempts": 3,
                "retry_delay": 5  # seconds
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "homebro.log"
            },
            "models": {
                "default": "claude-3-sonnet",
                "fallback": "claude-3-haiku"
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge file config with default config
                    self._merge_configs(default_config, file_config)
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                logger.info(f"Created default configuration file: {self.config_file}")
        
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.info("Using default configuration")
        
        return default_config
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Merge two configuration dictionaries.
        
        Args:
            default: The default configuration
            override: The configuration to override with
        """
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_configs(default[key], value)
            else:
                default[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key (dot-separated for nested keys)
            default: The default value if the key is not found
            
        Returns:
            The configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key (dot-separated for nested keys)
            value: The value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        # Save to file
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def save(self) -> None:
        """
        Save the current configuration to file.
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")

# Create a global configuration instance
config = Config()
