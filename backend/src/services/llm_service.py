"""
Multi-LLM Service for Duck Therapy System

Provides unified interface for OpenAI, Anthropic Claude, and Ollama LLMs
with intelligent fallback and provider selection using CrewAI's native LLM support.
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio
import httpx
from loguru import logger

from crewai.llm import LLM

from ..config.settings import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMService:
    """Multi-LLM service with fallback support."""
    
    def __init__(self):
        self._llm_instances: Dict[str, Any] = {}
        self._health_status: Dict[str, bool] = {}
        self._initialize_llms()
    
    def _initialize_llms(self):
        """Initialize all configured LLM providers using CrewAI's LLM class."""
        
        # Only initialize Ollama since that's what we're using
        try:
            self._llm_instances[LLMProvider.OLLAMA] = LLM(
                model=f"ollama/{settings.ollama_model}",
                base_url=settings.ollama_base_url,
                timeout=settings.ollama_timeout
            )
            # Test Ollama connection will be done later via health check
            self._health_status[LLMProvider.OLLAMA] = True
            logger.info(f"Ollama LLM initialized successfully with model: {settings.ollama_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self._health_status[LLMProvider.OLLAMA] = False
    
    async def _test_ollama_health(self):
        """Test Ollama server health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.ollama_base_url}/api/tags")
                self._health_status[LLMProvider.OLLAMA] = response.status_code == 200
        except Exception:
            self._health_status[LLMProvider.OLLAMA] = False
    
    def get_llm_for_agent(self, agent_name: str) -> Optional[Any]:
        """Get the configured LLM for a specific agent."""
        provider_mapping = {
            "listener": settings.listener_agent_llm,
            "duck_style": settings.duck_style_agent_llm,
            "content_recall": settings.content_recall_agent_llm,
            "therapy_tips": settings.therapy_tips_agent_llm,
            "report": settings.report_agent_llm,
        }
        
        provider = provider_mapping.get(agent_name, settings.primary_llm_provider)
        return self.get_llm(provider)
    
    def get_llm(self, provider: Optional[str] = None) -> Optional[Any]:
        """Get LLM instance with fallback support."""
        
        if provider is None:
            provider = settings.primary_llm_provider
        
        # Try requested provider first
        if provider in self._llm_instances and self._health_status.get(provider, False):
            return self._llm_instances[provider]
        
        # Fallback logic if enabled
        if settings.enable_llm_fallback:
            fallback_order = self._get_fallback_order(provider)
            
            for fallback_provider in fallback_order:
                if (fallback_provider in self._llm_instances and 
                    self._health_status.get(fallback_provider, False)):
                    logger.warning(f"Using fallback LLM: {fallback_provider} (requested: {provider})")
                    return self._llm_instances[fallback_provider]
        
        logger.error(f"No available LLM found (requested: {provider})")
        return None
    
    def _get_fallback_order(self, requested_provider: str) -> List[str]:
        """Get fallback order for LLM providers."""
        
        # Define preferred fallback chains
        fallback_chains = {
            LLMProvider.OPENAI: [LLMProvider.ANTHROPIC, LLMProvider.OLLAMA],
            LLMProvider.ANTHROPIC: [LLMProvider.OPENAI, LLMProvider.OLLAMA],
            LLMProvider.OLLAMA: [LLMProvider.OPENAI, LLMProvider.ANTHROPIC],
        }
        
        return fallback_chains.get(requested_provider, [
            LLMProvider.OPENAI, 
            LLMProvider.ANTHROPIC, 
            LLMProvider.OLLAMA
        ])
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """Generate response using specified or fallback LLM with CrewAI."""
        
        llm = self.get_llm(provider)
        if llm is None:
            return None
        
        try:
            # Combine system prompt and user message for CrewAI LLM
            full_prompt = f"System: {system_prompt}\n\nUser: {user_message}"
            
            # Use CrewAI's LLM.call method (not async)
            response = llm.call(full_prompt, **kwargs)
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed with {provider}: {e}")
            
            # Try fallback if enabled and this isn't already a fallback
            if settings.enable_llm_fallback and provider == settings.primary_llm_provider:
                fallback_provider = settings.fallback_llm_provider
                if fallback_provider and fallback_provider != provider:
                    logger.info(f"Attempting fallback to {fallback_provider}")
                    return await self.generate_response(
                        system_prompt, user_message, fallback_provider, **kwargs
                    )
            
            return None
    
    def get_health_status(self) -> Dict[str, bool]:
        """Get health status of all LLM providers."""
        return self._health_status.copy()
    
    async def check_all_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all LLM providers."""
        
        async def check_provider_health(provider: str, llm: Any) -> Dict[str, Any]:
            try:
                if provider == LLMProvider.OLLAMA:
                    await self._test_ollama_health()
                    status = self._health_status[LLMProvider.OLLAMA]
                else:
                    # Test with a simple message for other providers using CrewAI
                    test_response = llm.call("Hello")
                    status = bool(test_response)
                
                return {
                    "status": "healthy" if status else "unhealthy",
                    "provider": provider,
                    "model": getattr(llm, 'model', 'unknown')
                }
            except Exception as e:
                logger.error(f"Health check failed for {provider}: {e}")
                return {
                    "status": "unhealthy",
                    "provider": provider,
                    "error": str(e)
                }
        
        health_results = {}
        tasks = []
        for provider, llm in self._llm_instances.items():
            task = check_provider_health(provider, llm)
            tasks.append((provider, task))
        
        for provider, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=10.0)
                health_results[provider] = result
                self._health_status[provider] = result["status"] == "healthy"
            except asyncio.TimeoutError:
                health_results[provider] = {
                    "status": "unhealthy",
                    "provider": provider,
                    "error": "Health check timeout"
                }
                self._health_status[provider] = False
                logger.warning(f"Health check timeout for {provider}")
        
        return health_results

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Alias for check_all_health for backward compatibility."""
        return await self.check_all_health()


# Global LLM service instance
llm_service = LLMService()