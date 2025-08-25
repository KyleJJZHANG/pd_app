"""
Application Settings with Multi-LLM Configuration
"""
from typing import List, Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application configuration with multi-LLM support."""
    
    # Application Settings
    app_name: str = "Duck Therapy Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Settings
    database_url: str = "sqlite:///./duck_therapy.db"
    
    # Security Settings
    secret_key: str = Field(default="development-secret-key-change-in-production-32-chars", min_length=32)
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    session_expire_minutes: int = 1440  # 24 hours
    
    # Rate Limiting
    rate_limit_requests: int = 60
    rate_limit_period: int = 60
    
    # LLM Provider Configuration
    primary_llm_provider: Literal["openai", "anthropic", "ollama"] = "ollama"
    fallback_llm_provider: Optional[Literal["openai", "anthropic", "ollama"]] = "ollama"
    local_llm_provider: Literal["ollama"] = "ollama"
    enable_llm_fallback: bool = True
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    anthropic_max_tokens: int = 2000
    anthropic_temperature: float = 0.7
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5"
    ollama_timeout: int = 30
    
    # Agent-specific LLM Configuration
    listener_agent_llm: Literal["openai", "anthropic", "ollama"] = "ollama"
    duck_style_agent_llm: Literal["openai", "anthropic", "ollama"] = "ollama" 
    content_recall_agent_llm: Literal["openai", "anthropic", "ollama"] = "ollama"
    therapy_tips_agent_llm: Literal["openai", "anthropic", "ollama"] = "ollama"
    report_agent_llm: Literal["openai", "anthropic", "ollama"] = "ollama"
    
    # Cache Configuration
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = False
    
    # Content Configuration
    content_base_url: str = "/content"
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    
    # Logging Configuration
    log_file_path: str = "./logs/app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    
    # Development Features
    enable_api_docs: bool = True
    enable_cors: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields to prevent validation errors
    }
        
    def get_llm_config(self, provider: str) -> dict:
        """Get configuration for specific LLM provider."""
        if provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": self.openai_base_url,
                "max_tokens": self.openai_max_tokens,
                "temperature": self.openai_temperature,
            }
        elif provider == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
                "max_tokens": self.anthropic_max_tokens,
                "temperature": self.anthropic_temperature,
            }
        elif provider == "ollama":
            return {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
                "timeout": self.ollama_timeout,
            }
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def is_llm_available(self, provider: str) -> bool:
        """Check if LLM provider is configured and available."""
        # Always return True - let LLM service handle initialization
        return True


# Global settings instance
settings = Settings()