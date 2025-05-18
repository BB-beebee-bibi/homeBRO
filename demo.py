#!/usr/bin/env python3
"""
ROOcode System Demonstration Script

This script demonstrates the complete ROOcode system in action, processing a sample coding task
from requirements to implementation and testing. It initializes all four components (Orchestrator,
Architect, Coder, and Debugger), registers them with the Orchestrator, and shows the workflow
from requirements to final code.

The script includes detailed output showing the messages exchanged between components and the
progress of the task. It also demonstrates the model-switching capability of the system.
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime

# Import ROOcode components
from orchestrator import Orchestrator, Priority, Task
from architect import Architect
from coder import Coder
from debugger import Debugger
from models import ModelRegistry, ModelSelector
from config import config

# Configure logging to show detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ROOcode.Demo")

# Global storage for component outputs to simulate a shared repository
code_repository = {}


async def main():
    """
    Main demonstration function that shows the ROOcode system in action.
    """
    logger.info("Starting ROOcode System Demonstration")
    logger.info("=====================================")
    
    # Step 1: Initialize all components
    logger.info("\nStep 1: Initializing Components")
    logger.info("-----------------------------")
    
    orchestrator = Orchestrator()
    architect = Architect()
    coder = Coder()
    debugger = Debugger()
    
    logger.info("All components initialized successfully")
    
    # Step 2: Register components with the Orchestrator
    logger.info("\nStep 2: Registering Components with Orchestrator")
    logger.info("--------------------------------------------")
    
    orchestrator.register_agent("architect", architect)
    logger.info("Registered Architect with Orchestrator")
    
    orchestrator.register_agent("coder", coder)
    logger.info("Registered Coder with Orchestrator")
    
    orchestrator.register_agent("debugger", debugger)
    logger.info("Registered Debugger with Orchestrator")
    
    # Step 3: Display available models
    logger.info("\nStep 3: Available AI Models")
    logger.info("-------------------------")
    
    available_models = orchestrator.get_available_models()
    logger.info(f"Available models: {', '.join(available_models)}")
    
    default_model = orchestrator.model_registry.default_model
    logger.info(f"Default model: {default_model}")
    
    # Step 4: Define a sample task
    logger.info("\nStep 4: Defining Sample Tasks")
    logger.info("-------------------------")
    
    # Define a simple task to create a weather API service
    weather_api_task = {
        "task_type": "implement_system",
        "requirements": [
            "Create a weather service that provides current weather information",
            "The service should have a REST API endpoint to get weather by city",
            "Weather data should include temperature, humidity, and conditions",
            "The service should handle errors gracefully",
            "The API should be well-documented"
        ],
        "constraints": [
            "Use Node.js for the implementation",
            "Follow RESTful API design principles",
            "Include proper error handling",
            "Include unit tests"
        ],
        "metadata": {
            "priority": "medium",
            "deadline": (datetime.now().isoformat())
        }
    }
    
    # Define a task that requires complex reasoning
    complex_task = {
        "task_type": "system_design",
        "requirements": [
            "Design a distributed database system with strong consistency guarantees",
            "The system should support horizontal scaling across multiple data centers",
            "Implement a consensus algorithm for distributed transaction management",
            "Ensure the system can recover from network partitions",
            "Design a query optimization engine for complex analytical queries"
        ],
        "constraints": [
            "Minimize latency for read operations",
            "Ensure data durability even in the presence of multiple node failures",
            "Support both SQL and NoSQL interfaces",
            "Implement fine-grained access control"
        ],
        "metadata": {
            "priority": "high",
            "deadline": (datetime.now().isoformat())
        }
    }
    
    logger.info(f"Weather API task defined: {json.dumps(weather_api_task, indent=2)}")
    logger.info(f"Complex system design task defined: {json.dumps(complex_task, indent=2)}")
    
    # Step 5: Execute components with automatic model selection
    logger.info("\nStep 5: Executing Components with Automatic Model Selection")
    logger.info("-----------------------------------------------------")
    
    # Step 5.1: Execute Architect with automatic model selection for weather API task
    logger.info("\nStep 5.1: Executing Architect Component for Weather API Task")
    logger.info("--------------------------------------------------------")
    
    architect_task = Task(
        task_id=str(uuid.uuid4()),
        task_type="system_design",
        payload={
            "requirements": weather_api_task["requirements"],
            "constraints": weather_api_task["constraints"]
        },
        sender="orchestrator",
        recipient="architect"
    )
    
    logger.info("Executing architect task with automatic model selection...")
    architect_result = await orchestrator._execute_task(architect, architect_task)
    logger.info(f"Architect task completed using model: {architect_result.get('model_used', 'unknown')}")
    
    # Store architect results
    if architect_result["status"] == "completed":
        code_repository["design"] = architect_result["result"]
        logger.info("Stored design results in code repository")
        
        # Print design summary
        components = architect_result["result"].get("components", [])
        logger.info(f"Design summary: {len(components)} components designed")
        for comp in components:
            logger.info(f"  - {comp.get('name', 'unnamed')}: {comp.get('description', 'no description')}")
    else:
        logger.error(f"Architect task failed: {architect_result.get('error', 'Unknown error')}")
    
    # Step 5.2: Execute Architect with explicit model selection for complex task
    logger.info("\nStep 5.2: Executing Architect Component for Complex Task with Explicit Model")
    logger.info("----------------------------------------------------------------------")
    
    # For complex reasoning tasks, we'll explicitly use Claude-3.5-Opus
    complex_architect_task = Task(
        task_id=str(uuid.uuid4()),
        task_type="system_design",
        payload={
            "requirements": complex_task["requirements"],
            "constraints": complex_task["constraints"],
            "model": "Claude-3.5-Opus"  # Explicitly specify the model
        },
        sender="orchestrator",
        recipient="architect"
    )
    
    logger.info("Executing architect task with explicit model selection...")
    complex_architect_result = await orchestrator._execute_task(architect, complex_architect_task)
    logger.info(f"Complex architect task completed using model: {complex_architect_result.get('model_used', 'unknown')}")
    
    # Store complex architect results
    if complex_architect_result["status"] == "completed":
        code_repository["complex_design"] = complex_architect_result["result"]
        logger.info("Stored complex design results in code repository")
        
        # Print design summary
        components = complex_architect_result["result"].get("components", [])
        logger.info(f"Complex design summary: {len(components)} components designed")
        for comp in components:
            logger.info(f"  - {comp.get('name', 'unnamed')}: {comp.get('description', 'no description')}")
    else:
        logger.error(f"Complex architect task failed: {complex_architect_result.get('error', 'Unknown error')}")
    
    # Step 5.3: Change default model and execute Coder
    logger.info("\nStep 5.3: Changing Default Model and Executing Coder Component")
    logger.info("----------------------------------------------------------")
    
    # Change the default model to Claude-3.5-Haiku for efficiency
    previous_default = orchestrator.model_registry.default_model
    orchestrator.set_default_model("Claude-3.5-Haiku")
    logger.info(f"Changed default model from {previous_default} to {orchestrator.model_registry.default_model}")
    
    # Use the design from the architect to create the coder task
    component_name = "main"  # Default component name
    if "design" in code_repository and "components" in code_repository["design"]:
        # Find a suitable component to implement (e.g., backend)
        for comp in code_repository["design"]["components"]:
            if comp["name"] == "backend":
                component_name = "backend"
                break
    
    coder_task = Task(
        task_id=str(uuid.uuid4()),
        task_type="implement_component",
        payload={
            "component_name": component_name,
            "requirements": weather_api_task["requirements"],
            "specification": code_repository.get("design", {})
        },
        sender="orchestrator",
        recipient="coder"
    )
    
    logger.info(f"Executing coder task for component '{component_name}'...")
    coder_result = await orchestrator._execute_task(coder, coder_task)
    logger.info(f"Coder task completed using model: {coder_result.get('model_used', 'unknown')}")
    
    # Store coder results
    if coder_result["status"] == "completed":
        code_repository["implementation"] = coder_result["result"]
        
        # Store the code specifically for the debugger to use
        component = coder_result["result"].get("component", component_name)
        code = coder_result["result"].get("code", "")
        code_repository[f"code_{component}"] = code
        logger.info(f"Stored implementation for component '{component}' in code repository")
        
        # Print implementation summary
        code_lines = code.count("\n") if code else 0
        logger.info(f"Implementation summary: Component '{component}' with {code_lines} lines of code")
    else:
        logger.error(f"Coder task failed: {coder_result.get('error', 'Unknown error')}")
    
    # Step 5.4: Execute Debugger with model auto-selection
    logger.info("\nStep 5.4: Executing Debugger Component with Auto-Selection")
    logger.info("------------------------------------------------------")
    
    # Reset default model to original
    orchestrator.set_default_model(previous_default)
    logger.info(f"Reset default model to {orchestrator.model_registry.default_model}")
    
    # Use the implementation from the coder for the debugger task
    if "implementation" in code_repository:
        component = code_repository["implementation"].get("component", component_name)
        code = code_repository["implementation"].get("code", "")
        
        if code:
            debugger_task = Task(
                task_id=str(uuid.uuid4()),
                task_type="test_component",
                payload={
                    "component_name": component,
                    "code": code,
                    "requirements": weather_api_task["requirements"]
                },
                sender="orchestrator",
                recipient="debugger"
            )
            
            logger.info(f"Executing debugger task for component '{component}'...")
            debugger_result = await orchestrator._execute_task(debugger, debugger_task)
            logger.info(f"Debugger task completed using model: {debugger_result.get('model_used', 'unknown')}")
            
            # Store debugger results
            if debugger_result["status"] == "completed":
                code_repository["testing"] = debugger_result["result"]
                logger.info("Stored testing results in code repository")
                
                # Print testing summary
                status = debugger_result["result"].get("status", "unknown")
                issues = debugger_result["result"].get("bug_report", {}).get("issues", [])
                logger.info(f"Testing summary: Status '{status}' with {len(issues)} issues found")
            else:
                logger.error(f"Debugger task failed: {debugger_result.get('error', 'Unknown error')}")
        else:
            logger.error("No code available for testing")
    else:
        logger.error("No implementation available for testing")
    
    # Step 6: Display final results from all stages
    logger.info("\nStep 6: Final Results from All Stages")
    logger.info("----------------------------------")
    
    # Display model selection summary
    logger.info("\nModel Selection Summary:")
    logger.info(f"Available models: {', '.join(orchestrator.get_available_models())}")
    logger.info(f"Default model: {orchestrator.model_registry.default_model}")
    logger.info(f"Models used in this demonstration:")
    logger.info(f"  - Architect (Weather API): {architect_result.get('model_used', 'unknown')}")
    logger.info(f"  - Architect (Complex Task): {complex_architect_result.get('model_used', 'unknown')}")
    logger.info(f"  - Coder: {coder_result.get('model_used', 'unknown')}")
    logger.info(f"  - Debugger: {debugger_result.get('model_used', 'unknown') if 'debugger_result' in locals() else 'not executed'}")
    
    # Display design results
    if "design" in code_repository:
        design_result = code_repository["design"]
        logger.info("\nWeather API Design Stage Output:")
        
        # Show components
        components = design_result.get("components", [])
        logger.info(f"Components: {json.dumps(components, indent=2)}")
        
        # Show system diagram
        system_diagram = design_result.get("system_diagram", "No diagram available")
        logger.info(f"System Diagram:\n{system_diagram}")
    else:
        logger.warning("No weather API design results available")
    
    # Display complex design results
    if "complex_design" in code_repository:
        complex_design_result = code_repository["complex_design"]
        logger.info("\nComplex System Design Stage Output:")
        
        # Show components
        components = complex_design_result.get("components", [])
        logger.info(f"Components: {json.dumps(components, indent=2)}")
        
        # Show system diagram
        system_diagram = complex_design_result.get("system_diagram", "No diagram available")
        logger.info(f"System Diagram:\n{system_diagram}")
    else:
        logger.warning("No complex design results available")
    
    # Display implementation results
    if "implementation" in code_repository:
        impl_result = code_repository["implementation"]
        logger.info("\nImplementation Stage Output:")
        
        # Show component name
        component = impl_result.get("component", "No component name")
        logger.info(f"Component: {component}")
        
        # Show a snippet of the code (first 10 lines)
        code = impl_result.get("code", "No code available")
        code_lines = code.split("\n")
        code_snippet = "\n".join(code_lines[:min(10, len(code_lines))])
        logger.info(f"Code Snippet (first 10 lines):\n{code_snippet}\n...")
        
        # Show documentation summary
        docs = impl_result.get("documentation", "No documentation available")
        docs_lines = docs.split("\n")
        docs_snippet = "\n".join(docs_lines[:min(5, len(docs_lines))])
        logger.info(f"Documentation Snippet:\n{docs_snippet}\n...")
    else:
        logger.warning("No implementation results available")
    
    # Display testing results
    if "testing" in code_repository:
        test_result = code_repository["testing"]
        logger.info("\nTesting Stage Output:")
        
        # Show test status
        status = test_result.get("status", "Unknown")
        logger.info(f"Status: {status}")
        
        # Show test summary
        static_analysis = test_result.get("static_analysis", {})
        unit_tests = test_result.get("unit_tests", {})
        integration_tests = test_result.get("integration_tests", {})
        
        logger.info(f"Static Analysis: {static_analysis.get('summary', 'No summary available')}")
        logger.info(f"Unit Tests: {unit_tests.get('summary', 'No summary available')}")
        logger.info(f"Integration Tests: {integration_tests.get('summary', 'No summary available')}")
        
        # Show issues if any
        bug_report = test_result.get("bug_report", {})
        issues = bug_report.get("issues", [])
        if issues:
            logger.info("\nIssues Found:")
            for i, issue in enumerate(issues[:min(5, len(issues))]):
                logger.info(f"  {i+1}. [{issue.get('severity', 'unknown')}] {issue.get('message', 'No message')}")
            
            if len(issues) > 5:
                logger.info(f"  ... and {len(issues) - 5} more issues")
    else:
        logger.warning("No testing results available")
    
    logger.info("\nROOcode System Demonstration Completed")
    logger.info("=====================================")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
