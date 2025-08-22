"""
Configuration Loader for Duck Therapy System

Utility for loading and managing YAML-based agent and task configurations.
"""
import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

from ..config.settings import settings


class ConfigLoader:
    """Configuration loader for agents and tasks."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            # Default to config directory relative to project root
            current_dir = Path(__file__).parent.parent.parent
            self.config_dir = current_dir / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self._agent_configs: Optional[Dict[str, Any]] = None
        self._task_configs: Optional[Dict[str, Any]] = None
        
        logger.info(f"ConfigLoader initialized with config dir: {self.config_dir}")
    
    def load_agent_configs(self, reload: bool = False) -> Dict[str, Any]:
        """
        Load agent configurations from YAML file.
        
        Args:
            reload: Force reload even if already cached
            
        Returns:
            Dictionary of agent configurations
        """
        if self._agent_configs is None or reload:
            config_file = self.config_dir / "agents.yaml"
            
            if not config_file.exists():
                logger.error(f"Agent config file not found: {config_file}")
                return {}
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._agent_configs = yaml.safe_load(f)
                    logger.info("Agent configurations loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load agent configs: {e}")
                return {}
        
        return self._agent_configs or {}
    
    def load_task_configs(self, reload: bool = False) -> Dict[str, Any]:
        """
        Load task configurations from YAML file.
        
        Args:
            reload: Force reload even if already cached
            
        Returns:
            Dictionary of task configurations
        """
        if self._task_configs is None or reload:
            config_file = self.config_dir / "tasks.yaml"
            
            if not config_file.exists():
                logger.error(f"Task config file not found: {config_file}")
                return {}
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._task_configs = yaml.safe_load(f)
                    logger.info("Task configurations loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load task configs: {e}")
                return {}
        
        return self._task_configs or {}
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent configuration dictionary or None if not found
        """
        configs = self.load_agent_configs()
        agents = configs.get("agents", {})
        return agents.get(agent_name)
    
    def get_task_template(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Get template for a specific task.
        
        Args:
            task_name: Name of the task template
            
        Returns:
            Task template dictionary or None if not found
        """
        configs = self.load_task_configs()
        templates = configs.get("task_templates", {})
        return templates.get(task_name)
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow configuration.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Workflow configuration dictionary or None if not found
        """
        configs = self.load_task_configs()
        workflows = configs.get("workflows", {})
        return workflows.get(workflow_name)
    
    def get_all_agent_names(self) -> List[str]:
        """
        Get list of all configured agent names.
        
        Returns:
            List of agent names
        """
        configs = self.load_agent_configs()
        agents = configs.get("agents", {})
        return list(agents.keys())
    
    def get_all_task_names(self) -> List[str]:
        """
        Get list of all configured task template names.
        
        Returns:
            List of task template names
        """
        configs = self.load_task_configs()
        templates = configs.get("task_templates", {})
        return list(templates.keys())
    
    def get_all_workflow_names(self) -> List[str]:
        """
        Get list of all configured workflow names.
        
        Returns:
            List of workflow names
        """
        configs = self.load_task_configs()
        workflows = configs.get("workflows", {})
        return list(workflows.keys())
    
    def get_global_settings(self) -> Dict[str, Any]:
        """
        Get global agent settings.
        
        Returns:
            Global settings dictionary
        """
        configs = self.load_agent_configs()
        return configs.get("global_settings", {})
    
    def get_execution_settings(self) -> Dict[str, Any]:
        """
        Get task execution settings.
        
        Returns:
            Execution settings dictionary
        """
        configs = self.load_task_configs()
        return configs.get("execution_settings", {})
    
    def get_fallback_chain(self, provider: str) -> List[str]:
        """
        Get LLM provider fallback chain.
        
        Args:
            provider: Primary LLM provider name
            
        Returns:
            List of fallback providers in order
        """
        configs = self.load_agent_configs()
        chains = configs.get("fallback_chains", {})
        return chains.get(provider, [])
    
    def validate_agent_config(self, agent_name: str) -> bool:
        """
        Validate agent configuration.
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        config = self.get_agent_config(agent_name)
        
        if not config:
            logger.error(f"Agent config not found: {agent_name}")
            return False
        
        required_fields = ["name", "role", "goal", "backstory"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field '{field}' in agent {agent_name}")
                return False
        
        # Validate LLM provider
        llm_provider = config.get("llm_provider")
        if llm_provider and not settings.is_llm_available(llm_provider):
            logger.warning(f"LLM provider '{llm_provider}' not available for agent {agent_name}")
        
        return True
    
    def validate_task_template(self, task_name: str) -> bool:
        """
        Validate task template configuration.
        
        Args:
            task_name: Name of the task template to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        template = self.get_task_template(task_name)
        
        if not template:
            logger.error(f"Task template not found: {task_name}")
            return False
        
        required_fields = ["name", "description", "expected_output", "agent"]
        
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field '{field}' in task {task_name}")
                return False
        
        # Validate agent reference
        agent_name = template.get("agent")
        if agent_name and not self.get_agent_config(agent_name):
            logger.error(f"Referenced agent '{agent_name}' not found in task {task_name}")
            return False
        
        return True
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """
        Validate all configurations.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid_agents": [],
            "invalid_agents": [],
            "valid_tasks": [],
            "invalid_tasks": [],
            "errors": []
        }
        
        # Validate agents
        for agent_name in self.get_all_agent_names():
            if self.validate_agent_config(agent_name):
                results["valid_agents"].append(agent_name)
            else:
                results["invalid_agents"].append(agent_name)
        
        # Validate tasks
        for task_name in self.get_all_task_names():
            if self.validate_task_template(task_name):
                results["valid_tasks"].append(task_name)
            else:
                results["invalid_tasks"].append(task_name)
        
        return results
    
    def reload_all_configs(self):
        """Reload all configuration files."""
        self.load_agent_configs(reload=True)
        self.load_task_configs(reload=True)
        logger.info("All configurations reloaded")


# Global configuration loader instance
config_loader = ConfigLoader()