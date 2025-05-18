
"""
ROOcode Model Selector Module

This module implements the ModelSelector component of the ROOcode system, which is responsible
for selecting the most appropriate AI model for a given task. The selector uses task characteristics,
model capabilities, and performance metrics to make intelligent model selection decisions.
"""

import logging
from typing import Dict, List, Any, Optional
from .model_registry import ModelRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ROOcode.ModelSelector")

class ModelSelector:
    """
    The ModelSelector component of the ROOcode system.
    
    The ModelSelector is responsible for choosing the most appropriate AI model for a given task
    based on task characteristics, model capabilities, and performance metrics.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialize the ModelSelector with a model registry.
        
        Args:
            model_registry: The ModelRegistry containing available models
        """
        self.model_registry = model_registry
        logger.info("ModelSelector initialized")
    
    def select_model(self, task: Dict[str, Any]) -> str:
        """
        Select the most appropriate model for a given task.
        
        Args:
            task: A dictionary describing the task, including type, requirements, and constraints
            
        Returns:
            The name of the selected model
        """
        # Extract task characteristics
        task_type = task.get("task_type", "")
        requirements = task.get("requirements", [])
        constraints = task.get("constraints", [])
        
        # Check if a specific model is requested
        if "model" in task:
            requested_model = task["model"]
            if self.model_registry.get_model(requested_model):
                logger.info(f"Using explicitly requested model: {requested_model}")
                return requested_model
            else:
                logger.warning(f"Requested model {requested_model} not found, falling back to selection logic")
        
        # Determine required capabilities based on task type
        required_capabilities = self._determine_required_capabilities(task_type, requirements)
        
        # Find models with the required capabilities
        candidate_models = self._find_candidate_models(required_capabilities)
        
        if not candidate_models:
            logger.warning(f"No models found with required capabilities: {required_capabilities}")
            logger.info(f"Falling back to default model: {self.model_registry.default_model}")
            return self.model_registry.default_model
        
        # Apply constraints to filter candidates
        filtered_candidates = self._apply_constraints(candidate_models, constraints)
        
        if not filtered_candidates:
            logger.warning(f"No models satisfy constraints: {constraints}")
            logger.info(f"Falling back to candidates without constraints: {candidate_models}")
            filtered_candidates = candidate_models
        
        # Rank the remaining candidates
        ranked_models = self._rank_models(filtered_candidates, task_type, requirements)
        
        if not ranked_models:
            logger.warning("No models available after ranking")
            logger.info(f"Falling back to default model: {self.model_registry.default_model}")
            return self.model_registry.default_model
        
        # Select the highest-ranked model
        selected_model = ranked_models[0]
        logger.info(f"Selected model for task type '{task_type}': {selected_model}")
        
        return selected_model
    
    def _determine_required_capabilities(self, task_type: str, requirements: List[str]) -> List[str]:
        """
        Determine the capabilities required for a task based on its type and requirements.
        
        Args:
            task_type: The type of task
            requirements: The task requirements
            
        Returns:
            A list of required capabilities
        """
        # Map task types to required capabilities
        task_capability_map = {
            "system_design": ["natural_language_understanding", "reasoning", "system_design"],
            "component_design": ["natural_language_understanding", "reasoning", "system_design"],
            "interface_design": ["natural_language_understanding", "reasoning", "system_design"],
            "analyze_requirements": ["natural_language_understanding", "reasoning"],
            "implement_component": ["natural_language_understanding", "code_generation"],
            "implement_interface": ["natural_language_understanding", "code_generation"],
            "refactor_code": ["natural_language_understanding", "code_generation"],
            "fix_bug": ["natural_language_understanding", "code_generation", "debugging"],
            "test_component": ["natural_language_understanding", "code_generation", "debugging"],
            "validate_interface": ["natural_language_understanding", "code_generation", "debugging"],
            "performance_test": ["natural_language_understanding", "code_generation", "debugging"]
        }
        
        # Get the base capabilities for the task type
        capabilities = task_capability_map.get(task_type, ["natural_language_understanding", "instruction_following"])
        
        # Add additional capabilities based on requirements
        for requirement in requirements:
            requirement_lower = requirement.lower()
            
            if "complex" in requirement_lower and "reasoning" in requirement_lower:
                capabilities.append("complex_reasoning")
            
            if "optimize" in requirement_lower or "performance" in requirement_lower:
                capabilities.append("debugging")
            
            if "security" in requirement_lower:
                capabilities.append("debugging")
        
        # Remove duplicates
        return list(set(capabilities))
    
    def _find_candidate_models(self, required_capabilities: List[str]) -> List[str]:
        """
        Find models that have all the required capabilities.
        
        Args:
            required_capabilities: The capabilities required for the task
            
        Returns:
            A list of model names that have all the required capabilities
        """
        all_models = self.model_registry.list_models()
        candidate_models = []
        
        for model_name in all_models:
            model_info = self.model_registry.get_model(model_name)
            model_capabilities = model_info.get("capabilities", [])
            
            # Check if the model has all required capabilities
            if all(capability in model_capabilities for capability in required_capabilities):
                candidate_models.append(model_name)
        
        return candidate_models
    
    def _apply_constraints(self, candidate_models: List[str], constraints: List[str]) -> List[str]:
        """
        Apply constraints to filter candidate models.
        
        Args:
            candidate_models: The list of candidate model names
            constraints: The constraints to apply
            
        Returns:
            A filtered list of model names that satisfy the constraints
        """
        if not constraints:
            return candidate_models
        
        filtered_candidates = []
        
        for model_name in candidate_models:
            model_info = self.model_registry.get_model(model_name)
            satisfies_constraints = True
            
            for constraint in constraints:
                constraint_lower = constraint.lower()
                
                # Check for cost constraints
                if "low cost" in constraint_lower or "budget" in constraint_lower:
                    # Filter out expensive models
                    if model_info.get("cost", {}).get("output_tokens", 0) > 0.00003:
                        satisfies_constraints = False
                        break
                
                # Check for performance constraints
                if "high performance" in constraint_lower:
                    # Require high performance models
                    performance_values = model_info.get("performance", {}).values()
                    if not performance_values or sum(performance_values) / len(performance_values) < 0.85:
                        satisfies_constraints = False
                        break
                
                # Check for provider constraints
                if "provider:" in constraint_lower:
                    provider = constraint_lower.split("provider:")[1].strip()
                    if model_info.get("provider", "").lower() != provider:
                        satisfies_constraints = False
                        break
            
            if satisfies_constraints:
                filtered_candidates.append(model_name)
        
        return filtered_candidates
    
    def _rank_models(self, candidate_models: List[str], task_type: str, requirements: List[str]) -> List[str]:
        """
        Rank candidate models based on their suitability for the task.
        
        Args:
            candidate_models: The list of candidate model names
            task_type: The type of task
            requirements: The task requirements
            
        Returns:
            A list of model names sorted by their suitability (highest first)
        """
        # Map task types to relevant performance metrics
        task_metric_map = {
            "system_design": ["system_design", "reasoning"],
            "component_design": ["system_design", "reasoning"],
            "interface_design": ["system_design", "reasoning"],
            "analyze_requirements": ["reasoning"],
            "implement_component": ["code_generation"],
            "implement_interface": ["code_generation"],
            "refactor_code": ["code_generation"],
            "fix_bug": ["debugging", "code_generation"],
            "test_component": ["debugging", "code_generation"],
            "validate_interface": ["debugging", "code_generation"],
            "performance_test": ["debugging"]
        }
        
        # Get the relevant metrics for the task type
        relevant_metrics = task_metric_map.get(task_type, ["reasoning"])
        
        # Calculate a score for each candidate model
        model_scores = []
        
        for model_name in candidate_models:
            model_info = self.model_registry.get_model(model_name)
            performance = model_info.get("performance", {})
            
            # Calculate the average performance score for relevant metrics
            metric_scores = [performance.get(metric, 0) for metric in relevant_metrics]
            avg_performance = sum(metric_scores) / len(metric_scores) if metric_scores else 0
            
            # Adjust score based on model size and cost
            size_factor = 1.0
            if model_info.get("size") == "Opus":
                size_factor = 0.9  # Slightly penalize larger models for efficiency
            elif model_info.get("size") == "Haiku":
                size_factor = 1.1  # Slightly boost smaller models for efficiency
            
            # Calculate final score
            final_score = avg_performance * size_factor
            
            model_scores.append((model_name, final_score))
        
        # Sort models by score (descending)
        model_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted model names
        return [model[0] for model in model_scores]
