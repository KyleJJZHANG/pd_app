"""
CrewAI Manager for Duck Therapy System

Orchestrates multi-agent workflows with intelligent LLM routing and task execution.
Configured via YAML for maximum flexibility.
"""
from typing import Dict, Any, List, Optional, Type
import asyncio
import time
from datetime import datetime
from enum import Enum

from crewai import Crew, Process
from pydantic import BaseModel
from loguru import logger

from ..agents.base_agent import BaseAgent, BaseAgentInput, BaseAgentOutput
from ..agents.listener_agent import ListenerAgent, ListenerInput
from ..agents.duck_style_agent import DuckStyleAgent, DuckStyleInput
from ..utils.config_loader import config_loader
from ..services.llm_service import llm_service


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class TaskResult(BaseModel):
    """Individual task execution result."""
    task_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int
    agent_used: str
    llm_provider_used: Optional[str] = None


class WorkflowResult(BaseModel):
    """Complete workflow execution result."""
    workflow_name: str
    status: WorkflowStatus
    task_results: List[TaskResult]
    total_execution_time_ms: int
    success_rate: float
    final_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CrewManager:
    """Manager for CrewAI multi-agent workflows."""
    
    def __init__(self):
        """Initialize CrewManager with agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.crews: Dict[str, Crew] = {}
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info("CrewManager initialized successfully")
    
    def _initialize_agents(self):
        """Initialize all available agents."""
        try:
            # Initialize listener agent
            self.agents["listener_agent"] = ListenerAgent()
            logger.info("ListenerAgent initialized")
            
            # Initialize duck style agent
            self.agents["duck_style_agent"] = DuckStyleAgent()
            logger.info("DuckStyleAgent initialized")
            
            # TODO: Add other agents as they're implemented
            # self.agents["content_recall_agent"] = ContentRecallAgent()
            # self.agents["therapy_tips_agent"] = TherapyTipsAgent()
            # self.agents["report_agent"] = ReportAgent()
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        input_data: Dict[str, Any],
        session_id: str
    ) -> WorkflowResult:
        """
        Execute a complete workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            input_data: Input data for the workflow
            session_id: Session identifier
            
        Returns:
            Workflow execution result
        """
        start_time = time.time()
        
        try:
            # Get workflow configuration
            workflow_config = config_loader.get_workflow(workflow_name)
            if not workflow_config:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            logger.info(f"Starting workflow: {workflow_name}")
            
            # Execute workflow steps
            if workflow_name == "basic_chat_flow":
                result = await self._execute_basic_chat_flow(input_data, session_id)
            elif workflow_name == "enhanced_chat_flow":
                result = await self._execute_enhanced_chat_flow(input_data, session_id)
            elif workflow_name == "daily_report_flow":
                result = await self._execute_daily_report_flow(input_data, session_id)
            else:
                # Generic workflow execution
                result = await self._execute_generic_workflow(workflow_config, input_data, session_id)
            
            # Calculate execution metrics
            total_time = int((time.time() - start_time) * 1000)
            success_count = sum(1 for task in result.task_results if task.success)
            success_rate = success_count / len(result.task_results) if result.task_results else 0
            
            # Update result with metrics
            result.total_execution_time_ms = total_time
            result.success_rate = success_rate
            
            # Determine final status
            if success_rate == 1.0:
                result.status = WorkflowStatus.COMPLETED
            elif success_rate > 0.5:
                result.status = WorkflowStatus.PARTIALLY_COMPLETED
            else:
                result.status = WorkflowStatus.FAILED
            
            logger.info(f"Workflow {workflow_name} completed with {success_rate:.2%} success rate")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return WorkflowResult(
                workflow_name=workflow_name,
                status=WorkflowStatus.FAILED,
                task_results=[],
                total_execution_time_ms=int((time.time() - start_time) * 1000),
                success_rate=0.0,
                error=str(e)
            )
    
    async def _execute_basic_chat_flow(
        self, 
        input_data: Dict[str, Any], 
        session_id: str
    ) -> WorkflowResult:
        """Execute basic chat workflow: emotion analysis → duck response."""
        task_results = []
        
        # Step 1: Emotion Analysis
        emotion_task_result = await self._execute_task(
            task_name="emotion_analysis",
            agent_name="listener_agent",
            input_data=ListenerInput(
                session_id=session_id,
                timestamp=datetime.now(),
                text=input_data.get("user_message", ""),
                context=input_data.get("context", []),
                analysis_depth=input_data.get("analysis_depth", "standard")
            )
        )
        task_results.append(emotion_task_result)
        
        # Step 2: Duck Response Generation (depends on emotion analysis)
        duck_input_data = {
            "user_message": input_data.get("user_message", ""),
            "emotion_analysis": emotion_task_result.data if emotion_task_result.success else {},
            "response_style": input_data.get("response_style", "standard")
        }
        
        duck_task_result = await self._execute_task(
            task_name="duck_response_generation",
            agent_name="duck_style_agent",
            input_data=DuckStyleInput(
                session_id=session_id,
                timestamp=datetime.now(),
                **duck_input_data
            )
        )
        task_results.append(duck_task_result)
        
        # Prepare final output
        final_output = None
        if duck_task_result.success:
            final_output = {
                "response_text": duck_task_result.data.get("text", ""),
                "emotion_analysis": emotion_task_result.data if emotion_task_result.success else None,
                "workflow_type": "basic_chat"
            }
        
        return WorkflowResult(
            workflow_name="basic_chat_flow",
            status=WorkflowStatus.RUNNING,  # Will be updated by caller
            task_results=task_results,
            total_execution_time_ms=0,  # Will be updated by caller
            success_rate=0.0,  # Will be updated by caller
            final_output=final_output
        )
    
    async def _execute_enhanced_chat_flow(
        self, 
        input_data: Dict[str, Any], 
        session_id: str
    ) -> WorkflowResult:
        """Execute enhanced chat workflow with content recommendation and therapy suggestions."""
        task_results = []
        
        # Step 1: Emotion Analysis (required)
        emotion_task_result = await self._execute_task(
            task_name="emotion_analysis",
            agent_name="listener_agent",
            input_data=ListenerInput(
                session_id=session_id,
                timestamp=datetime.now(),
                text=input_data.get("user_message", ""),
                context=input_data.get("context", []),
                analysis_depth=input_data.get("analysis_depth", "standard")
            )
        )
        task_results.append(emotion_task_result)
        
        # Parallel tasks (content recommendation and therapy suggestions)
        parallel_tasks = []
        
        # Content recommendation (optional)
        if emotion_task_result.success:
            content_task = self._execute_task(
                task_name="content_recommendation",
                agent_name="content_recall_agent",  # TODO: Implement this agent
                input_data={
                    "session_id": session_id,
                    "timestamp": datetime.now(),
                    "emotion_analysis": emotion_task_result.data,
                    "user_preferences": input_data.get("user_preferences", {}),
                    "recent_content": input_data.get("recent_content", [])
                }
            )
            parallel_tasks.append(content_task)
        
        # Therapy suggestions (conditional)
        emotion_data = emotion_task_result.data if emotion_task_result.success else {}
        emotion_intensity = emotion_data.get("intensity", 0)
        if emotion_intensity > 0.6:
            therapy_task = self._execute_task(
                task_name="therapy_suggestion",
                agent_name="therapy_tips_agent",  # TODO: Implement this agent
                input_data={
                    "session_id": session_id,
                    "timestamp": datetime.now(),
                    "emotion_analysis": emotion_data,
                    "urgency_level": emotion_data.get("urgency_level", 1),
                    "user_history": input_data.get("user_history", [])
                }
            )
            parallel_tasks.append(therapy_task)
        
        # Execute parallel tasks
        if parallel_tasks:
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            for result in parallel_results:
                if isinstance(result, TaskResult):
                    task_results.append(result)
                else:
                    logger.error(f"Parallel task failed: {result}")
        
        # Final step: Duck Response Generation
        duck_input_data = {
            "user_message": input_data.get("user_message", ""),
            "emotion_analysis": emotion_task_result.data if emotion_task_result.success else {},
            "content_recommendations": None,  # TODO: Extract from content task result
            "therapy_suggestions": None,  # TODO: Extract from therapy task result
            "response_style": input_data.get("response_style", "standard")
        }
        
        duck_task_result = await self._execute_task(
            task_name="duck_response_generation",
            agent_name="duck_style_agent",
            input_data=DuckStyleInput(
                session_id=session_id,
                timestamp=datetime.now(),
                **duck_input_data
            )
        )
        task_results.append(duck_task_result)
        
        # Prepare final output
        final_output = None
        if duck_task_result.success:
            final_output = {
                "response_text": duck_task_result.data.get("text", ""),
                "emotion_analysis": emotion_task_result.data if emotion_task_result.success else None,
                "content_recommendations": None,  # TODO: Add when content agent is implemented
                "therapy_suggestions": None,  # TODO: Add when therapy agent is implemented
                "workflow_type": "enhanced_chat"
            }
        
        return WorkflowResult(
            workflow_name="enhanced_chat_flow",
            status=WorkflowStatus.RUNNING,
            task_results=task_results,
            total_execution_time_ms=0,
            success_rate=0.0,
            final_output=final_output
        )
    
    async def _execute_daily_report_flow(
        self, 
        input_data: Dict[str, Any], 
        session_id: str
    ) -> WorkflowResult:
        """Execute daily report generation workflow."""
        task_results = []
        
        # TODO: Implement when report agent is available
        logger.warning("Daily report flow not yet implemented - report agent required")
        
        return WorkflowResult(
            workflow_name="daily_report_flow",
            status=WorkflowStatus.FAILED,
            task_results=task_results,
            total_execution_time_ms=0,
            success_rate=0.0,
            error="Report agent not yet implemented"
        )
    
    async def _execute_generic_workflow(
        self, 
        workflow_config: Dict[str, Any], 
        input_data: Dict[str, Any], 
        session_id: str
    ) -> WorkflowResult:
        """Execute generic workflow based on YAML configuration."""
        # TODO: Implement generic workflow executor based on YAML structure
        task_results = []
        
        logger.warning(f"Generic workflow execution not yet implemented for: {workflow_config.get('name')}")
        
        return WorkflowResult(
            workflow_name=workflow_config.get("name", "unknown"),
            status=WorkflowStatus.FAILED,
            task_results=task_results,
            total_execution_time_ms=0,
            success_rate=0.0,
            error="Generic workflow executor not yet implemented"
        )
    
    async def _execute_task(
        self, 
        task_name: str, 
        agent_name: str, 
        input_data: Any
    ) -> TaskResult:
        """
        Execute a single task with specified agent.
        
        Args:
            task_name: Name of the task
            agent_name: Name of the agent to execute the task
            input_data: Input data for the agent
            
        Returns:
            Task execution result
        """
        start_time = time.time()
        
        try:
            # Get agent
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent '{agent_name}' not found")
            
            # Execute task
            logger.debug(f"Executing task {task_name} with agent {agent_name}")
            result = await agent.safe_process(input_data)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return TaskResult(
                task_name=task_name,
                success=result.success,
                data=result.data,
                error=result.error,
                execution_time_ms=execution_time,
                agent_used=agent_name,
                llm_provider_used=result.llm_provider_used
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Task execution failed: {e}")
            
            return TaskResult(
                task_name=task_name,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                agent_used=agent_name
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all agents and LLM providers.
        
        Returns:
            Health status information
        """
        health_status = {
            "crew_manager": "healthy",
            "agents": {},
            "llm_providers": {},
            "total_agents": len(self.agents),
            "healthy_agents": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check agent health
        for agent_name, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_status["agents"][agent_name] = agent_health
                if agent_health.get("status") == "healthy":
                    health_status["healthy_agents"] += 1
            except Exception as e:
                health_status["agents"][agent_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check LLM provider health
        llm_health = await llm_service.health_check_all()
        health_status["llm_providers"] = llm_health
        
        # Determine overall health
        if health_status["healthy_agents"] == health_status["total_agents"]:
            health_status["crew_manager"] = "healthy"
        elif health_status["healthy_agents"] > 0:
            health_status["crew_manager"] = "degraded"
        else:
            health_status["crew_manager"] = "unhealthy"
        
        return health_status
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow names."""
        return config_loader.get_all_workflow_names()
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent."""
        agent = self.agents.get(agent_name)
        if agent:
            return agent.get_agent_info()
        return None
    
    async def reload_configurations(self):
        """Reload all YAML configurations and reinitialize agents."""
        try:
            # Reload configurations
            config_loader.reload_all_configs()
            
            # Reinitialize agents with new configurations
            old_agents = self.agents.copy()
            self.agents.clear()
            
            try:
                self._initialize_agents()
                logger.info("Configurations and agents reloaded successfully")
            except Exception as init_error:
                # Restore old agents if reinitialization fails
                self.agents = old_agents
                logger.error(f"Failed to reinitialize agents, restored previous state: {init_error}")
                raise
                
        except Exception as e:
            logger.error(f"Failed to reload configurations: {e}")
            raise


# Global crew manager instance
crew_manager = CrewManager()