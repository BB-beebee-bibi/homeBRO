#!/usr/bin/env python3
"""
homeBRO Demo Script

This script demonstrates how to use homeBRO with ChatLLM for various coding tasks.
"""

import asyncio
import logging
from typing import Dict, Any
import os

from models.model_registry import ModelRegistry
from models.chatllm_adapter import ChatLLMAdapter
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("homeBRO.Demo")

async def analyze_code_example(adapter: ChatLLMAdapter) -> None:
    """
    Demonstrate code analysis using ChatLLM.
    
    Args:
        adapter: The ChatLLM adapter
    """
    code = """
def calculate_fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    """
    
    logger.info("Analyzing code...")
    result = await adapter.analyze_code(
        code=code,
        task="Analyze the performance and suggest improvements",
        model="claude-3-sonnet"
    )
    
    print("\n=== Code Analysis ===")
    print(result["completion"])

async def generate_code_example(adapter: ChatLLMAdapter) -> None:
    """
    Demonstrate code generation using ChatLLM.
    
    Args:
        adapter: The ChatLLM adapter
    """
    specification = """
Create a Python class for a simple task manager that can:
1. Add tasks with a title, description, and due date
2. Mark tasks as complete
3. List all tasks
4. Filter tasks by status (complete/incomplete)
5. Delete tasks
Include proper error handling and documentation.
    """
    
    logger.info("Generating code...")
    result = await adapter.generate_code(
        specification=specification,
        task_type="implement_component",
        model="claude-3-sonnet"
    )
    
    print("\n=== Generated Code ===")
    print(result["completion"])

async def refactor_code_example(adapter: ChatLLMAdapter) -> None:
    """
    Demonstrate code refactoring using ChatLLM.
    
    Args:
        adapter: The ChatLLM adapter
    """
    code = """
class UserManager:
    def __init__(self):
        self.users = {}
    
    def add_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        return True
    
    def check_password(self, username, password):
        if username not in self.users:
            return False
        return self.users[username] == password
    
    def remove_user(self, username):
        if username not in self.users:
            return False
        del self.users[username]
        return True
    """
    
    requirements = [
        "Add proper password hashing",
        "Add input validation",
        "Add error handling",
        "Add type hints",
        "Add docstrings"
    ]
    
    logger.info("Refactoring code...")
    result = await adapter.refactor_code(
        code=code,
        requirements=requirements,
        model="claude-3-sonnet"
    )
    
    print("\n=== Refactored Code ===")
    print(result["completion"])

async def fix_bug_example(adapter: ChatLLMAdapter) -> None:
    """
    Demonstrate bug fixing using ChatLLM.
    
    Args:
        adapter: The ChatLLM adapter
    """
    code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        elif item < 0:
            result.append(item * -1)
    return result

# Test the function
test_data = [1, -2, 3, -4, 0]
print(process_data(test_data))  # Expected: [2, 2, 6, 4, 0]
    """
    
    bug_description = """
The function is not handling the case when item is 0 correctly.
According to the test case, 0 should be included in the result,
but the current implementation skips it.
    """
    
    logger.info("Fixing bug...")
    result = await adapter.fix_bug(
        code=code,
        bug_description=bug_description,
        model="claude-3-sonnet"
    )
    
    print("\n=== Fixed Code ===")
    print(result["completion"])

async def main() -> None:
    """
    Main function to run the demo.
    """
    # Check for API key
    api_key = config.get("chatllm.api_key")
    if not api_key:
        logger.error("ChatLLM API key not found. Please set the CHATLLM_API_KEY environment variable.")
        return
    
    # Initialize the ChatLLM adapter
    adapter = ChatLLMAdapter(api_key=api_key)
    
    # Run examples
    print("Running homeBRO demo with ChatLLM...")
    
    await analyze_code_example(adapter)
    await generate_code_example(adapter)
    await refactor_code_example(adapter)
    await fix_bug_example(adapter)
    
    print("\nDemo completed!")

if __name__ == "__main__":
    asyncio.run(main())
