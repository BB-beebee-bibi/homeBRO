"""
ROOcode Orchestrator Module

This module implements the Orchestrator component of the ROOcode system, which serves as the
central coordination hub for the entire multi-agent workflow. The Orchestrator manages task
queues, delegates work to specialized agents, tracks workflow state, and handles error recovery.

The Orchestrator is responsible for:
- Receiving and interpreting user requirements
- Breaking down complex tasks into subtasks
- Assigning tasks to appropriate agents (Architect, Coder, Debugger)
- Tracking progress and managing workflow state
- Handling inter-agent communication
- Managing error recovery and retries
- Providing status updates to the user
- Selecting appropriate AI models for tasks
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field

from models import ModelRegistry, ModelSelector
from config import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ROOcode.Orchestrator")


class MessageType(Enum):
    """Enumeration of message types used in the ROOcode system."""
    TASK = "task"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"


class Priority(Enum):
    """Enumeration of priority levels for tasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Enumeration of possible task statuses."""
    SUBMITTED = "submitted"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class RecoveryStrategy(Enum):
    """Enumeration of error recovery strategies."""
    RETRY = "retry"
    REASSIGN = "reassign"
    DECOMPOSE = "decompose"
    ESCALATE = "escalate"
    ROLLBACK = "rollback"


@dataclass
class Message:
    """Base class for all messages in the ROOcode system."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.TASK
    priority: Priority = Priority.MEDIUM
    content: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps({
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create a Message object from a JSON string."""
        data = json.loads(json_str)
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            message_type=MessageType(data.get("message_type", "task")),
            priority=Priority(data.get("priority", "medium")),
            content=data.get("content", {})
        )


@dataclass
class Task(Message):
    """Represents a task to be executed by an agent."""
    def __init__(self, 
                 task_id: str = None,
                 task_type: str = "",
                 payload: Dict[str, Any] = None,
                 metadata: Dict[str, Any] = None,
                 deadline: str = None,
                 parent_id: str = None,
                 **kwargs):
        super().__init__(message_type=MessageType.TASK, **kwargs)
        
        # Initialize task-specific content
        self.content["task_id"] = task_id or str(uuid.uuid4())
        self.content["task_type"] = task_type
        self.content["payload"] = payload or {}
        self.content["metadata"] = metadata or {}
        
        if deadline:
            self.content["deadline"] = deadline
            
        if parent_id:
            self.content["parent_id"] = parent_id


@dataclass
class Response(Message):
    """Represents a response from an agent after executing a task."""
    def __init__(self, 
                 task_id: str,
                 status: str = "completed",
                 result: Dict[str, Any] = None,
                 **kwargs):
        super().__init__(message_type=MessageType.RESPONSE, **kwargs)
        
        # Initialize response-specific content
        self.content["task_id"] = task_id
        self.content["status"] = status
        self.content["result"] = result or {}


@dataclass
class StatusUpdate(Message):
    """Represents a status update for a task in progress."""
    def __init__(self, 
                 task_id: str,
                 progress: int = 0,
                 stage: str = "",
                 estimated_completion: str = None,
                 **kwargs):
        super().__init__(message_type=MessageType.STATUS, **kwargs)
        
        # Initialize status-specific content
        self.content["task_id"] = task_id
        self.content["progress"] = progress
        self.content["stage"] = stage
        
        if estimated_completion:
            self.content["estimated_completion"] = estimated_completion


@dataclass
class ErrorMessage(Message):
    """Represents an error that occurred during task execution."""
    def __init__(self, 
                 task_id: str,
                 error_code: str = "",
                 severity: ErrorSeverity = ErrorSeverity.WARNING,
                 description: str = "",
                 context: Dict[str, Any] = None,
                 recovery_suggestion: str = "",
                 **kwargs):
        super().__init__(message_type=MessageType.ERROR, **kwargs)
        
        # Initialize error-specific content
        self.content["task_id"] = task_id
        self.content["error_code"] = error_code
        self.content["severity"] = severity.value
        self.content["description"] = description
        self.content["context"] = context or {}
        self.content["recovery_suggestion"] = recovery_suggestion


class TaskQueue:
    """
    A priority queue for tasks with additional functionality for task management.
    
    This queue organizes tasks by priority and provides methods for adding, retrieving,
    and managing tasks in the queue.
    """
    
    def __init__(self):
        """Initialize the task queue with separate queues for each priority level."""
        self._queues = {
            Priority.HIGH: asyncio.Queue(),
            Priority.MEDIUM: asyncio.Queue(),
            Priority.LOW: asyncio.Queue()
        }
        self._task_lookup = {}  # Maps task_id to (priority, position) for quick lookups
    
    async def put(self, task: Task) -> None:
        """
        Add a task to the queue based on its priority.
        
        Args:
            task: The task to add to the queue
        """
        priority = task.priority
        await self._queues[priority].put(task)
        self._task_lookup[task.content["task_id"]] = priority
        logger.debug(f"Task {task.content['task_id']} added to {priority.value} priority queue")
    
    async def get(self) -> Optional[Task]:
        """
        Get the next task from the queue, respecting priority order.
        
        Returns:
            The next task to process, or None if all queues are empty
        """
        # Check queues in priority order
        for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            if not self._queues[priority].empty():
                task = await self._queues[priority].get()
                if task.content["task_id"] in self._task_lookup:
                    del self._task_lookup[task.content["task_id"]]
                logger.debug(f"Task {task.content['task_id']} retrieved from {priority.value} priority queue")
                return task
        
        return None
    
    def empty(self) -> bool:
        """
        Check if all queues are empty.
        
        Returns:
            True if all queues are empty, False otherwise
        """
        return all(queue.empty() for queue in self._queues.values())
    
    async def remove(self, task_id: str) -> bool:
        """
        Remove a specific task from the queue.
        
        Args:
            task_id: The ID of the task to remove
            
        Returns:
            True if the task was found and removed, False otherwise
        """
        if task_id not in self._task_lookup:
            return False
        
        # This is a simplified implementation - in a real system, you would need
        # to actually remove the task from the underlying queue, which is not
        # directly supported by asyncio.Queue. A more complete implementation
        # would use a custom queue implementation.
        logger.debug(f"Task {task_id} marked for removal")
        self._task_lookup[task_id] = None  # Mark as removed
        return True
    
    def get_task_count(self) -> Dict[str, int]:
        """
        Get the number of tasks in each priority queue.
        
        Returns:
            A dictionary with the count of tasks in each priority queue
        """
        return {
            priority.value: queue.qsize() 
            for priority, queue in self._queues.items()
        }


class WorkflowState:
    """
    Manages the state of workflows and their constituent tasks.
    
    This class tracks the status of all workflows and their subtasks,
    providing methods to update and query workflow state.
    """
    
    def __init__(self):
        """Initialize the workflow state tracker."""
        self._workflows = {}  # workflow_id -> workflow state
        self._task_to_workflow = {}  # task_id -> workflow_id
    
    def create_workflow(self, workflow_id: str, metadata: Dict[str, Any] = None) -> None:
        """
        Create a new workflow with the given ID.
        
        Args:
            workflow_id: The unique identifier for the workflow
            metadata: Optional metadata associated with the workflow
        """
        if workflow_id in self._workflows:
            raise ValueError(f"Workflow {workflow_id} already exists")
        
        self._workflows[workflow_id] = {
            "status": TaskStatus.SUBMITTED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "subtasks": [],
            "results": {},
            "metadata": metadata or {}
        }
        logger.info(f"Created new workflow: {workflow_id}")
    
    def add_task_to_workflow(self, workflow_id: str, task_id: str) -> None:
        """
        Add a task to a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            task_id: The ID of the task to add
        """
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow {workflow_id} does not exist")
        
        self._workflows[workflow_id]["subtasks"].append(task_id)
        self._workflows[workflow_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._task_to_workflow[task_id] = workflow_id
        logger.debug(f"Added task {task_id} to workflow {workflow_id}")
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Dict[str, Any] = None) -> None:
        """
        Update the status of a task within a workflow.
        
        Args:
            task_id: The ID of the task
            status: The new status of the task
            result: Optional result data from the task
        """
        if task_id not in self._task_to_workflow:
            logger.warning(f"Task {task_id} not associated with any workflow")
            return
        
        workflow_id = self._task_to_workflow[task_id]
        self._workflows[workflow_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        if result:
            self._workflows[workflow_id]["results"][task_id] = result
        
        # Check if all subtasks are complete
        if self._all_subtasks_complete(workflow_id):
            if self._all_subtasks_successful(workflow_id):
                self._workflows[workflow_id]["status"] = TaskStatus.COMPLETED.value
                logger.info(f"Workflow {workflow_id} completed successfully")
            else:
                self._workflows[workflow_id]["status"] = TaskStatus.FAILED.value
                logger.warning(f"Workflow {workflow_id} failed due to subtask failures")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            A dictionary containing the workflow state
        """
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow {workflow_id} does not exist")
        
        return self._workflows[workflow_id]
    
    def get_task_workflow(self, task_id: str) -> Optional[str]:
        """
        Get the workflow ID associated with a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            The workflow ID, or None if the task is not associated with any workflow
        """
        return self._task_to_workflow.get(task_id)
    
    def _all_subtasks_complete(self, workflow_id: str) -> bool:
        """
        Check if all subtasks in a workflow are complete.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            True if all subtasks are complete, False otherwise
        """
        workflow = self._workflows[workflow_id]
        return all(
            task_id in workflow["results"] 
            for task_id in workflow["subtasks"]
        )
    
    def _all_subtasks_successful(self, workflow_id: str) -> bool:
        """
        Check if all subtasks in a workflow completed successfully.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            True if all subtasks completed successfully, False otherwise
        """
        workflow = self._workflows[workflow_id]
        return all(
            workflow["results"].get(task_id, {}).get("status") == "completed"
            for task_id in workflow["subtasks"]
        )


class Orchestrator:
    """
    The central coordination component of the ROOcode system.
    
    The Orchestrator is responsible for managing workflows, delegating tasks to specialized
    agents, tracking progress, and handling errors. It serves as the communication hub
    between all components of the system. It also manages model selection for tasks.
    """
    
    def __init__(self):
        """Initialize the Orchestrator with required components and state tracking."""
        self.task_queue = TaskQueue()
        self.workflow_state = WorkflowState()
        
        # Communication channels (queues)
        self.response_queue = asyncio.Queue()
        self.status_queue = asyncio.Queue()
        self.error_queue = asyncio.Queue()
        
        # Agent registry - will be populated with actual agent instances
        self.agents = {
            'architect': None,  # Will be set when agents are registered
            'coder': None,
            'debugger': None
        }
        
        # Error handling configuration
        self.max_retries = 3
        self.retry_delays = [5, 15, 30]  # Seconds to wait before retry attempts
        
        # Callback registry for event handling
        self.callbacks = {
            'on_task_complete': [],
            'on_task_failed': [],
            'on_workflow_complete': [],
            'on_workflow_failed': [],
            'on_error': []
        }
        
        # Initialize model registry and selector
        default_model = config.get("model.default", "Claude-3.7-Sonnet")
        self.model_registry = ModelRegistry(default_model=default_model)
        self.model_selector = ModelSelector(self.model_registry)
        
        logger.info(f"Orchestrator initialized with default model: {default_model}")
    
    def register_agent(self, agent_type: str, agent_instance: Any) -> None:
        """
        Register an agent with the Orchestrator.
        
        Args:
            agent_type: The type of agent (architect, coder, debugger, etc.)
            agent_instance: The agent instance to register
        """
        if agent_type not in self.agents:
            self.agents[agent_type] = agent_instance
            logger.info(f"Registered agent: {agent_type}")
        else:
            logger.warning(f"Agent type {agent_type} already registered, replacing")
            self.agents[agent_type] = agent_instance
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: The type of event to register for
            callback: The function to call when the event occurs
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            logger.debug(f"Registered callback for event: {event_type}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    async def submit_task(self, task_description: Dict[str, Any], priority: Priority = Priority.MEDIUM) -> str:
        """
        Submit a new task to the Orchestrator.
        
        Args:
            task_description: A dictionary describing the task
            priority: The priority level for the task
            
        Returns:
            The ID of the created workflow
        """
        # Generate IDs
        workflow_id = str(uuid.uuid4())
        
        # Create workflow
        self.workflow_state.create_workflow(workflow_id, metadata=task_description.get("metadata"))
        
        # Break down the task into subtasks
        subtasks = self._break_down_task(task_description, workflow_id)
        
        # Add subtasks to the workflow and queue
        for subtask in subtasks:
            task = Task(
                task_id=subtask["task_id"],
                task_type=subtask["task_type"],
                payload=subtask["payload"],
                metadata=subtask.get("metadata"),
                parent_id=workflow_id,
                priority=priority,
                sender="orchestrator"
            )
            
            self.workflow_state.add_task_to_workflow(workflow_id, subtask["task_id"])
            await self.task_queue.put(task)
        
        logger.info(f"Submitted new workflow {workflow_id} with {len(subtasks)} subtasks")
        return workflow_id
    
    async def process_tasks(self) -> None:
        """
        Process tasks from the queue until it's empty.
        
        This method continuously retrieves tasks from the queue and delegates them
        to the appropriate agents for execution.
        """
        while not self.task_queue.empty():
            # Get the next task
            task = await self.task_queue.get()
            if not task:
                continue
            
            task_id = task.content["task_id"]
            task_type = task.content["task_type"]
            
            # Determine which agent should handle this task
            agent_type = self._determine_agent_type(task_type)
            if not agent_type or agent_type not in self.agents or not self.agents[agent_type]:
                error_msg = f"No agent available to handle task type: {task_type}"
                logger.error(error_msg)
                await self._handle_error(task, error_msg)
                continue
            
            # Execute the task
            try:
                logger.info(f"Executing task {task_id} of type {task_type} with agent {agent_type}")
                result = await self._execute_task(self.agents[agent_type], task)
                await self._handle_result(task, result)
            except Exception as e:
                logger.error(f"Error executing task {task_id}: {str(e)}")
                await self._handle_error(task, str(e))
    
    async def run(self) -> None:
        """
        Run the main orchestration loop.
        
        This method starts the main processing loops for tasks, responses, and errors.
        It runs indefinitely until explicitly stopped.
        """
        # Create tasks for processing different queues
        tasks = [
            self._process_task_loop(),
            self._process_response_loop(),
            self._process_error_loop()
        ]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    
    async def _process_task_loop(self) -> None:
        """Process tasks from the queue in a continuous loop."""
        while True:
            await self.process_tasks()
            await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning
    
    async def _process_response_loop(self) -> None:
        """Process responses from agents in a continuous loop."""
        while True:
            if not self.response_queue.empty():
                response = await self.response_queue.get()
                await self._handle_response(response)
            await asyncio.sleep(0.1)
    
    async def _process_error_loop(self) -> None:
        """Process errors in a continuous loop."""
        while True:
            if not self.error_queue.empty():
                error = await self.error_queue.get()
                await self._handle_error_message(error)
            await asyncio.sleep(0.1)
    
    async def _execute_task(self, agent: Any, task: Task) -> Dict[str, Any]:
        """
        Execute a task using the specified agent with the appropriate model.
        
        Args:
            agent: The agent to execute the task
            task: The task to execute
            
        Returns:
            The result of the task execution
        """
        # Select the appropriate model for this task
        task_dict = {
            "task_type": task.content.get("task_type", ""),
            "requirements": task.content.get("payload", {}).get("requirements", []),
            "constraints": task.content.get("payload", {}).get("constraints", []),
        }
        
        # Check if a specific model is requested in the task
        if "model" in task.content:
            task_dict["model"] = task.content["model"]
        
        # Use auto-selection if enabled in config, otherwise use default model
        if config.get("model.auto_select", True):
            selected_model = self.model_selector.select_model(task_dict)
        else:
            selected_model = self.model_registry.default_model
        
        # Add the selected model to the task payload
        if "payload" not in task.content:
            task.content["payload"] = {}
        
        task.content["payload"]["model"] = selected_model
        
        logger.info(f"Executing task {task.content['task_id']} with model: {selected_model}")
        
        # Execute the task with the selected model
        return await agent.execute_task(task)
    
    async def _handle_result(self, task: Task, result: Dict[str, Any]) -> None:
        """
        Handle the result of a completed task.
        
        Args:
            task: The task that was executed
            result: The result of the task execution
        """
        task_id = task.content["task_id"]
        workflow_id = task.content.get("parent_id")
        
        if not workflow_id:
            logger.warning(f"Task {task_id} has no associated workflow")
            return
        
        # Update workflow state
        self.workflow_state.update_task_status(
            task_id, 
            TaskStatus.COMPLETED, 
            result
        )
        
        # Check if this completion triggers any callbacks
        for callback in self.callbacks['on_task_complete']:
            callback(task_id, result)
        
        # Check if the workflow is complete
        workflow_status = self.workflow_state.get_workflow_status(workflow_id)
        if workflow_status["status"] == TaskStatus.COMPLETED.value:
            logger.info(f"Workflow {workflow_id} completed")
            for callback in self.callbacks['on_workflow_complete']:
                callback(workflow_id, workflow_status)
    
    async def _handle_response(self, response: Response) -> None:
        """
        Handle a response message from an agent.
        
        Args:
            response: The response message
        """
        task_id = response.content["task_id"]
        status = response.content["status"]
        result = response.content.get("result", {})
        
        workflow_id = self.workflow_state.get_task_workflow(task_id)
        if not workflow_id:
            logger.warning(f"Response for unknown task: {task_id}")
            return
        
        if status == "completed":
            self.workflow_state.update_task_status(task_id, TaskStatus.COMPLETED, result)
            for callback in self.callbacks['on_task_complete']:
                callback(task_id, result)
        elif status == "failed":
            self.workflow_state.update_task_status(task_id, TaskStatus.FAILED, result)
            for callback in self.callbacks['on_task_failed']:
                callback(task_id, result)
            
            # Determine recovery strategy
            recovery_strategy = self._determine_recovery_strategy(task_id, result)
            await self._apply_recovery_strategy(task_id, recovery_strategy, result)
    
    async def _handle_error(self, task: Task, error_message: str) -> None:
        """
        Handle an error that occurred during task execution.
        
        Args:
            task: The task that failed
            error_message: The error message
        """
        task_id = task.content["task_id"]
        workflow_id = task.content.get("parent_id")
        
        if not workflow_id:
            logger.warning(f"Task {task_id} has no associated workflow")
            return
        
        # Create an error message
        error = ErrorMessage(
            task_id=task_id,
            error_code="execution_error",
            severity=ErrorSeverity.WARNING,
            description=error_message,
            context={"task": task.content},
            recovery_suggestion="Retry the task",
            sender="orchestrator"
        )
        
        # Add to error queue
        await self.error_queue.put(error)
        
        # Update workflow state
        self.workflow_state.update_task_status(
            task_id, 
            TaskStatus.FAILED, 
            {"error": error_message}
        )
        
        # Trigger callbacks
        for callback in self.callbacks['on_task_failed']:
            callback(task_id, {"error": error_message})
        
        # Determine and apply recovery strategy
        recovery_strategy = self._determine_recovery_strategy(task_id, {"error": error_message})
        await self._apply_recovery_strategy(task_id, recovery_strategy, {"error": error_message})
    
    async def _handle_error_message(self, error: ErrorMessage) -> None:
        """
        Handle an error message from the error queue.
        
        Args:
            error: The error message
        """
        task_id = error.content["task_id"]
        severity = error.content["severity"]
        description = error.content["description"]
        
        logger.error(f"Error in task {task_id}: {description} (Severity: {severity})")
        
        # Trigger callbacks
        for callback in self.callbacks['on_error']:
            callback(task_id, error.content)
        
        # For critical errors, we might want to take special action
        if severity == ErrorSeverity.CRITICAL.value:
            workflow_id = self.workflow_state.get_task_workflow(task_id)
            if workflow_id:
                logger.critical(f"Critical error in workflow {workflow_id}, escalating")
                # Implement escalation logic here
    
    def _determine_agent_type(self, task_type: str) -> Optional[str]:
        """
        Determine which agent should handle a specific task type.
        
        Args:
            task_type: The type of task
            
        Returns:
            The type of agent that should handle the task, or None if no agent is suitable
        """
        # This is a simplified mapping - in a real system, this would be more sophisticated
        task_to_agent_mapping = {
            # Architect tasks
            "system_design": "architect",
            "component_design": "architect",
            "interface_design": "architect",
            "analyze_requirements": "architect",
            
            # Coder tasks
            "implement_component": "coder",
            "implement_interface": "coder",
            "refactor_code": "coder",
            "fix_bug": "coder",
            
            # Debugger tasks
            "test_component": "debugger",
            "validate_interface": "debugger",
            "performance_test": "debugger"
        }
        
        return task_to_agent_mapping.get(task_type)
    
    def _determine_recovery_strategy(self, task_id: str, error_info: Dict[str, Any]) -> RecoveryStrategy:
        """
        Determine the appropriate recovery strategy for a failed task.
        
        Args:
            task_id: The ID of the failed task
            error_info: Information about the error
            
        Returns:
            The recovery strategy to apply
        """
        # This is a simplified implementation - in a real system, this would be more sophisticated
        # and would take into account the nature of the error, the task type, and the workflow state
        
        # Get retry count from workflow state
        workflow_id = self.workflow_state.get_task_workflow(task_id)
        if not workflow_id:
            return RecoveryStrategy.ESCALATE
        
        workflow = self.workflow_state.get_workflow_status(workflow_id)
        retry_count = workflow.get("metadata", {}).get("retry_count", {}).get(task_id, 0)
        
        # Check if we've exceeded max retries
        if retry_count >= self.max_retries:
            # If we've tried retrying too many times, try decomposing the task
            return RecoveryStrategy.DECOMPOSE
        
        # Otherwise, retry the task
        return RecoveryStrategy.RETRY
    
    async def _apply_recovery_strategy(self, task_id: str, strategy: RecoveryStrategy, error_info: Dict[str, Any]) -> None:
        """
        Apply a recovery strategy to a failed task.
        
        Args:
            task_id: The ID of the failed task
            strategy: The recovery strategy to apply
            error_info: Information about the error
        """
        workflow_id = self.workflow_state.get_task_workflow(task_id)
        if not workflow_id:
            logger.warning(f"Cannot apply recovery strategy for task {task_id}: no associated workflow")
            return
        
        workflow = self.workflow_state.get_workflow_status(workflow_id)
        
        if strategy == RecoveryStrategy.RETRY:
            # Increment retry count
            retry_count = workflow.get("metadata", {}).get("retry_count", {}).get(task_id, 0)
            if "retry_count" not in workflow.get("metadata", {}):
                workflow["metadata"]["retry_count"] = {}
            workflow["metadata"]["retry_count"][task_id] = retry_count + 1
            
            # Get the original task and requeue it
            original_task = None
            for subtask_id in workflow["subtasks"]:
                if subtask_id == task_id:
                    # Recreate the task - in a real implementation, we would store the original task
                    original_task = Task(
                        task_id=task_id,
                        task_type=workflow["metadata"].get("task_type", "unknown"),
                        payload=workflow["metadata"].get("payload", {}),
                        parent_id=workflow_id,
                        sender="orchestrator"
                    )
                    break
            
            if original_task:
                logger.info(f"Retrying task {task_id} (attempt {retry_count + 1})")
                await self.task_queue.put(original_task)
            else:
                logger.warning(f"Cannot retry task {task_id}: original task not found")
        
        elif strategy == RecoveryStrategy.DECOMPOSE:
            logger.info(f"Decomposing task {task_id}")
            # In a real implementation, this would break down the task into smaller subtasks
            # For now, we'll just log that we would decompose the task
            logger.info(f"Task decomposition not implemented yet")
        
        elif strategy == RecoveryStrategy.ESCALATE:
            logger.warning(f"Escalating task {task_id} for human intervention")
            # In a real implementation, this would trigger some form of human intervention
            # For now, we'll just log that we would escalate the task
            logger.warning(f"Task escalation not implemented yet")
    
    def _break_down_task(self, task_description: Dict[str, Any], workflow_id: str) -> List[Dict[str, Any]]:
        """
        Break down a complex task into subtasks.
        
        Args:
            task_description: The description of the task to break down
            workflow_id: The ID of the workflow
            
        Returns:
            A list of subtask descriptions
        """
        # This is a simplified implementation - in a real system, this would be more sophisticated
        # and would depend on the nature of the task
        
        task_type = task_description.get("task_type", "")
        
        if task_type == "implement_system":
            # Break down into design, implementation, and testing
            return [
                {
                    "task_id": str(uuid.uuid4()),
                    "task_type": "system_design",
                    "payload": {
                        "requirements": task_description.get("requirements", []),
                        "constraints": task_description.get("constraints", [])
                    },
                    "metadata": {
                        "stage": "design",
                        "parent_task": task_description.get("task_id")
                    }
                },
                {
                    "task_id": str(uuid.uuid4()),
                    "task_type": "implement_component",
                    "payload": {
                        "component_name": "main",
                        "requirements": task_description.get("requirements", [])
                    },
                    "metadata": {
                        "stage": "implementation",
                        "parent_task": task_description.get("task_id")
                    }
                },
                {
                    "task_id": str(uuid.uuid4()),
                    "task_type": "test_component",
                    "payload": {
                        "component_name": "main",
                        "requirements": task_description.get("requirements", [])
                    },
                    "metadata": {
                        "stage": "testing",
                        "parent_task": task_description.get("task_id")
                    }
                }
            ]
        else:
            # For other task types, just create a single subtask
            return [
                {
                    "task_id": str(uuid.uuid4()),
                    "task_type": task_type,
                    "payload": task_description.get("payload", {}),
                    "metadata": {
                        "parent_task": task_description.get("task_id")
                    }
                }
            ]
    
    async def broadcast_message(self, message: Message) -> None:
        """
        Broadcast a message to all registered agents.
        
        Args:
            message: The message to broadcast
        """
        for agent_type, agent in self.agents.items():
            if agent:
                # In a real implementation, this would use the agent's interface to send the message
                logger.debug(f"Broadcasting message to {agent_type}")
                # await agent.receive_message(message)
    
    async def send_message(self, recipient: str, message: Message) -> None:
        """
        Send a message to a specific agent.
        
        Args:
            recipient: The type of agent to send the message to
            message: The message to send
        """
        if recipient in self.agents and self.agents[recipient]:
            # In a real implementation, this would use the agent's interface to send the message
            logger.debug(f"Sending message to {recipient}")
            message.recipient = recipient
            # await self.agents[recipient].receive_message(message)
        else:
            logger.warning(f"Cannot send message to unknown agent: {recipient}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            A dictionary containing the workflow state
        """
        return self.workflow_state.get_workflow_status(workflow_id)
    
    def get_queue_status(self) -> Dict[str, int]:
        """
        Get the current status of all task queues.
        
        Returns:
            A dictionary with the count of tasks in each queue
        """
        return {
            "task_queue": self.task_queue.get_task_count(),
            "response_queue": self.response_queue.qsize(),
            "status_queue": self.status_queue.qsize(),
            "error_queue": self.error_queue.qsize()
        }
    
    def set_default_model(self, model_name: str) -> bool:
        """
        Set the default model for the system.
        
        Args:
            model_name: The name of the model to set as default
            
        Returns:
            True if successful, False if the model is not registered
        """
        success = self.model_registry.set_default_model(model_name)
        if success:
            # Update the configuration
            config.set("model.default", model_name)
            logger.info(f"Default model set to: {model_name}")
        return success
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of all available models.
        
        Returns:
            A list of model names
        """
        return self.model_registry.list_models()
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            The model information, or None if the model is not registered
        """
        return self.model_registry.get_model(model_name)
    
    async def shutdown(self) -> None:
        """
        Gracefully shut down the Orchestrator.
        
        This method ensures that all tasks are properly saved and resources are released.
        """
        logger.info("Shutting down Orchestrator")
        # In a real implementation, this would save state, close connections, etc.


# Example usage
async def main():
    """Example usage of the Orchestrator."""
    orchestrator = Orchestrator()
    
    # Register mock agents (in a real implementation, these would be actual agent instances)
    class MockAgent:
        async def execute_task(self, task):
            return {"status": "completed", "result": f"Executed {task.content['task_type']}"}
    
    orchestrator.register_agent("architect", MockAgent())
    orchestrator.register_agent("coder", MockAgent())
    orchestrator.register_agent("debugger", MockAgent())
    
    # Submit a task
    workflow_id = await orchestrator.submit_task({
        "task_type": "implement_system",
        "requirements": ["req1", "req2"],
        "constraints": ["constraint1"]
    })
    
    # Process tasks
    await orchestrator.process_tasks()
    
    # Get workflow status
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow status: {status}")
    
    # Shutdown
    await orchestrator.shutdown()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
