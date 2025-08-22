"""
FastAPI Application for Duck Therapy System

Main entry point for the multi-agent psychological support API.
"""
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, Any

from src.config.settings import settings
from src.services.crew_manager import crew_manager
from src.services.llm_service import llm_service
from src.api.chat import router as chat_router
from loguru import logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/duck_therapy.log", rotation="1 day", retention="7 days")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Duck Therapy API server...")
    
    # Perform health checks
    try:
        health_status = await crew_manager.health_check()
        logger.info(f"System health check completed: {health_status['crew_manager']}")
    except Exception as e:
        logger.error(f"Health check failed during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Duck Therapy API server...")


# Create FastAPI application
app = FastAPI(
    title="Duck Therapy API",
    description="Multi-agent psychological support system with warm duck personality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🦆 Duck Therapy API",
        "description": "Multi-agent psychological support system",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_status = await crew_manager.health_check()
        
        # Determine HTTP status code based on overall health
        status_code = 200
        if health_status["crew_manager"] == "degraded":
            status_code = 206  # Partial Content
        elif health_status["crew_manager"] == "unhealthy":
            status_code = 503  # Service Unavailable
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "crew_manager": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/health/llm")
async def llm_health_check():
    """LLM providers health check endpoint."""
    try:
        health_status = await llm_service.check_all_health()
        
        # Count healthy providers
        healthy_count = sum(1 for status in health_status.values() if status.get("status") == "healthy")
        total_count = len(health_status)
        
        status_code = 200
        if healthy_count == 0:
            status_code = 503  # Service Unavailable
        elif healthy_count < total_count:
            status_code = 206  # Partial Content
        
        return JSONResponse(
            status_code=status_code,
            content={
                "providers": health_status,
                "healthy_count": healthy_count,
                "total_count": total_count,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/info/agents")
async def get_agents_info():
    """Get information about available agents."""
    try:
        agents = crew_manager.get_available_agents()
        agent_info = {}
        
        for agent_name in agents:
            info = crew_manager.get_agent_info(agent_name)
            if info:
                agent_info[agent_name] = info
        
        return {
            "available_agents": agents,
            "agent_details": agent_info,
            "total_count": len(agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info/workflows")
async def get_workflows_info():
    """Get information about available workflows."""
    try:
        workflows = crew_manager.get_available_workflows()
        
        return {
            "available_workflows": workflows,
            "total_count": len(workflows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get workflow info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/reload-config")
async def reload_configuration(background_tasks: BackgroundTasks):
    """Reload YAML configurations (admin endpoint)."""
    try:
        # Schedule reload in background to avoid blocking
        background_tasks.add_task(crew_manager.reload_configurations)
        
        return {
            "message": "Configuration reload scheduled",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/config/validate")
async def validate_configuration():
    """Validate all YAML configurations."""
    try:
        from src.utils.config_loader import config_loader
        
        validation_results = config_loader.validate_all_configs()
        
        # Determine if validation passed
        has_errors = (
            len(validation_results["invalid_agents"]) > 0 or
            len(validation_results["invalid_tasks"]) > 0 or
            len(validation_results["errors"]) > 0
        )
        
        status_code = 200 if not has_errors else 400
        
        return JSONResponse(
            status_code=status_code,
            content={
                "validation_passed": not has_errors,
                "results": validation_results,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )