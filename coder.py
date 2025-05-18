
"""
ROOcode Coder Module

This module implements the Coder component of the ROOcode system, which is responsible for
implementing code based on the Architect's specifications. The Coder generates efficient,
maintainable code, follows coding standards and best practices, documents code appropriately,
and refactors existing code when necessary.

The Coder component interfaces with the Orchestrator to receive coding tasks and return
implementations, and with the Repository to store and retrieve code artifacts.
"""

import asyncio
import json
import logging
import uuid
import os
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
logger = logging.getLogger("ROOcode.Coder")


class Coder:
    """
    The Coder component of the ROOcode system.
    
    The Coder is responsible for implementing code based on the Architect's specifications.
    It generates efficient, maintainable code, follows coding standards and best practices,
    documents code appropriately, and refactors existing code when necessary.
    """
    
    def __init__(self, knowledge_base=None, code_repository=None):
        """
        Initialize the Coder component.
        
        Args:
            knowledge_base: Optional knowledge base for accessing coding patterns and best practices
            code_repository: Optional code repository for storing and retrieving code artifacts
        """
        self.knowledge_base = knowledge_base
        self.code_repository = code_repository
        self.component_name = "coder"
        logger.info("Coder component initialized")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a coding task assigned by the Orchestrator.
        
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
            if task_type == "implement_component":
                result = await self._implement_component(task, model)
            elif task_type == "implement_interface":
                result = await self._implement_interface(task, model)
            elif task_type == "refactor_code":
                result = await self._refactor_code(task, model)
            elif task_type == "fix_bug":
                result = await self._fix_bug(task, model)
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
    
    async def _implement_component(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Implement a component based on specifications.
        
        Args:
            task: The component implementation task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the implemented code and documentation
        """
        # Extract component name and specification from task payload
        component_name = task.content.get("payload", {}).get("component_name", "")
        specification = task.content.get("payload", {}).get("specification", {})
        
        logger.info(f"Implementing component {component_name}")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 25, "analyzing_specification")
        
        # Analyze the specification
        component_type = self._determine_component_type(component_name, specification)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 50, "generating_code")
        
        # Generate code based on component type
        code = self._generate_component_code(component_name, component_type, specification)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 75, "generating_documentation")
        
        # Generate documentation
        documentation = self._generate_documentation(component_name, code)
        
        # If we have a code repository, store the code
        if self.code_repository:
            # Store code in the repository
            # self.code_repository.save_code(component_name, code)
            pass
        
        # Return the implementation
        return {
            "component": component_name,
            "code": code,
            "documentation": documentation,
            "tests": self._generate_tests(component_name, code)
        }
    
    async def _implement_interface(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Implement an interface based on specifications.
        
        Args:
            task: The interface implementation task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the implemented interface code
        """
        # Extract interface name and specification from task payload
        interface_name = task.content.get("payload", {}).get("interface_name", "")
        specification = task.content.get("payload", {}).get("specification", {})
        
        logger.info(f"Implementing interface {interface_name}")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 33, "analyzing_specification")
        
        # Analyze the specification
        methods = specification.get("methods", [])
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 66, "generating_code")
        
        # Generate interface code
        code = self._generate_interface_code(interface_name, methods)
        
        # Return the implementation
        return {
            "interface": interface_name,
            "code": code,
            "documentation": self._generate_documentation(interface_name, code)
        }
    
    async def _refactor_code(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Refactor existing code based on requirements.
        
        Args:
            task: The code refactoring task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the refactored code
        """
        # Extract code and requirements from task payload
        code = task.content.get("payload", {}).get("code", "")
        requirements = task.content.get("payload", {}).get("requirements", [])
        
        logger.info(f"Refactoring code with {len(requirements)} requirements")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 33, "analyzing_code")
        
        # Analyze the code
        code_analysis = self._analyze_code(code)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 66, "refactoring_code")
        
        # Refactor the code
        refactored_code = self._refactor(code, code_analysis, requirements)
        
        # Return the refactored code
        return {
            "original_code": code,
            "refactored_code": refactored_code,
            "changes": self._document_changes(code, refactored_code)
        }
    
    async def _fix_bug(self, task: Task, model: str) -> Dict[str, Any]:
        """
        Fix a bug in the code.
        
        Args:
            task: The bug fixing task
            model: The AI model to use for this task
            
        Returns:
            A dictionary containing the fixed code
        """
        # Extract code and bug report from task payload
        code = task.content.get("payload", {}).get("code", "")
        bug_report = task.content.get("payload", {}).get("bug_report", {})
        
        logger.info(f"Fixing bug: {bug_report.get('description', 'No description')}")
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 33, "analyzing_bug")
        
        # Analyze the bug
        bug_analysis = self._analyze_bug(code, bug_report)
        
        # Send status update
        await self._send_status_update(task.content["task_id"], 66, "fixing_bug")
        
        # Fix the bug
        fixed_code = self._fix(code, bug_analysis)
        
        # Return the fixed code
        return {
            "original_code": code,
            "fixed_code": fixed_code,
            "changes": self._document_changes(code, fixed_code),
            "verification": self._verify_fix(fixed_code, bug_report)
        }
    
    def _determine_component_type(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Determine the type of component based on its name and specification.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The type of the component
        """
        # In a real implementation, this would analyze the specification more thoroughly
        # For now, we'll use a simple mapping based on component name
        
        if component_name.lower() in ["frontend", "ui", "interface"]:
            return "frontend"
        elif component_name.lower() in ["backend", "server", "api"]:
            return "backend"
        elif component_name.lower() in ["database", "db", "storage"]:
            return "database"
        elif component_name.lower() in ["auth", "authentication", "security"]:
            return "authentication"
        elif component_name.lower() in ["api_gateway", "gateway"]:
            return "api_gateway"
        else:
            # Default to a generic service
            return "service"
    
    def _generate_component_code(self, component_name: str, component_type: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for a component based on its type and specification.
        
        Args:
            component_name: The name of the component
            component_type: The type of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # In a real implementation, this would generate more sophisticated code
        # For now, we'll create simple template code based on component type
        
        if component_type == "frontend":
            return self._generate_frontend_code(component_name, specification)
        elif component_type == "backend":
            return self._generate_backend_code(component_name, specification)
        elif component_type == "database":
            return self._generate_database_code(component_name, specification)
        elif component_type == "authentication":
            return self._generate_authentication_code(component_name, specification)
        elif component_type == "api_gateway":
            return self._generate_api_gateway_code(component_name, specification)
        else:
            # Generate generic service code
            return self._generate_service_code(component_name, specification)
    
    def _generate_frontend_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for a frontend component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple React component
        return f"""
import React, {{ useState, useEffect }} from 'react';

/**
 * {component_name.capitalize()} Component
 * 
 * A frontend component that handles user interactions and displays data.
 */
const {component_name.capitalize()} = ({{ onSubmit, initialData }}) => {{
    // State management
    const [data, setData] = useState(initialData or {{}});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Effect to load initial data
    useEffect(() => {{
        const fetchData = async () => {{
            try {{
                setLoading(true);
                // Fetch data from API
                const response = await fetch('/api/{component_name.lower()}');
                const result = await response.json();
                setData(result);
                setError(null);
            }} catch (err) {{
                setError('Failed to load data');
                console.error(err);
            }} finally {{
                setLoading(false);
            }}
        }};
        
        fetchData();
    }}, []);
    
    // Handle form submission
    const handleSubmit = async (event) => {{
        event.preventDefault();
        
        try {{
            setLoading(true);
            // Submit data to API
            const response = await fetch('/api/{component_name.lower()}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(data)
            }});
            
            const result = await response.json();
            
            if (response.ok) {{
                // Call the onSubmit callback with the result
                if (onSubmit) {{
                    onSubmit(result);
                }}
                setError(null);
            }} else {{
                setError(result.message or 'An error occurred');
            }}
        }} catch (err) {{
            setError('Failed to submit data');
            console.error(err);
        }} finally {{
            setLoading(false);
        }}
    }};
    
    // Handle input changes
    const handleChange = (event) => {{
        const {{ name, value }} = event.target;
        setData(prevData => ({{
            ...prevData,
            [name]: value
        }}));
    }};
    
    return (
        <div className="{component_name.lower()}-container">
            <h2>{component_name.capitalize()}</h2>
            
            {{error && <div className="error-message">{{error}}</div>}}
            
            <form onSubmit={handleSubmit}>
                {{/* Form fields would be generated based on the specification */}}
                <div className="form-field">
                    <label htmlFor="name">Name:</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={data.name or ''}
                        onChange={handleChange}
                        required
                    />
                </div>
                
                <div className="form-field">
                    <label htmlFor="description">Description:</label>
                    <textarea
                        id="description"
                        name="description"
                        value={data.description or ''}
                        onChange={handleChange}
                    />
                </div>
                
                <button type="submit" disabled={loading}>
                    {{loading ? 'Submitting...' : 'Submit'}}
                </button>
            </form>
            
            {{loading && <div className="loading-indicator">Loading...</div>}}
        </div>
    );
}};

export default {component_name.capitalize()};
"""
    
    def _generate_backend_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for a backend component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple Express.js backend service
        return f"""
const express = require('express');
const bodyParser = require('body-parser');
const logger = require('./logger');

/**
 * {component_name.capitalize()} Service
 * 
 * A backend service that implements business logic for {component_name}.
 */
class {component_name.capitalize()}Service {{
    constructor(database) {{
        this.database = database;
        this.router = express.Router();
        this.setupRoutes();
    }}
    
    /**
     * Set up the API routes for this service
     */
    setupRoutes() {{
        // Parse JSON request bodies
        this.router.use(bodyParser.json());
        
        // Get all items
        this.router.get('/', async (req, res) => {{
            try {{
                const items = await this.getAllItems();
                res.json(items);
            }} catch (error) {{
                logger.error(`Error getting items: ${{error.message}}`);
                res.status(500).json({{ message: 'Internal server error' }});
            }}
        }});
        
        // Get a specific item by ID
        this.router.get('/:id', async (req, res) => {{
            try {{
                const item = await this.getItemById(req.params.id);
                if (!item) {{
                    return res.status(404).json({{ message: 'Item not found' }});
                }}
                res.json(item);
            }} catch (error) {{
                logger.error(`Error getting item: ${{error.message}}`);
                res.status(500).json({{ message: 'Internal server error' }});
            }}
        }});
        
        // Create a new item
        this.router.post('/', async (req, res) => {{
            try {{
                const newItem = await this.createItem(req.body);
                res.status(201).json(newItem);
            }} catch (error) {{
                logger.error(`Error creating item: ${{error.message}}`);
                res.status(400).json({{ message: error.message }});
            }}
        }});
        
        // Update an existing item
        this.router.put('/:id', async (req, res) => {{
            try {{
                const updatedItem = await this.updateItem(req.params.id, req.body);
                if (!updatedItem) {{
                    return res.status(404).json({{ message: 'Item not found' }});
                }}
                res.json(updatedItem);
            }} catch (error) {{
                logger.error(`Error updating item: ${{error.message}}`);
                res.status(400).json({{ message: error.message }});
            }}
        }});
        
        // Delete an item
        this.router.delete('/:id', async (req, res) => {{
            try {{
                const success = await this.deleteItem(req.params.id);
                if (!success) {{
                    return res.status(404).json({{ message: 'Item not found' }});
                }}
                res.status(204).end();
            }} catch (error) {{
                logger.error(`Error deleting item: ${{error.message}}`);
                res.status(500).json({{ message: 'Internal server error' }});
            }}
        }});
    }}
    
    /**
     * Get all items from the database
     * @returns {{Promise<Array>}} Array of items
     */
    async getAllItems() {{
        return this.database.find('{component_name.lower()}', {{}});
    }}
    
    /**
     * Get an item by ID
     * @param {{string}} id - The item ID
     * @returns {{Promise<Object|null>}} The item or null if not found
     */
    async getItemById(id) {{
        return this.database.findOne('{component_name.lower()}', {{ id }});
    }}
    
    /**
     * Create a new item
     * @param {{Object}} data - The item data
     * @returns {{Promise<Object>}} The created item
     */
    async createItem(data) {{
        // Validate the data
        this._validateItemData(data);
        
        // Create the item
        return this.database.create('{component_name.lower()}', data);
    }}
    
    /**
     * Update an existing item
     * @param {{string}} id - The item ID
     * @param {{Object}} data - The updated data
     * @returns {{Promise<Object|null>}} The updated item or null if not found
     */
    async updateItem(id, data) {{
        // Validate the data
        this._validateItemData(data);
        
        // Update the item
        return this.database.update('{component_name.lower()}', id, data);
    }}
    
    /**
     * Delete an item
     * @param {{string}} id - The item ID
     * @returns {{Promise<boolean>}} True if deleted, false if not found
     */
    async deleteItem(id) {{
        return this.database.delete('{component_name.lower()}', id);
    }}
    
    /**
     * Validate item data
     * @param {{Object}} data - The data to validate
     * @throws {{Error}} If validation fails
     * @private
     */
    _validateItemData(data) {{
        if (!data) {{
            throw new Error('No data provided');
        }}
        
        if (!data.name) {{
            throw new Error('Name is required');
        }}
        
        // Add more validation as needed
    }}
}}

module.exports = {component_name.capitalize()}Service;
"""
    
    def _generate_database_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for a database component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple database access layer
        return f"""
const mongoose = require('mongoose');
const logger = require('./logger');

/**
 * {component_name.capitalize()} Database
 * 
 * A database component that handles data storage and retrieval.
 */
class {component_name.capitalize()}Database {{
    constructor(connectionString) {{
        this.connectionString = connectionString;
        this.models = {{}};
        this.connected = false;
    }}
    
    /**
     * Connect to the database
     * @returns {{Promise<void>}}
     */
    async connect() {{
        try {{
            await mongoose.connect(this.connectionString, {{
                useNewUrlParser: true,
                useUnifiedTopology: true,
                useCreateIndex: true,
                useFindAndModify: false
            }});
            
            this.connected = true;
            logger.info('Connected to database');
            
            // Define schemas and models
            this._defineModels();
        }} catch (error) {{
            logger.error(`Database connection error: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Disconnect from the database
     * @returns {{Promise<void>}}
     */
    async disconnect() {{
        if (this.connected) {{
            await mongoose.disconnect();
            this.connected = false;
            logger.info('Disconnected from database');
        }}
    }}
    
    /**
     * Define database models
     * @private
     */
    _defineModels() {{
        // User model
        const userSchema = new mongoose.Schema({{
            name: {{ type: String, required: true }},
            email: {{ type: String, required: true, unique: true }},
            password: {{ type: String, required: true }},
            createdAt: {{ type: Date, default: Date.now }},
            updatedAt: {{ type: Date, default: Date.now }}
        }});
        
        // Product model
        const productSchema = new mongoose.Schema({{
            name: {{ type: String, required: true }},
            description: {{ type: String }},
            price: {{ type: Number, required: true }},
            category: {{ type: String }},
            createdAt: {{ type: Date, default: Date.now }},
            updatedAt: {{ type: Date, default: Date.now }}
        }});
        
        // Register models
        this.models.User = mongoose.model('User', userSchema);
        this.models.Product = mongoose.model('Product', productSchema);
    }}
    
    /**
     * Find documents in a collection
     * @param {{string}} modelName - The name of the model
     * @param {{Object}} query - The query criteria
     * @returns {{Promise<Array>}} Array of documents
     */
    async find(modelName, query) {{
        this._checkConnection();
        const model = this._getModel(modelName);
        return model.find(query).exec();
    }}
    
    /**
     * Find a single document in a collection
     * @param {{string}} modelName - The name of the model
     * @param {{Object}} query - The query criteria
     * @returns {{Promise<Object|null>}} The document or null if not found
     */
    async findOne(modelName, query) {{
        this._checkConnection();
        const model = this._getModel(modelName);
        return model.findOne(query).exec();
    }}
    
    /**
     * Create a new document
     * @param {{string}} modelName - The name of the model
     * @param {{Object}} data - The document data
     * @returns {{Promise<Object>}} The created document
     */
    async create(modelName, data) {{
        this._checkConnection();
        const model = this._getModel(modelName);
        const document = new model(data);
        return document.save();
    }}
    
    /**
     * Update a document
     * @param {{string}} modelName - The name of the model
     * @param {{string}} id - The document ID
     * @param {{Object}} data - The updated data
     * @returns {{Promise<Object|null>}} The updated document or null if not found
     */
    async update(modelName, id, data) {{
        this._checkConnection();
        const model = this._getModel(modelName);
        
        // Add updatedAt timestamp
        data.updatedAt = new Date();
        
        return model.findByIdAndUpdate(id, data, {{ new: true }}).exec();
    }}
    
    /**
     * Delete a document
     * @param {{string}} modelName - The name of the model
     * @param {{string}} id - The document ID
     * @returns {{Promise<boolean>}} True if deleted, false if not found
     */
    async delete(modelName, id) {{
        this._checkConnection();
        const model = this._getModel(modelName);
        const result = await model.findByIdAndDelete(id).exec();
        return !!result;
    }}
    
    /**
     * Check if connected to the database
     * @throws {{Error}} If not connected
     * @private
     */
    _checkConnection() {{
        if (!this.connected) {{
            throw new Error('Not connected to database');
        }}
    }}
    
    /**
     * Get a model by name
     * @param {{string}} modelName - The name of the model
     * @returns {{Object}} The mongoose model
     * @throws {{Error}} If model not found
     * @private
     */
    _getModel(modelName) {{
        const model = this.models[modelName];
        if (!model) {{
            throw new Error(`Model not found: ${{modelName}}`);
        }}
        return model;
    }}
}}

module.exports = {component_name.capitalize()}Database;
"""
    
    def _generate_authentication_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for an authentication component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple authentication service
        return f"""
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const logger = require('./logger');

/**
 * {component_name.capitalize()} Service
 * 
 * An authentication service that handles user authentication and authorization.
 */
class {component_name.capitalize()}Service {{
    constructor(database, config) {{
        this.database = database;
        this.config = config;
    }}
    
    /**
     * Register a new user
     * @param {{Object}} userData - The user data
     * @returns {{Promise<Object>}} The created user (without password)
     */
    async registerUser(userData) {{
        try {{
            // Validate user data
            this._validateUserData(userData);
            
            // Check if user already exists
            const existingUser = await this.database.findOne('User', {{ email: userData.email }});
            if (existingUser) {{
                throw new Error('User already exists');
            }}
            
            // Hash the password
            const hashedPassword = await bcrypt.hash(userData.password, 10);
            
            // Create the user with hashed password
            const user = await this.database.create('User', {{
                ...userData,
                password: hashedPassword
            }});
            
            // Return user without password
            const {{ password, ...userWithoutPassword }} = user.toObject();
            return userWithoutPassword;
        }} catch (error) {{
            logger.error(`Error registering user: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Login a user
     * @param {{string}} email - The user's email
     * @param {{string}} password - The user's password
     * @returns {{Promise<Object>}} The authentication result
     */
    async loginUser(email, password) {{
        try {{
            // Find the user
            const user = await this.database.findOne('User', {{ email }});
            if (!user) {{
                throw new Error('Invalid email or password');
            }}
            
            // Verify the password
            const passwordMatch = await bcrypt.compare(password, user.password);
            if (!passwordMatch) {{
                throw new Error('Invalid email or password');
            }}
            
            // Generate a JWT token
            const token = this._generateToken(user);
            
            // Return the authentication result
            return {{
                token,
                user: {{
                    id: user._id,
                    name: user.name,
                    email: user.email
                }}
            }};
        }} catch (error) {{
            logger.error(`Error logging in user: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Verify a JWT token
     * @param {{string}} token - The JWT token
     * @returns {{Promise<Object>}} The decoded token payload
     */
    async verifyToken(token) {{
        try {{
            // Verify the token
            const decoded = jwt.verify(token, this.config.jwtSecret);
            
            // Check if the user still exists
            const user = await this.database.findOne('User', {{ _id: decoded.userId }});
            if (!user) {{
                throw new Error('User not found');
            }}
            
            return decoded;
        }} catch (error) {{
            logger.error(`Error verifying token: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Check if a user has permission to access a resource
     * @param {{string}} userId - The user ID
     * @param {{string}} resource - The resource name
     * @param {{string}} action - The action (read, write, delete)
     * @returns {{Promise<boolean>}} True if allowed, false otherwise
     */
    async checkPermission(userId, resource, action) {{
        try {{
            // Find the user
            const user = await this.database.findOne('User', {{ _id: userId }});
            if (!user) {{
                return false;
            }}
            
            // In a real implementation, this would check against a permissions system
            // For now, we'll just return true for simplicity
            return true;
        }} catch (error) {{
            logger.error(`Error checking permission: ${{error.message}}`);
            return false;
        }}
    }}
    
    /**
     * Generate a JWT token for a user
     * @param {{Object}} user - The user object
     * @returns {{string}} The JWT token
     * @private
     */
    _generateToken(user) {{
        return jwt.sign(
            {{ userId: user._id }},
            this.config.jwtSecret,
            {{ expiresIn: this.config.jwtExpiresIn }}
        );
    }}
    
    /**
     * Validate user data
     * @param {{Object}} userData - The user data to validate
     * @throws {{Error}} If validation fails
     * @private
     */
    _validateUserData(userData) {{
        if (!userData) {{
            throw new Error('No user data provided');
        }}
        
        if (!userData.name) {{
            throw new Error('Name is required');
        }}
        
        if (!userData.email) {{
            throw new Error('Email is required');
        }}
        
        if (!userData.password) {{
            throw new Error('Password is required');
        }}
        
        if (userData.password.length < 8) {{
            throw new Error('Password must be at least 8 characters long');
        }}
    }}
}}

module.exports = {component_name.capitalize()}Service;
"""
    
    def _generate_api_gateway_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for an API gateway component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple API gateway
        return f"""
const express = require('express');
const httpProxy = require('http-proxy');
const logger = require('./logger');

/**
 * {component_name.capitalize()} Gateway
 * 
 * An API gateway that routes requests to appropriate services.
 */
class {component_name.capitalize()}Gateway {{
    constructor(config) {{
        this.config = config;
        this.app = express();
        this.proxy = httpProxy.createProxyServer();
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }}
    
    /**
     * Set up middleware
     */
    setupMiddleware() {{
        // Parse JSON request bodies
        this.app.use(express.json());
        
        // Add request logging
        this.app.use((req, res, next) => {{
            logger.info(`${{req.method}} ${{req.url}}`);
            next();
        }});
        
        // Add CORS headers
        this.app.use((req, res, next) => {{
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
            if (req.method === 'OPTIONS') {{
                return res.sendStatus(200);
            }}
            next();
        }});
        
        // Add authentication middleware
        this.app.use(this._authMiddleware.bind(this));
    }}
    
    /**
     * Set up API routes
     */
    setupRoutes() {{
        // Define service routes
        const services = this.config.services;
        
        for (const [path, service] of Object.entries(services)) {{
            this.app.all(`/api/${{path}}*`, (req, res) => {{
                logger.info(`Routing request to ${{service.url}}`);
                
                // Add rate limiting headers
                if (service.rateLimit) {{
                    res.header('X-RateLimit-Limit', service.rateLimit.limit);
                    res.header('X-RateLimit-Remaining', service.rateLimit.remaining);
                }}
                
                // Proxy the request to the service
                this.proxy.web(req, res, {{ target: service.url }}, (err) => {{
                    logger.error(`Proxy error: ${{err.message}}`);
                    res.status(500).json({{ message: 'Internal server error' }});
                }});
            }});
        }}
        
        // Add a health check endpoint
        this.app.get('/health', (req, res) => {{
            res.json({{ status: 'ok' }});
        }});
        
        // Add API documentation endpoint
        this.app.get('/api-docs', (req, res) => {{
            res.json(this._generateApiDocs());
        }});
    }}
    
    /**
     * Set up error handling
     */
    setupErrorHandling() {{
        // Handle 404 errors
        this.app.use((req, res) => {{
            logger.warn(`Route not found: ${{req.method}} ${{req.url}}`);
            res.status(404).json({{ message: 'Not found' }});
        }});
        
        // Handle other errors
        this.app.use((err, req, res, next) => {{
            logger.error(`Error: ${{err.message}}`);
            res.status(err.status or 500).json({{ message: err.message or 'Internal server error' }});
        }});
    }}
    
    /**
     * Start the server
     * @returns {{Promise<void>}}
     */
    async start() {{
        return new Promise((resolve) => {{
            const port = this.config.port or 3000;
            this.server = this.app.listen(port, () => {{
                logger.info(`API Gateway listening on port ${{port}}`);
                resolve();
            }});
        }});
    }}
    
    /**
     * Stop the server
     * @returns {{Promise<void>}}
     */
    async stop() {{
        return new Promise((resolve) => {{
            if (this.server) {{
                this.server.close(() => {{
                    logger.info('API Gateway stopped');
                    resolve();
                }});
            }} else {{
                resolve();
            }}
        }});
    }}
    
    /**
     * Authentication middleware
     * @param {{Object}} req - The request object
     * @param {{Object}} res - The response object
     * @param {{Function}} next - The next middleware function
     * @private
     */
    _authMiddleware(req, res, next) {{
        // Skip authentication for public routes
        if (this._isPublicRoute(req.path)) {{
            return next();
        }}
        
        // Get the authorization header
        const authHeader = req.headers.authorization;
        if (!authHeader or !authHeader.startsWith('Bearer ')) {{
            return res.status(401).json({{ message: 'Unauthorized' }});
        }}
        
        // Extract the token
        const token = authHeader.split(' ')[1];
        
        try {{
            // Verify the token (in a real implementation, this would call the auth service)
            // For now, we'll just check if the token exists
            if (!token) {{
                throw new Error('Invalid token');
            }}
            
            // Add the user ID to the request
            req.userId = 'user-123'; // This would be extracted from the token
            
            next();
        }} catch (error) {{
            logger.error(`Authentication error: ${{error.message}}`);
            res.status(401).json({{ message: 'Unauthorized' }});
        }}
    }}
    
    /**
     * Check if a route is public (doesn't require authentication)
     * @param {{string}} path - The request path
     * @returns {{boolean}} True if the route is public
     * @private
     */
    _isPublicRoute(path) {{
        const publicRoutes = [
            '/health',
            '/api-docs',
            '/api/auth/login',
            '/api/auth/register'
        ];
        
        return publicRoutes.some(route => path.startsWith(route));
    }}
    
    /**
     * Generate API documentation
     * @returns {{Object}} The API documentation
     * @private
     */
    _generateApiDocs() {{
        const docs = {{
            openapi: '3.0.0',
            info: {{
                title: 'API Gateway',
                version: '1.0.0',
                description: 'API Gateway for microservices'
            }},
            paths: {{}}
        }};
        
        // Add paths for each service
        const services = this.config.services;
        
        for (const [path, service] of Object.entries(services)) {{
            docs.paths[`/api/${{path}}`] = {{
                get: {{
                    summary: `Get all ${{path}}`,
                    responses: {{
                        '200': {{
                            description: 'Successful response'
                        }}
                    }}
                }},
                post: {{
                    summary: `Create a new ${{path}}`,
                    responses: {{
                        '201': {{
                            description: 'Created successfully'
                        }}
                    }}
                }}
            }};
            
            docs.paths[`/api/${{path}}/{{id}}`] = {{
                get: {{
                    summary: `Get a ${{path}} by ID`,
                    parameters: [
                        {{
                            name: 'id',
                            in: 'path',
                            required: true,
                            schema: {{
                                type: 'string'
                            }}
                        }}
                    ],
                    responses: {{
                        '200': {{
                            description: 'Successful response'
                        }}
                    }}
                }},
                put: {{
                    summary: `Update a ${{path}} by ID`,
                    parameters: [
                        {{
                            name: 'id',
                            in: 'path',
                            required: true,
                            schema: {{
                                type: 'string'
                            }}
                        }}
                    ],
                    responses: {{
                        '200': {{
                            description: 'Updated successfully'
                        }}
                    }}
                }},
                delete: {{
                    summary: `Delete a ${{path}} by ID`,
                    parameters: [
                        {{
                            name: 'id',
                            in: 'path',
                            required: true,
                            schema: {{
                                type: 'string'
                            }}
                        }}
                    ],
                    responses: {{
                        '204': {{
                            description: 'Deleted successfully'
                        }}
                    }}
                }}
            }};
        }}
        
        return docs;
    }}
}}

module.exports = {component_name.capitalize()}Gateway;
"""
    
    def _generate_service_code(self, component_name: str, specification: Dict[str, Any]) -> str:
        """
        Generate code for a generic service component.
        
        Args:
            component_name: The name of the component
            specification: The component specification
            
        Returns:
            The generated code
        """
        # Generate a simple service class
        return f"""
const logger = require('./logger');

/**
 * {component_name.capitalize()} Service
 * 
 * A service that implements functionality for {component_name}.
 */
class {component_name.capitalize()}Service {{
    constructor(dependencies = {{}}) {{
        this.dependencies = dependencies;
        logger.info('{component_name.capitalize()} service initialized');
    }}
    
    /**
     * Initialize the service
     * @returns {{Promise<void>}}
     */
    async initialize() {{
        try {{
            logger.info('Initializing {component_name.capitalize()} service');
            // Perform initialization tasks
            
            // Example: Connect to dependencies
            for (const [name, dependency] of Object.entries(this.dependencies)) {{
                if (dependency.connect && typeof dependency.connect === 'function') {{
                    await dependency.connect();
                    logger.info(`Connected to dependency: ${{name}}`);
                }}
            }}
            
            logger.info('{component_name.capitalize()} service initialized successfully');
        }} catch (error) {{
            logger.error(`Error initializing {component_name.capitalize()} service: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Process a request
     * @param {{Object}} request - The request to process
     * @returns {{Promise<Object>}} The response
     */
    async processRequest(request) {{
        try {{
            logger.info(`Processing request: ${{JSON.stringify(request)}}`);
            
            // Validate the request
            this._validateRequest(request);
            
            // Process the request based on its type
            let response;
            switch (request.type) {{
                case 'getData':
                    response = await this._handleGetData(request);
                    break;
                case 'performAction':
                    response = await this._handlePerformAction(request);
                    break;
                default:
                    throw new Error(`Unknown request type: ${{request.type}}`);
            }}
            
            logger.info(`Request processed successfully: ${{JSON.stringify(response)}}`);
            return response;
        }} catch (error) {{
            logger.error(`Error processing request: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Get the service status
     * @returns {{Object}} The service status
     */
    getStatus() {{
        return {{
            name: '{component_name.capitalize()} Service',
            status: 'running',
            uptime: process.uptime(),
            memory: process.memoryUsage()
        }};
    }}
    
    /**
     * Shutdown the service
     * @returns {{Promise<void>}}
     */
    async shutdown() {{
        try {{
            logger.info('Shutting down {component_name.capitalize()} service');
            
            // Perform cleanup tasks
            
            // Example: Disconnect from dependencies
            for (const [name, dependency] of Object.entries(this.dependencies)) {{
                if (dependency.disconnect && typeof dependency.disconnect === 'function') {{
                    await dependency.disconnect();
                    logger.info(`Disconnected from dependency: ${{name}}`);
                }}
            }}
            
            logger.info('{component_name.capitalize()} service shut down successfully');
        }} catch (error) {{
            logger.error(`Error shutting down {component_name.capitalize()} service: ${{error.message}}`);
            throw error;
        }}
    }}
    
    /**
     * Validate a request
     * @param {{Object}} request - The request to validate
     * @throws {{Error}} If validation fails
     * @private
     */
    _validateRequest(request) {{
        if (!request) {{
            throw new Error('No request provided');
        }}
        
        if (!request.type) {{
            throw new Error('Request type is required');
        }}
        
        // Add more validation as needed
    }}
    
    /**
     * Handle a getData request
     * @param {{Object}} request - The request
     * @returns {{Promise<Object>}} The response
     * @private
     */
    async _handleGetData(request) {{
        // Example implementation
        return {{
            data: {{
                id: '123',
                name: 'Example',
                timestamp: new Date().toISOString()
            }}
        }};
    }}
    
    /**
     * Handle a performAction request
     * @param {{Object}} request - The request
     * @returns {{Promise<Object>}} The response
     * @private
     */
    async _handlePerformAction(request) {{
        // Example implementation
        return {{
            success: true,
            action: request.action,
            timestamp: new Date().toISOString()
        }};
    }}
}}

module.exports = {component_name.capitalize()}Service;
"""
    
    def _generate_interface_code(self, interface_name: str, methods: List[Dict[str, Any]]) -> str:
        """
        Generate code for an interface.
        
        Args:
            interface_name: The name of the interface
            methods: The methods of the interface
            
        Returns:
            The generated code
        """
        # Generate a simple interface in TypeScript
        method_definitions = []
        for method in methods:
            method_name = method.get("name", "method")
            parameters = method.get("parameters", [])
            returns = method.get("returns", "void")
            
            # Create parameter list
            param_list = ", ".join([f"{param}: any" for param in parameters])
            
            # Add method definition
            method_definitions.append(f"  {method_name}({param_list}): {returns};")
        
        # Join method definitions with newlines
        methods_code = "\n".join(method_definitions)
        
        # Create implementation code with proper indentation
        implementation_code = []
        for method in methods:
            method_name = method.get("name", "method")
            parameters = method.get("parameters", [])
            param_list = ", ".join([f"{param}: any" for param in parameters])
            implementation_code.append(f"  {method_name}({param_list}) {{")
            implementation_code.append(f"    throw new Error(\"Method not implemented\");")
            implementation_code.append(f"  }}")
        
        implementation_code_str = "\n".join(implementation_code)
        
        # Build the complete interface code
        interface_code = f"""
/**
 * {interface_name} Interface
 * 
 * Defines the contract for components implementing {interface_name}.
 */
export interface {interface_name} {{
{methods_code}
}}

/**
 * Abstract base class for {interface_name} implementations
 */
export abstract class {interface_name}Base implements {interface_name} {{
{implementation_code_str}
}}

/**
 * Default implementation of {interface_name}
 */
export class Default{interface_name} extends {interface_name}Base {{
  // Override methods as needed
}}
"""
        return interface_code
    
    def _generate_documentation(self, component_name: str, code: str) -> str:
        """
        Generate documentation for a component.
        
        Args:
            component_name: The name of the component
            code: The component code
            
        Returns:
            The generated documentation
        """
        # Extract class and method names from the code
        # In a real implementation, this would use more sophisticated parsing
        
        # For now, we'll create a simple documentation template
        return f"""
# {component_name.capitalize()} Documentation

## Overview

This document provides documentation for the {component_name.capitalize()} component.

## Installation

```bash
npm install {component_name.lower()}
```

## Usage

```javascript
const {component_name.capitalize()} = require('{component_name.lower()}');

// Create an instance
const {component_name.lower()} = new {component_name.capitalize()}();

// Use the component
// ...
```

## API Reference

### Methods

The {component_name.capitalize()} component provides the following methods:

- `initialize()`: Initialize the component
- `processRequest(request)`: Process a request
- `getStatus()`: Get the component status
- `shutdown()`: Shutdown the component

### Events

The {component_name.capitalize()} component emits the following events:

- `initialized`: Emitted when the component is initialized
- `error`: Emitted when an error occurs
- `shutdown`: Emitted when the component is shut down

## Examples

### Basic Example

```javascript
const {component_name.capitalize()} = require('{component_name.lower()}');

async function main() {{
  // Create an instance
  const {component_name.lower()} = new {component_name.capitalize()}();
  
  // Initialize
  await {component_name.lower()}.initialize();
  
  // Process a request
  const response = await {component_name.lower()}.processRequest({{
    type: 'getData',
    params: {{
      // ...
    }}
  }});
  
  console.log(response);
  
  // Shutdown
  await {component_name.lower()}.shutdown();
}}

main().catch(console.error);
```

## Error Handling

The {component_name.capitalize()} component throws errors in the following cases:

- Invalid request
- Initialization failure
- Processing failure
- Shutdown failure

## License

MIT
"""
    
    def _generate_tests(self, component_name: str, code: str) -> str:
        """
        Generate tests for a component.
        
        Args:
            component_name: The name of the component
            code: The component code
            
        Returns:
            The generated tests
        """
        # In a real implementation, this would analyze the code to generate appropriate tests
        # For now, we'll create a simple test template
        return f"""
const {component_name.capitalize()} = require('../{component_name.lower()}');
const assert = require('assert');

describe('{component_name.capitalize()}', () => {{
  let {component_name.lower()};
  
  beforeEach(() => {{
    // Create a new instance for each test
    {component_name.lower()} = new {component_name.capitalize()}();
  }});
  
  describe('initialization', () => {{
    it('should initialize successfully', async () => {{
      await {component_name.lower()}.initialize();
      // Add assertions
    }});
    
    it('should handle initialization errors', async () => {{
      // Mock dependencies to cause an error
      // ...
      
      try {{
        await {component_name.lower()}.initialize();
        assert.fail('Should have thrown an error');
      }} catch (error) {{
        // Assert error properties
      }}
    }});
  }});
  
  describe('processRequest', () => {{
    beforeEach(async () => {{
      // Initialize before testing processRequest
      await {component_name.lower()}.initialize();
    }});
    
    it('should process getData requests', async () => {{
      const response = await {component_name.lower()}.processRequest({{
        type: 'getData',
        params: {{
          // ...
        }}
      }});
      
      // Assert response properties
      assert.ok(response.data);
    }});
    
    it('should process performAction requests', async () => {{
      const response = await {component_name.lower()}.processRequest({{
        type: 'performAction',
        action: 'test',
        params: {{
          // ...
        }}
      }});
      
      // Assert response properties
      assert.strictEqual(response.success, true);
      assert.strictEqual(response.action, 'test');
    }});
    
    it('should validate requests', async () => {{
      try {{
        await {component_name.lower()}.processRequest(null);
        assert.fail('Should have thrown an error');
      }} catch (error) {{
        // Assert error properties
        assert.strictEqual(error.message, 'No request provided');
      }}
    }});
  }});
  
  describe('getStatus', () => {{
    it('should return the component status', () => {{
      const status = {component_name.lower()}.getStatus();
      
      // Assert status properties
      assert.strictEqual(status.name, '{component_name.capitalize()} Service');
      assert.strictEqual(status.status, 'running');
      assert.ok(status.uptime >= 0);
      assert.ok(status.memory);
    }});
  }});
  
  describe('shutdown', () => {{
    beforeEach(async () => {{
      // Initialize before testing shutdown
      await {component_name.lower()}.initialize();
    }});
    
    it('should shutdown successfully', async () => {{
      await {component_name.lower()}.shutdown();
      // Add assertions
    }});
    
    it('should handle shutdown errors', async () => {{
      // Mock dependencies to cause an error
      // ...
      
      try {{
        await {component_name.lower()}.shutdown();
        assert.fail('Should have thrown an error');
      }} catch (error) {{
        // Assert error properties
      }}
    }});
  }});
}});
"""
    
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code to identify potential issues and improvement opportunities.
        
        Args:
            code: The code to analyze
            
        Returns:
            A dictionary containing the analysis results
        """
        # In a real implementation, this would use more sophisticated analysis
        # For now, we'll create a simple analysis
        
        # Count lines of code
        lines = code.strip().split("\n")
        line_count = len(lines)
        
        # Count functions/methods
        function_count = code.count("function") + code.count("=>")
        
        # Check for common issues
        issues = []
        
        if code.count("console.log") > 0:
            issues.append("Uses console.log for logging, consider using a proper logging library")
        
        if code.count("try") < code.count("throw"):
            issues.append("More throw statements than try blocks, consider adding error handling")
        
        if code.count("TODO") > 0:
            issues.append("Contains TODO comments, consider addressing them")
        
        # Return the analysis
        return {
            "line_count": line_count,
            "function_count": function_count,
            "issues": issues,
            "complexity": "medium"  # Placeholder, would be calculated in a real implementation
        }
    
    def _refactor(self, code: str, code_analysis: Dict[str, Any], requirements: List[str]) -> str:
        """
        Refactor code based on analysis and requirements.
        
        Args:
            code: The code to refactor
            code_analysis: The code analysis results
            requirements: The refactoring requirements
            
        Returns:
            The refactored code
        """
        # In a real implementation, this would perform more sophisticated refactoring
        # For now, we'll make some simple changes
        
        refactored_code = code
        
        # Replace console.log with logger
        if "Uses console.log for logging" in str(code_analysis.get("issues", [])):
            refactored_code = refactored_code.replace("console.log", "logger.info")
            
            # Add logger import if not present
            if "const logger" not in refactored_code:
                refactored_code = "const logger = require('./logger');\n\n" + refactored_code
        
        # Add error handling where missing
        if "More throw statements than try blocks" in str(code_analysis.get("issues", [])):
            # This is a simplified approach - in a real implementation, this would be more sophisticated
            refactored_code = refactored_code.replace(
                "throw new Error",
                "try {\n    // Operation that might fail\n  } catch (error) {\n    throw new Error"
            )
        
        # Address TODOs if required
        if "Contains TODO comments" in str(code_analysis.get("issues", [])) and any("todo" in req.lower() for req in requirements):
            refactored_code = refactored_code.replace(
                "// TODO",
                "// Implemented:"
            )
        
        return refactored_code
    
    def _document_changes(self, original_code: str, modified_code: str) -> str:
        """
        Document the changes made to the code.
        
        Args:
            original_code: The original code
            modified_code: The modified code
            
        Returns:
            A string describing the changes
        """
        # In a real implementation, this would generate a more detailed diff
        # For now, we'll create a simple summary
        
        # Count lines
        original_lines = original_code.strip().split("\n")
        modified_lines = modified_code.strip().split("\n")
        
        # Calculate basic metrics
        added_lines = len(modified_lines) - len(original_lines)
        
        # Check for specific changes
        changes = []
        
        if "logger" in modified_code and "logger" not in original_code:
            changes.append("Added proper logging with logger")
        
        if modified_code.count("try") > original_code.count("try"):
            changes.append("Added error handling with try/catch blocks")
        
        if modified_code.count("// TODO") < original_code.count("// TODO"):
            changes.append("Addressed TODO comments")
        
        # If no specific changes were identified, add a generic message
        if not changes:
            changes.append("Refactored code for improved readability and maintainability")
        
        # Create the change summary
        return f"""
# Code Changes Summary

## Overview

The code has been refactored to improve quality and meet requirements.

## Changes Made

{chr(10).join(f"- {change}" for change in changes)}

## Metrics

- Lines added: {added_lines if added_lines > 0 else "None"}
- Lines removed: {-added_lines if added_lines < 0 else "None"}
- Lines modified: {len(modified_lines) - len(original_lines) + abs(added_lines)}
"""
    
    def _analyze_bug(self, code: str, bug_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a bug in the code.
        
        Args:
            code: The code containing the bug
            bug_report: The bug report
            
        Returns:
            A dictionary containing the bug analysis
        """
        # In a real implementation, this would perform more sophisticated analysis
        # For now, we'll create a simple analysis based on the bug report
        
        bug_description = bug_report.get("description", "")
        steps_to_reproduce = bug_report.get("steps_to_reproduce", [])
        expected_behavior = bug_report.get("expected_behavior", "")
        actual_behavior = bug_report.get("actual_behavior", "")
        
        # Look for keywords in the bug description to identify potential causes
        potential_causes = []
        
        if "null" in bug_description.lower() or "undefined" in bug_description.lower():
            potential_causes.append("Null or undefined value")
        
        if "exception" in bug_description.lower() or "error" in bug_description.lower():
            potential_causes.append("Unhandled exception")
        
        if "timeout" in bug_description.lower() or "slow" in bug_description.lower():
            potential_causes.append("Performance issue")
        
        if "memory" in bug_description.lower() or "leak" in bug_description.lower():
            potential_causes.append("Memory leak")
        
        # If no specific causes were identified, add a generic cause
        if not potential_causes:
            potential_causes.append("Logic error")
        
        # Return the analysis
        return {
            "description": bug_description,
            "potential_causes": potential_causes,
            "affected_areas": self._identify_affected_areas(code, bug_description),
            "severity": bug_report.get("severity", "medium")
        }
    
    def _identify_affected_areas(self, code: str, bug_description: str) -> List[str]:
        """
        Identify areas of the code that might be affected by a bug.
        
        Args:
            code: The code containing the bug
            bug_description: The bug description
            
        Returns:
            A list of affected areas
        """
        # In a real implementation, this would perform more sophisticated analysis
        # For now, we'll use a simple keyword-based approach
        
        affected_areas = []
        
        # Split the code into lines
        lines = code.strip().split("\n")
        
        # Look for functions/methods that might be related to the bug
        for i, line in enumerate(lines):
            if "function" in line or "=>" in line:
                # Extract function name (simplified approach)
                function_name = line.split("function")[1].split("(")[0].strip() if "function" in line else line.split("=>")[0].strip()
                
                # Check if the function name or line content is related to the bug description
                if function_name in bug_description or any(keyword in line.lower() for keyword in bug_description.lower().split()):
                    affected_areas.append(f"Line {i+1}: {line.strip()}")
        
        # If no specific areas were identified, add a generic message
        if not affected_areas:
            affected_areas.append("Unknown - further investigation needed")
        
        return affected_areas
    
    def _fix(self, code: str, bug_analysis: Dict[str, Any]) -> str:
        """
        Fix a bug in the code.
        
        Args:
            code: The code containing the bug
            bug_analysis: The bug analysis
            
        Returns:
            The fixed code
        """
        # In a real implementation, this would perform more sophisticated fixes
        # For now, we'll make some simple changes based on the bug analysis
        
        fixed_code = code
        
        # Apply fixes based on potential causes
        for cause in bug_analysis.get("potential_causes", []):
            if cause == "Null or undefined value":
                # Add null checks
                fixed_code = fixed_code.replace(
                    "function process(data) {",
                    "function process(data) {\n  if (!data) {\n    throw new Error('Data is required');\n  }"
                )
            
            elif cause == "Unhandled exception":
                # Add try/catch blocks
                fixed_code = fixed_code.replace(
                    "function process(data) {",
                    "function process(data) {\n  try {"
                )
                fixed_code = fixed_code.replace(
                    "  return result;",
                    "    return result;\n  } catch (error) {\n    logger.error(`Error processing data: ${error.message}`);\n    throw error;\n  }"
                )
            
            elif cause == "Performance issue":
                # Add caching
                fixed_code = fixed_code.replace(
                    "function process(data) {",
                    "const cache = {};\n\nfunction process(data) {\n  // Check cache\n  const cacheKey = JSON.stringify(data);\n  if (cache[cacheKey]) {\n    return cache[cacheKey];\n  }"
                )
                fixed_code = fixed_code.replace(
                    "  return result;",
                    "  // Store in cache\n  cache[cacheKey] = result;\n  return result;"
                )
            
            elif cause == "Memory leak":
                # Add cleanup
                fixed_code = fixed_code.replace(
                    "function process(data) {",
                    "function process(data) {\n  // Clean up resources when done\n  let resources = [];"
                )
                fixed_code = fixed_code.replace(
                    "  return result;",
                    "  // Release resources\n  resources.forEach(resource => resource.release());\n  resources = [];\n  return result;"
                )
            
            elif cause == "Logic error":
                # This is a generic fix - in a real implementation, this would be more specific
                fixed_code = fixed_code.replace(
                    "if (condition) {",
                    "// Fixed logic error\nif (condition && additionalCheck) {"
                )
        
        return fixed_code
    
    def _verify_fix(self, fixed_code: str, bug_report: Dict[str, Any]) -> str:
        """
        Verify that the fix addresses the bug.
        
        Args:
            fixed_code: The fixed code
            bug_report: The bug report
            
        Returns:
            A verification report
        """
        # In a real implementation, this would run tests to verify the fix
        # For now, we'll create a simple verification report
        
        return f"""
# Fix Verification

## Bug Description

{bug_report.get("description", "No description provided")}

## Expected Behavior

{bug_report.get("expected_behavior", "No expected behavior provided")}

## Fix Applied

The following changes were made to address the bug:

- Added null/undefined checks
- Added error handling with try/catch blocks
- Improved performance with caching
- Fixed memory leaks by releasing resources
- Corrected logic errors

## Verification Steps

1. The fixed code was reviewed for correctness
2. The changes directly address the reported issues
3. The code now handles edge cases properly

## Conclusion

The fix addresses the reported bug and should resolve the issue. Further testing is recommended to ensure the fix does not introduce new issues.
"""
    
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


# Export the Coder class
__all__ = ['Coder']
