"""
ChatLLM Adapter Module

This module implements the ChatLLM adapter for the homeBRO system, which provides
an interface to interact with ChatLLM's API for various AI tasks.
"""

import logging
import json
from typing import Dict, Any, Optional, List
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("homeBRO.ChatLLMAdapter")

class ChatLLMAdapter:
    """
    The ChatLLM adapter for the homeBRO system.
    
    This adapter provides an interface to interact with ChatLLM's API for various AI tasks.
    It handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.chatllm.com/v1"):
        """
        Initialize the ChatLLM adapter.
        
        Args:
            api_key: The ChatLLM API key
            base_url: The base URL for the ChatLLM API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info("ChatLLM adapter initialized")
    
    async def generate_completion(self, 
                                prompt: str, 
                                model: str = "claude-3-sonnet", 
                                temperature: float = 0.7,
                                max_tokens: int = 4000,
                                system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a completion using ChatLLM.
        
        Args:
            prompt: The input prompt
            model: The model to use
            temperature: The temperature for generation
            max_tokens: The maximum number of tokens to generate
            system_prompt: Optional system prompt to guide the model
            
        Returns:
            A dictionary containing the generated completion and metadata
        """
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_prompt:
                payload["messages"].insert(0, {"role": "system", "content": system_prompt})
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            return {
                "completion": result["choices"][0]["message"]["content"],
                "model": model,
                "usage": result.get("usage", {}),
                "finish_reason": result["choices"][0].get("finish_reason", "stop")
            }
            
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    async def analyze_code(self, 
                          code: str, 
                          task: str,
                          model: str = "claude-3-sonnet") -> Dict[str, Any]:
        """
        Analyze code using ChatLLM.
        
        Args:
            code: The code to analyze
            task: The analysis task description
            model: The model to use
            
        Returns:
            A dictionary containing the analysis results
        """
        prompt = f"""Please analyze the following code for the task: {task}

Code:
```python
{code}
```

Provide a detailed analysis including:
1. Code quality assessment
2. Potential issues or bugs
3. Performance considerations
4. Security considerations
5. Recommendations for improvement
"""
        
        return await self.generate_completion(prompt, model=model)
    
    async def generate_code(self, 
                           specification: str, 
                           task_type: str,
                           model: str = "claude-3-sonnet") -> Dict[str, Any]:
        """
        Generate code based on a specification.
        
        Args:
            specification: The code specification
            task_type: The type of code generation task
            model: The model to use
            
        Returns:
            A dictionary containing the generated code and metadata
        """
        system_prompt = f"""You are an expert software developer. Your task is to generate high-quality code based on the given specification.
Task type: {task_type}

Follow these guidelines:
1. Write clean, maintainable, and well-documented code
2. Follow best practices and design patterns
3. Include appropriate error handling
4. Add comments explaining complex logic
5. Consider performance and security
"""
        
        return await self.generate_completion(
            specification,
            model=model,
            system_prompt=system_prompt
        )
    
    async def refactor_code(self, 
                           code: str, 
                           requirements: List[str],
                           model: str = "claude-3-sonnet") -> Dict[str, Any]:
        """
        Refactor code based on requirements.
        
        Args:
            code: The code to refactor
            requirements: List of refactoring requirements
            model: The model to use
            
        Returns:
            A dictionary containing the refactored code and metadata
        """
        requirements_str = "\n".join(f"- {req}" for req in requirements)
        
        prompt = f"""Please refactor the following code according to these requirements:

{requirements_str}

Original code:
```python
{code}
```

Provide the refactored code with explanations of the changes made.
"""
        
        return await self.generate_completion(prompt, model=model)
    
    async def fix_bug(self, 
                      code: str, 
                      bug_description: str,
                      model: str = "claude-3-sonnet") -> Dict[str, Any]:
        """
        Fix a bug in the code.
        
        Args:
            code: The code containing the bug
            bug_description: Description of the bug
            model: The model to use
            
        Returns:
            A dictionary containing the fixed code and metadata
        """
        prompt = f"""Please fix the following bug in the code:

Bug description: {bug_description}

Code:
```python
{code}
```

Provide the fixed code with an explanation of the bug and the fix.
"""
        
        return await self.generate_completion(prompt, model=model) 