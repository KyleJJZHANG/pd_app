"""
Base Agent for Duck Therapy System

Abstract base class for all CrewAI agents with multi-LLM support and
unified processing interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
import time
from datetime import datetime

from crewai import Agent, Task
from pydantic import BaseModel
from loguru import logger

from ..services.llm_service import llm_service
from ..config.settings import settings
from ..utils.config_loader import config_loader


class BaseAgentInput(BaseModel):
    """Base input model for all agents."""
    
    session_id: str
    timestamp: datetime
    
    class Config:
        extra = "allow"  # Allow additional fields


class BaseAgentOutput(BaseModel):
    """Base output model for all agents."""
    
    success: bool
    agent_name: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    llm_provider_used: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


class BaseAgent(ABC):
    """Abstract base class for all therapy agents."""
    
    def __init__(
        self,
        agent_name: str,
        config_override: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None,
        **kwargs
    ):
        """
        Initialize base agent with YAML configuration support.
        
        Args:
            agent_name: Agent name identifier (must match YAML config)
            config_override: Optional configuration overrides
            tools: List of tools available to agent
            **kwargs: Additional agent configuration
        """
        self.name = agent_name
        
        # Load configuration from YAML
        config = config_loader.get_agent_config(agent_name)
        if not config:
            raise ValueError(f"Agent configuration not found for: {agent_name}")
        
        # Apply overrides if provided
        if config_override:
            config.update(config_override)
        
        # Extract configuration values
        role = config.get("role", "AI Agent")
        goal = config.get("goal", "Assist users")
        backstory = config.get("backstory", "I am an AI assistant.")
        self.llm_provider = config.get("llm_provider")
        verbose = config.get("verbose", True)
        allow_delegation = config.get("allow_delegation", False)
        
        # Store configuration for reference
        self.config = config
        
        # Get LLM instance with potential model override
        llm = self._get_configured_llm(config)
        if llm is None:
            raise ValueError(f"No LLM provider available for agent {agent_name}")
        
        # Create CrewAI agent
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or self._load_configured_tools(config),
            llm=llm,
            verbose=verbose,
            allow_delegation=allow_delegation,
            **kwargs
        )
        
        logger.info(f"Initialized {agent_name} agent from YAML config")
    
    def _get_configured_llm(self, config: Dict[str, Any]):
        """Get LLM instance based on agent configuration using CrewAI's LLM class attributes."""
        provider = config.get("llm_provider", "openai")
        model_override = config.get("model_override")
        temperature = config.get("temperature")
        max_tokens = config.get("max_tokens")
        
        # Use CrewAI's LLM class attributes approach
        from crewai.llm import LLM
        
        # Determine model string format
        if model_override:
            # Check if model_override already has provider prefix
            if model_override.startswith(f"{provider}/"):
                model_str = model_override
            else:
                model_str = f"{provider}/{model_override}"
        else:
            # Use defaults from settings
            if provider == "openai":
                model_str = f"openai/{settings.openai_model}"
            elif provider == "anthropic":
                model_str = f"anthropic/{settings.anthropic_model}"
            elif provider == "ollama":
                model_str = f"ollama/{settings.ollama_model}"
            else:
                model_str = f"openai/{settings.openai_model}"  # Default fallback
        
        # Get API key for the provider
        api_key = None
        base_url = None
        if provider == "openai":
            api_key = settings.openai_api_key
            base_url = settings.openai_base_url
        elif provider == "anthropic":
            api_key = settings.anthropic_api_key
        elif provider == "ollama":
            base_url = settings.ollama_base_url
        
        # Create LLM instance with configuration
        llm_config = {
            "model": model_str
        }
        
        if api_key:
            llm_config["api_key"] = api_key
        if base_url:
            llm_config["base_url"] = base_url
        if temperature is not None:
            llm_config["temperature"] = temperature
        if max_tokens is not None:
            llm_config["max_tokens"] = max_tokens
        
        try:
            llm = LLM(**llm_config)
            logger.info(f"Created LLM for agent {self.name}: {model_str}")
            return llm
        except Exception as e:
            logger.error(f"Failed to create LLM for agent {self.name}: {e}")
            
            # Fallback to service method
            llm = llm_service.get_llm_for_agent(self.name)
            if llm is None:
                logger.warning(f"No LLM available for agent {self.name}, using fallback")
                llm = llm_service.get_llm(provider)
            
            return llm
    
    def _load_configured_tools(self, config: Dict[str, Any]) -> list:
        """Load tools specified in configuration."""
        tool_names = config.get("tools", [])
        # TODO: Implement tool loading based on names
        # This would map tool names to actual tool instances
        return []
    
    @abstractmethod
    async def process(self, input_data: BaseAgentInput) -> BaseAgentOutput:
        """
        Process input data and return result.
        
        This method must be implemented by all agent subclasses.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing result with success/error status
        """
        pass
    
    def _validate_input(self, input_data: BaseAgentInput) -> bool:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not input_data.session_id:
            return False
        return True
    
    async def _execute_task(
        self,
        task_description: str,
        expected_output: str,
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Execute a CrewAI task with the agent.
        
        Args:
            task_description: Description of task to execute
            expected_output: Description of expected output format
            context: Optional context information
            **kwargs: Additional task parameters
            
        Returns:
            Task execution result
        """
        # Add context to task description if provided
        if context:
            full_description = f"Context: {context}\n\nTask: {task_description}"
        else:
            full_description = task_description
        
        # Create and execute task
        task = Task(
            description=full_description,
            expected_output=expected_output,
            agent=self.agent,
            **kwargs
        )
        
        try:
            result = task.execute_async()
            return str(result)
        except Exception as e:
            logger.error(f"Task execution failed for {self.name}: {e}")
            raise
    
    def _log_processing(
        self, 
        input_data: BaseAgentInput, 
        output: BaseAgentOutput,
        start_time: float
    ):
        """
        Log processing information.
        
        Args:
            input_data: Input data that was processed
            output: Output data that was generated
            start_time: Processing start time
        """
        processing_time = int((time.time() - start_time) * 1000)
        
        log_data = {
            "agent": self.name,
            "session_id": input_data.session_id,
            "success": output.success,
            "processing_time_ms": processing_time,
            "llm_provider": output.llm_provider_used,
        }
        
        if output.error:
            log_data["error"] = output.error
            logger.error("Agent processing failed", **log_data)
        else:
            logger.info("Agent processing completed", **log_data)
    
    async def safe_process(self, input_data: BaseAgentInput) -> BaseAgentOutput:
        """
        Safe wrapper for process method with error handling and logging.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing result with guaranteed error handling
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not self._validate_input(input_data):
                return BaseAgentOutput(
                    success=False,
                    agent_name=self.name,
                    error="Invalid input data",
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Process data
            result = await self.process(input_data)
            
            # Add processing metadata
            result.processing_time_ms = int((time.time() - start_time) * 1000)
            result.agent_name = self.name
            
            # Determine which LLM provider was used (CrewAI LLM format)
            if hasattr(self.agent, 'llm') and hasattr(self.agent.llm, 'model'):
                model_str = str(self.agent.llm.model).lower()
                if 'openai/' in model_str or 'gpt' in model_str:
                    result.llm_provider_used = "openai"
                elif 'anthropic/' in model_str or 'claude' in model_str:
                    result.llm_provider_used = "anthropic"
                elif 'ollama/' in model_str:
                    result.llm_provider_used = "ollama"
                else:
                    # Try to parse provider from model string format "provider/model"
                    parts = model_str.split('/', 1)
                    if len(parts) >= 2:
                        result.llm_provider_used = parts[0]
            
            # Log processing
            self._log_processing(input_data, result, start_time)
            
            return result
            
        except Exception as e:
            # Create error response
            error_result = BaseAgentOutput(
                success=False,
                agent_name=self.name,
                error=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            # Log error
            self._log_processing(input_data, error_result, start_time)
            
            return error_result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information and status.
        
        Returns:
            Agent information dictionary
        """
        return {
            "name": self.name,
            "role": self.agent.role,
            "goal": self.agent.goal,
            "llm_provider": self.llm_provider,
            "tools_count": len(self.agent.tools) if self.agent.tools else 0,
            "verbose": verbose,
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform agent health check.
        
        Returns:
            Health status information
        """
        try:
            # Test basic functionality with simple input
            test_input = BaseAgentInput(
                session_id="health_check",
                timestamp=datetime.now()
            )
            
            # This should be overridden by subclasses for proper testing
            start_time = time.time()
            health_status = {
                "agent_name": self.name,
                "status": "healthy",
                "response_time_ms": int((time.time() - start_time) * 1000),
                "llm_available": self.agent.llm is not None,
                "tools_loaded": len(self.agent.tools) if self.agent.tools else 0,
            }
            
            return health_status
            
        except Exception as e:
            return {
                "agent_name": self.name,
                "status": "unhealthy",
                "error": str(e),
                "llm_available": False,
            }