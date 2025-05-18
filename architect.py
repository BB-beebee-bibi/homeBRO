
"""
ROOcode Architect Module

This module implements the Architect component of the ROOcode system, which is responsible for
high-level system design, architecture decisions, and technical specifications. The Architect
analyzes requirements and creates system designs, defines component interfaces and data structures,
creates technical specifications for implementation, evaluates architectural trade-offs, and
ensures design patterns and best practices are followed.

The Architect component interfaces with the Orchestrator to receive design tasks and return
specifications, and with the Repository to store and retrieve design artifacts.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from orchestrator import (
    Message, Task, Response, StatusUpdate, ErrorMessage,
    MessageType, Priority, TaskStatus, ErrorSeverity, RecoveryStrategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ROOcode.Architect")


class Architect:
    """
    The Architect component of the ROOcode system.
    
    The Architect is responsible for high-level system design, architecture decisions,
    and technical specifications. It analyzes requirements, creates system designs,
    defines component interfaces and data structures, and ensures design patterns and
    best practices are followed.
    """
    
    def __init__(self, knowledge_base=None, code_repository=None):
        """
        Initialize the Architect component.
        
        Args:
            knowledge_base: Optional knowledge base for accessing design patterns and best practices
            code_repository: Optional code repository for storing and retrieving design artifacts
        """
        self.knowledge_base = knowledge_base
        self.code_repository = code_repository
        self.component_name = "architect"
        logger.info("Architect component initialized")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a design task assigned by the Orchestrator.
        
        Args:
            task: The task to execute
            
        Returns:
            A dictionary containing the result of the task execution
            
        Raises:
            ValueError: If the task type is unknown
        """
        task_type = task.content.get("task_type", "")
        task_id = task.content.get("task_id", "")
        
        # Get the selected model from the task payload
        model = task.content.get("payload", {}).get("model", "Claude-3.7-Sonnet")
        
        logger.info(f"Executing task {task_id} of type {task_type} with model {model}")
        
        # Send status update indicating task has started
        await self._send_status_update(task_id, 0, "starting")
        
        try:
            # Dispatch to appropriate method based on task type
            if task_type == "system_design":
                result = await self._design_system(task, model)
            elif task_type == "component_design":
                result = await self._design_component(task, model)
            elif task_type == "interface_design":
                result = await self._design_interface(task, model)
            elif task_type == "analyze_requirements":
                result = await self._analyze_requirements(task, model)
            else:
                error_msg = f"Unknown task type: {task_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Send status update indicating task is complete
            await self._send_status_update(task_id, 100, "completed")
            
            # Return successful response
            return {
                "status": "completed",
                "result": result,
                "model_used": model
            }
            
        except Exception as e:
            # Log the error
            error_msg = f"Error executing task {task_id}: {str(e)}"
            logger.error(error_msg)
            
            # Send error message
            await self._send_error_message(
                task_id,
                "execution_error",
                ErrorSeverity.WARNING,
                str(e),
                {"task_type": task_type, "model": model}
            )
            
            # Return error response
            return {
                "status": "failed",
                "error": str(e),
                "model_used": model
            }
    
    async def receive_message(self, message: Message) -> None:
        """
        Receive a message from the Orchestrator.
        
        Args:
            message: The message received
        """
        if message.message_type == MessageType.TASK:
            # Handle task message
            task = Task.from_json(message.to_json())
            result = await self.execute_task(task)
            
            # Create and send response
            response = Response(
                task_id=task.content["task_id"],
                status=result.get("status", "failed"),
                result=result.get("result", {}),
                sender=self.component_name,
                recipient=message.sender
            )
            
            # In a real implementation, this would send the response back to the Orchestrator
            logger.debug(f"Sending response for task {task.content['task_id']}")
            # await self._send_response(response)
        
        elif message.message_type == MessageType.STATUS:
            # Handle status request
            logger.debug(f"Received status request: {message.content}")
            # Implement status handling logic
        
        else:
            logger.warning(f"Received unsupported message type: {message.message_type}")
    
    async def _design_system(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Create a high-level system design based on requirements.
        
        Args:
            task: The system design task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the system design artifacts
        """
        # Extract requirements and constraints from task payload
        requirements = task.content.get("payload", {}).get("requirements", [])
        constraints = task.content.get("payload", {}).get("constraints", [])
        
        logger.info(f"Designing system with {len(requirements)} requirements and {len(constraints)} constraints")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 25, "analyzing_requirements")
        
        # Analyze requirements (in a real implementation, this would be more sophisticated)
        components = self._identify_components(requirements)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 50, "defining_architecture")
        
        # Define system architecture
        architecture = self._define_architecture(components, constraints)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 75, "creating_specifications")
        
        # Create detailed specifications
        specifications = self._create_specifications(components, architecture)
        
        # If we have a code repository, store the design artifacts
        if self.code_repository:
            # Store design artifacts in the repository
            # self.code_repository.save_design_artifacts(specifications)
            pass
        
        # Return the design artifacts
        return {
            "system_diagram": architecture.get("system_diagram", ""),
            "components": components,
            "interfaces": architecture.get("interfaces", []),
            "data_models": specifications.get("data_models", []),
            "design_rationale": specifications.get("design_rationale", "")
        }
    
    async def _design_component(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Design a specific component based on requirements.
        
        Args:
            task: The component design task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the component design artifacts
        """
        # Extract component name and requirements from task payload
        component_name = task.content.get("payload", {}).get("component_name", "")
        requirements = task.content.get("payload", {}).get("requirements", [])
        
        logger.info(f"Designing component {component_name} with {len(requirements)} requirements")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 33, "defining_responsibilities")
        
        # Define component responsibilities
        responsibilities = self._define_responsibilities(component_name, requirements)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 66, "defining_interfaces")
        
        # Define component interfaces
        interfaces = self._define_interfaces(component_name, responsibilities)
        
        # Return the component design
        return {
            "component_name": component_name,
            "responsibilities": responsibilities,
            "interfaces": interfaces,
            "internal_structure": self._define_internal_structure(component_name, responsibilities)
        }
    
    async def _design_interface(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Design interfaces between components.
        
        Args:
            task: The interface design task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the interface design artifacts
        """
        # Extract components and requirements from task payload
        components = task.content.get("payload", {}).get("components", [])
        requirements = task.content.get("payload", {}).get("requirements", [])
        
        logger.info(f"Designing interfaces between {len(components)} components")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 50, "defining_interfaces")
        
        # Define interfaces between components
        interfaces = []
        for i, component1 in enumerate(components):
            for component2 in components[i+1:]:
                interface = self._define_component_interface(component1, component2, requirements)
                interfaces.append(interface)
        
        # Return the interface designs
        return {
            "interfaces": interfaces,
            "communication_patterns": self._define_communication_patterns(interfaces)
        }
    
    async def _analyze_requirements(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Analyze requirements to extract design implications.
        
        Args:
            task: The requirements analysis task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the analysis results
        """
        # Extract requirements from task payload
        requirements = task.content.get("payload", {}).get("requirements", [])
        
        logger.info(f"Analyzing {len(requirements)} requirements")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 50, "analyzing_requirements")
        
        # Analyze requirements (in a real implementation, this would be more sophisticated)
        functional_reqs = []
        non_functional_reqs = []
        constraints = []
        
        for req in requirements:
            # Simple classification based on keywords (in a real implementation, this would be more sophisticated)
            if any(kw in req.lower() for kw in ["shall", "must", "will"]):
                functional_reqs.append(req)
            elif any(kw in req.lower() for kw in ["performance", "security", "usability", "reliability"]):
                non_functional_reqs.append(req)
            elif any(kw in req.lower() for kw in ["constraint", "limitation", "restriction"]):
                constraints.append(req)
            else:
                # Default to functional requirement
                functional_reqs.append(req)
        
        # Return the analysis results
        return {
            "functional_requirements": functional_reqs,
            "non_functional_requirements": non_functional_reqs,
            "constraints": constraints,
            "design_implications": self._extract_design_implications(functional_reqs, non_functional_reqs)
        }
    
    def _identify_components(self, requirements: List[str]) -> List[Dict[str, Any]]:
        """
        Identify system components based on requirements.
        
        Args:
            requirements: The system requirements
            
        Returns:
            A list of component definitions
        """
        # In a real implementation, this would use more sophisticated analysis
        # For now, we'll create a simple set of components
        
        # Default components that most systems would have
        components = [
            {
                "name": "frontend",
                "description": "User interface component",
                "responsibilities": ["Display information to users", "Capture user input"]
            },
            {
                "name": "backend",
                "description": "Business logic component",
                "responsibilities": ["Process business rules", "Coordinate system activities"]
            },
            {
                "name": "database",
                "description": "Data storage component",
                "responsibilities": ["Store and retrieve data", "Ensure data integrity"]
            }
        ]
        
        # Add additional components based on requirements
        if any("authentication" in req.lower() for req in requirements):
            components.append({
                "name": "authentication",
                "description": "User authentication component",
                "responsibilities": ["Verify user identity", "Manage user sessions"]
            })
        
        if any("api" in req.lower() for req in requirements):
            components.append({
                "name": "api_gateway",
                "description": "API Gateway component",
                "responsibilities": ["Route API requests", "Handle API versioning"]
            })
        
        return components
    
    def _define_architecture(self, components: List[Dict[str, Any]], constraints: List[str]) -> Dict[str, Any]:
        """
        Define the system architecture based on components and constraints.
        
        Args:
            components: The system components
            constraints: The system constraints
            
        Returns:
            A dictionary containing the architecture definition
        """
        # In a real implementation, this would consider various architectural patterns
        # For now, we'll create a simple layered architecture
        
        # Define layers
        layers = [
            {
                "name": "presentation",
                "components": [c["name"] for c in components if c["name"] in ["frontend", "api_gateway"]]
            },
            {
                "name": "business",
                "components": [c["name"] for c in components if c["name"] in ["backend", "authentication"]]
            },
            {
                "name": "data",
                "components": [c["name"] for c in components if c["name"] in ["database"]]
            }
        ]
        
        # Define interfaces between components
        interfaces = []
        for i, layer in enumerate(layers[:-1]):
            for comp1 in layer["components"]:
                for comp2 in layers[i+1]["components"]:
                    interfaces.append({
                        "name": f"{comp1}_to_{comp2}",
                        "source": comp1,
                        "target": comp2,
                        "type": "synchronous"  # Default to synchronous
                    })
        
        # Create a simple system diagram (in a real implementation, this would be more sophisticated)
        system_diagram = f"""
        System Architecture Diagram
        --------------------------
        {layers[0]['name'].upper()} LAYER: {', '.join(layers[0]['components'])}
                |
                v
        {layers[1]['name'].upper()} LAYER: {', '.join(layers[1]['components'])}
                |
                v
        {layers[2]['name'].upper()} LAYER: {', '.join(layers[2]['components'])}
        """
        
        return {
            "layers": layers,
            "interfaces": interfaces,
            "system_diagram": system_diagram
        }
    
    def _create_specifications(self, components: List[Dict[str, Any]], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create detailed specifications based on components and architecture.
        
        Args:
            components: The system components
            architecture: The system architecture
            
        Returns:
            A dictionary containing the detailed specifications
        """
        # Define data models
        data_models = []
        for component in components:
            if component["name"] == "database":
                # Create data models for the database
                data_models.extend([
                    {
                        "name": "User",
                        "attributes": [
                            {"name": "id", "type": "string", "description": "Unique identifier"},
                            {"name": "username", "type": "string", "description": "User's username"},
                            {"name": "email", "type": "string", "description": "User's email address"}
                        ]
                    },
                    {
                        "name": "Product",
                        "attributes": [
                            {"name": "id", "type": "string", "description": "Unique identifier"},
                            {"name": "name", "type": "string", "description": "Product name"},
                            {"name": "price", "type": "number", "description": "Product price"}
                        ]
                    }
                ])
        
        # Define API specifications
        api_specs = []
        for interface in architecture.get("interfaces", []):
            if interface["source"] == "api_gateway":
                # Create API specifications for the API gateway
                api_specs.append({
                    "endpoint": f"/api/{interface['target']}",
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "parameters": [
                        {"name": "id", "type": "string", "description": "Resource identifier"}
                    ],
                    "responses": [
                        {"code": 200, "description": "Success"},
                        {"code": 400, "description": "Bad request"},
                        {"code": 401, "description": "Unauthorized"},
                        {"code": 404, "description": "Not found"},
                        {"code": 500, "description": "Server error"}
                    ]
                })
        
        # Create design rationale
        design_rationale = """
        Design Rationale
        ---------------
        The system follows a layered architecture pattern to separate concerns and improve maintainability.
        The presentation layer handles user interactions and API requests.
        The business layer implements the core business logic and authentication.
        The data layer manages data storage and retrieval.
        
        This architecture was chosen for its simplicity, scalability, and alignment with the system requirements.
        """
        
        return {
            "data_models": data_models,
            "api_specifications": api_specs,
            "design_rationale": design_rationale
        }
    
    def _define_responsibilities(self, component_name: str, requirements: List[str]) -> List[str]:
        """
        Define the responsibilities of a component based on requirements.
        
        Args:
            component_name: The name of the component
            requirements: The requirements related to the component
            
        Returns:
            A list of responsibilities for the component
        """
        # In a real implementation, this would analyze requirements more thoroughly
        # For now, we'll define some default responsibilities based on component name
        
        if component_name == "frontend":
            return [
                "Display information to users in a user-friendly manner",
                "Capture and validate user input",
                "Communicate with backend services",
                "Handle client-side errors gracefully"
            ]
        elif component_name == "backend":
            return [
                "Implement business logic according to requirements",
                "Process and validate data from the frontend",
                "Communicate with the database and external services",
                "Handle server-side errors and exceptions"
            ]
        elif component_name == "database":
            return [
                "Store and retrieve data efficiently",
                "Ensure data integrity and consistency",
                "Implement data access controls",
                "Backup and recover data as needed"
            ]
        elif component_name == "authentication":
            return [
                "Verify user identity through secure mechanisms",
                "Manage user sessions and tokens",
                "Implement authorization controls",
                "Protect against common security threats"
            ]
        elif component_name == "api_gateway":
            return [
                "Route API requests to appropriate services",
                "Handle API versioning and backward compatibility",
                "Implement rate limiting and throttling",
                "Provide API documentation and discovery"
            ]
        else:
            # Generic responsibilities for unknown components
            return [
                f"Implement core functionality for {component_name}",
                "Communicate with other components as needed",
                "Handle errors and exceptions gracefully",
                "Maintain performance and reliability standards"
            ]
    
    def _define_interfaces(self, component_name: str, responsibilities: List[str]) -> List[Dict[str, Any]]:
        """
        Define the interfaces for a component based on its responsibilities.
        
        Args:
            component_name: The name of the component
            responsibilities: The responsibilities of the component
            
        Returns:
            A list of interface definitions for the component
        """
        # In a real implementation, this would derive interfaces from responsibilities
        # For now, we'll define some default interfaces based on component name
        
        interfaces = []
        
        if component_name == "frontend":
            interfaces.append({
                "name": "UserInterface",
                "methods": [
                    {"name": "displayData", "parameters": ["data"], "returns": "void"},
                    {"name": "getUserInput", "parameters": ["form"], "returns": "userInput"},
                    {"name": "showError", "parameters": ["errorMessage"], "returns": "void"}
                ]
            })
        elif component_name == "backend":
            interfaces.append({
                "name": "BusinessLogic",
                "methods": [
                    {"name": "processRequest", "parameters": ["request"], "returns": "response"},
                    {"name": "validateData", "parameters": ["data"], "returns": "validationResult"},
                    {"name": "executeTransaction", "parameters": ["transaction"], "returns": "result"}
                ]
            })
        elif component_name == "database":
            interfaces.append({
                "name": "DataAccess",
                "methods": [
                    {"name": "create", "parameters": ["entity", "data"], "returns": "id"},
                    {"name": "read", "parameters": ["entity", "id"], "returns": "data"},
                    {"name": "update", "parameters": ["entity", "id", "data"], "returns": "success"},
                    {"name": "delete", "parameters": ["entity", "id"], "returns": "success"}
                ]
            })
        elif component_name == "authentication":
            interfaces.append({
                "name": "AuthService",
                "methods": [
                    {"name": "login", "parameters": ["credentials"], "returns": "session"},
                    {"name": "logout", "parameters": ["session"], "returns": "success"},
                    {"name": "verifyToken", "parameters": ["token"], "returns": "validity"},
                    {"name": "checkPermission", "parameters": ["user", "resource", "action"], "returns": "allowed"}
                ]
            })
        elif component_name == "api_gateway":
            interfaces.append({
                "name": "ApiGateway",
                "methods": [
                    {"name": "routeRequest", "parameters": ["request"], "returns": "response"},
                    {"name": "validateApiKey", "parameters": ["apiKey"], "returns": "validity"},
                    {"name": "throttleRequest", "parameters": ["clientId"], "returns": "allowed"}
                ]
            })
        else:
            # Generic interface for unknown components
            interfaces.append({
                "name": f"{component_name.capitalize()}Service",
                "methods": [
                    {"name": "process", "parameters": ["input"], "returns": "output"},
                    {"name": "getStatus", "parameters": [], "returns": "status"},
                    {"name": "configure", "parameters": ["config"], "returns": "success"}
                ]
            })
        
        return interfaces
    
    def _define_internal_structure(self, component_name: str, responsibilities: List[str]) -> str:
        """
        Define the internal structure of a component.
        
        Args:
            component_name: The name of the component
            responsibilities: The responsibilities of the component
            
        Returns:
            A string describing the internal structure of the component
        """
        # In a real implementation, this would create a more detailed structure
        # For now, we'll create a simple description
        
        return f"""
        Internal Structure of {component_name.capitalize()}
        ------------------------------
        The {component_name} component is organized into the following modules:
        
        1. Core - Implements the main functionality
        2. Utilities - Provides helper functions and utilities
        3. Interfaces - Defines interfaces with other components
        4. Error Handling - Manages errors and exceptions
        
        Each module is responsible for a subset of the component's responsibilities
        and follows the single responsibility principle.
        """
    
    def _define_component_interface(self, component1: str, component2: str, requirements: List[str]) -> Dict[str, Any]:
        """
        Define the interface between two components.
        
        Args:
            component1: The name of the first component
            component2: The name of the second component
            requirements: The system requirements
            
        Returns:
            A dictionary defining the interface between the components
        """
        # In a real implementation, this would analyze requirements to determine the interface
        # For now, we'll create a simple interface definition
        
        interface_name = f"{component1}_to_{component2}"
        
        # Define methods based on component types
        methods = []
        if component1 == "frontend" and component2 == "backend":
            methods = [
                {"name": "submitForm", "parameters": ["formData"], "returns": "response"},
                {"name": "fetchData", "parameters": ["query"], "returns": "data"},
                {"name": "reportError", "parameters": ["error"], "returns": "acknowledgement"}
            ]
        elif component1 == "backend" and component2 == "database":
            methods = [
                {"name": "executeQuery", "parameters": ["query"], "returns": "resultSet"},
                {"name": "executeTransaction", "parameters": ["transaction"], "returns": "result"},
                {"name": "checkConnection", "parameters": [], "returns": "status"}
            ]
        elif component1 == "backend" and component2 == "authentication":
            methods = [
                {"name": "authenticateUser", "parameters": ["credentials"], "returns": "authResult"},
                {"name": "validateSession", "parameters": ["session"], "returns": "validity"},
                {"name": "getUserPermissions", "parameters": ["userId"], "returns": "permissions"}
            ]
        else:
            # Generic interface for other component combinations
            methods = [
                {"name": "sendRequest", "parameters": ["request"], "returns": "response"},
                {"name": "getStatus", "parameters": [], "returns": "status"}
            ]
        
        # Determine communication pattern
        communication_pattern = "synchronous"  # Default
        if any("async" in req.lower() for req in requirements):
            communication_pattern = "asynchronous"
        
        return {
            "name": interface_name,
            "source": component1,
            "target": component2,
            "methods": methods,
            "communication_pattern": communication_pattern,
            "data_format": "JSON"  # Default
        }
    
    def _define_communication_patterns(self, interfaces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Define communication patterns between components.
        
        Args:
            interfaces: The interfaces between components
            
        Returns:
            A dictionary defining the communication patterns
        """
        # Count the number of each communication pattern
        sync_count = sum(1 for i in interfaces if i.get("communication_pattern") == "synchronous")
        async_count = sum(1 for i in interfaces if i.get("communication_pattern") == "asynchronous")
        
        # Determine the dominant pattern
        dominant_pattern = "synchronous" if sync_count >= async_count else "asynchronous"
        
        # Create a description of the communication patterns
        description = f"""
        Communication Patterns
        ---------------------
        The system uses a mix of synchronous and asynchronous communication patterns:
        - Synchronous: {sync_count} interfaces
        - Asynchronous: {async_count} interfaces
        
        The dominant pattern is {dominant_pattern}.
        
        Synchronous interfaces are used for operations that require immediate responses,
        while asynchronous interfaces are used for operations that can be processed in the background.
        """
        
        return {
            "dominant_pattern": dominant_pattern,
            "synchronous_count": sync_count,
            "asynchronous_count": async_count,
            "description": description
        }
    
    def _extract_design_implications(self, functional_reqs: List[str], non_functional_reqs: List[str]) -> List[str]:
        """
        Extract design implications from requirements.
        
        Args:
            functional_reqs: The functional requirements
            non_functional_reqs: The non-functional requirements
            
        Returns:
            A list of design implications
        """
        # In a real implementation, this would analyze requirements more thoroughly
        # For now, we'll create some simple design implications
        
        implications = []
        
        # Implications from functional requirements
        if functional_reqs:
            implications.append("The system must implement all specified functional capabilities")
            implications.append("User interactions should be intuitive and follow established patterns")
        
        # Implications from non-functional requirements
        for req in non_functional_reqs:
            if "performance" in req.lower():
                implications.append("The architecture should optimize for performance, possibly using caching and efficient algorithms")
            elif "security" in req.lower():
                implications.append("Security measures must be implemented at all layers of the architecture")
            elif "usability" in req.lower():
                implications.append("The user interface should be designed with usability principles in mind")
            elif "reliability" in req.lower():
                implications.append("The system should include error handling and recovery mechanisms")
            elif "scalability" in req.lower():
                implications.append("The architecture should support horizontal scaling to handle increased load")
        
        # Add some default implications if we don't have many
        if len(implications) < 3:
            implications.extend([
                "The system should follow the separation of concerns principle",
                "Components should communicate through well-defined interfaces",
                "The architecture should be flexible enough to accommodate future changes"
            ])
        
        return implications
    
    async def _send_status_update(self, task_id: str, progress: int, stage: str) -> None:
        """
        Send a status update for a task.
        
        Args:
            task_id: The ID of the task
            progress: The progress percentage (0-100)
            stage: The current stage of execution
        """
        status_update = StatusUpdate(
            task_id=task_id,
            progress=progress,
            stage=stage,
            sender=self.component_name
        )
        
        # In a real implementation, this would send the status update to the Orchestrator
        logger.debug(f"Sending status update for task {task_id}: {progress}% ({stage})")
        # await self._send_message(status_update)
    
    async def _send_error_message(self, task_id: str, error_code: str, severity: ErrorSeverity,
                                 description: str, context: Dict[str, Any]) -> None:
        """
        Send an error message for a task.
        
        Args:
            task_id: The ID of the task
            error_code: The error code
            severity: The severity of the error
            description: A description of the error
            context: Additional context for the error
        """
        error_message = ErrorMessage(
            task_id=task_id,
            error_code=error_code,
            severity=severity,
            description=description,
            context=context,
            recovery_suggestion="Retry the task with modified parameters",
            sender=self.component_name
        )
        
        # In a real implementation, this would send the error message to the Orchestrator
        logger.error(f"Sending error message for task {task_id}: {description}")
        # await self._send_message(error_message)


# Export the Architect class
__all__ = ['Architect']
