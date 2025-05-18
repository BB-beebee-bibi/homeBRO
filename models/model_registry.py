
"""
ROOcode Model Registry Module

This module implements the ModelRegistry component of the ROOcode system, which is responsible
for managing the available AI models. The registry maintains a catalog of models with their
capabilities, performance characteristics, and usage costs. It allows models to be registered,
retrieved, and queried based on various criteria.
"""

import logging
from typing import Dict, List, Any, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ROOcode.ModelRegistry")

class ModelRegistry:
    """
    The ModelRegistry component of the ROOcode system.
    
    The ModelRegistry maintains a catalog of available AI models and their characteristics.
    It provides methods to register new models, retrieve models by name or criteria,
    and query model capabilities.
    """
    
    def __init__(self, default_model: str = "Claude-3.7-Sonnet"):
        """
        Initialize the ModelRegistry with a default model.
        
        Args:
            default_model: The name of the default model to use when no specific model is requested
        """
        self.models = {}
        self.default_model = default_model
        self._register_default_models()
        logger.info(f"ModelRegistry initialized with default model: {default_model}")
    
    def register_model(self, model_name: str, model_info: Dict[str, Any]) -> None:
        """
        Register a new model with the registry.
        
        Args:
            model_name: The name of the model
            model_info: Information about the model, including capabilities, performance, and cost
        """
        if model_name in self.models:
            logger.warning(f"Model {model_name} already registered, updating information")
        
        self.models[model_name] = model_info
        logger.info(f"Registered model: {model_name}")
    
    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            The model information, or None if the model is not registered
        """
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not found in registry")
            return None
        
        return self.models[model_name]
    
    def get_default_model(self) -> Dict[str, Any]:
        """
        Get information about the default model.
        
        Returns:
            The default model information
        """
        return self.get_model(self.default_model)
    
    def set_default_model(self, model_name: str) -> bool:
        """
        Set the default model.
        
        Args:
            model_name: The name of the model to set as default
            
        Returns:
            True if successful, False if the model is not registered
        """
        if model_name not in self.models:
            logger.warning(f"Cannot set default model: {model_name} not found in registry")
            return False
        
        self.default_model = model_name
        logger.info(f"Default model set to: {model_name}")
        return True
    
    def list_models(self) -> List[str]:
        """
        Get a list of all registered model names.
        
        Returns:
            A list of model names
        """
        return list(self.models.keys())
    
    def find_models_by_capability(self, capability: str) -> List[str]:
        """
        Find models that have a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            A list of model names that have the specified capability
        """
        matching_models = []
        
        for model_name, model_info in self.models.items():
            capabilities = model_info.get("capabilities", [])
            if capability in capabilities:
                matching_models.append(model_name)
        
        return matching_models
    
    def find_models_by_criteria(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Find models that match specific criteria.
        
        Args:
            criteria: A dictionary of criteria to match against model information
            
        Returns:
            A list of model names that match the criteria
        """
        matching_models = []
        
        for model_name, model_info in self.models.items():
            matches = True
            
            for key, value in criteria.items():
                if key not in model_info or model_info[key] != value:
                    matches = False
                    break
            
            if matches:
                matching_models.append(model_name)
        
        return matching_models
    
    def _register_default_models(self) -> None:
        """
        Register the default set of models with the registry.
        """
        # Register Claude 3.7 Sonnet
        self.register_model("Claude-3.7-Sonnet", {
            "provider": "Anthropic",
            "version": "3.7",
            "size": "Sonnet",
            "capabilities": [
                "natural_language_understanding",
                "code_generation",
                "reasoning",
                "instruction_following",
                "system_design",
                "debugging"
            ],
            "performance": {
                "reasoning": 0.9,
                "code_generation": 0.85,
                "system_design": 0.9,
                "debugging": 0.8
            },
            "cost": {
                "input_tokens": 0.00000325,
                "output_tokens": 0.00001550
            },
            "context_window": 200000,
            "description": "Claude 3.7 Sonnet is a powerful and efficient model with strong reasoning and code generation capabilities."
        })
        
        # Register Claude 3.5 Sonnet
        self.register_model("Claude-3.5-Sonnet", {
            "provider": "Anthropic",
            "version": "3.5",
            "size": "Sonnet",
            "capabilities": [
                "natural_language_understanding",
                "code_generation",
                "reasoning",
                "instruction_following",
                "system_design",
                "debugging"
            ],
            "performance": {
                "reasoning": 0.85,
                "code_generation": 0.8,
                "system_design": 0.85,
                "debugging": 0.75
            },
            "cost": {
                "input_tokens": 0.00000300,
                "output_tokens": 0.00001500
            },
            "context_window": 200000,
            "description": "Claude 3.5 Sonnet is a balanced model with good performance across a range of tasks."
        })
        
        # Register Claude 3.5 Haiku
        self.register_model("Claude-3.5-Haiku", {
            "provider": "Anthropic",
            "version": "3.5",
            "size": "Haiku",
            "capabilities": [
                "natural_language_understanding",
                "code_generation",
                "reasoning",
                "instruction_following"
            ],
            "performance": {
                "reasoning": 0.8,
                "code_generation": 0.75,
                "system_design": 0.7,
                "debugging": 0.65
            },
            "cost": {
                "input_tokens": 0.00000025,
                "output_tokens": 0.00000125
            },
            "context_window": 200000,
            "description": "Claude 3.5 Haiku is a fast and cost-effective model suitable for simpler tasks."
        })
        
        # Register Claude 3.5 Opus
        self.register_model("Claude-3.5-Opus", {
            "provider": "Anthropic",
            "version": "3.5",
            "size": "Opus",
            "capabilities": [
                "natural_language_understanding",
                "code_generation",
                "reasoning",
                "instruction_following",
                "system_design",
                "debugging",
                "complex_reasoning"
            ],
            "performance": {
                "reasoning": 0.95,
                "code_generation": 0.9,
                "system_design": 0.95,
                "debugging": 0.9
            },
            "cost": {
                "input_tokens": 0.00001500,
                "output_tokens": 0.00007500
            },
            "context_window": 200000,
            "description": "Claude 3.5 Opus is a high-performance model with exceptional reasoning and problem-solving capabilities."
        })
        
        # Register GPT-4o
        self.register_model("GPT-4o", {
            "provider": "OpenAI",
            "version": "4o",
            "size": "Standard",
            "capabilities": [
                "natural_language_understanding",
                "code_generation",
                "reasoning",
                "instruction_following",
                "system_design",
                "debugging"
            ],
            "performance": {
                "reasoning": 0.9,
                "code_generation": 0.9,
                "system_design": 0.85,
                "debugging": 0.85
            },
            "cost": {
                "input_tokens": 0.00001000,
                "output_tokens": 0.00003000
            },
            "context_window": 128000,
            "description": "GPT-4o is a versatile model with strong performance across a wide range of tasks."
        })
        
        logger.info(f"Registered {len(self.models)} default models")
