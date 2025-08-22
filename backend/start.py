#!/usr/bin/env python3
"""
Startup script for Duck Therapy API

This script handles environment setup and starts the FastAPI server.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "config",
        "data"
    ]
    
    for directory in directories:
        dir_path = backend_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check if required environment variables are set."""
    required_vars = []
    optional_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "OLLAMA_BASE_URL"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these variables before starting the server.")
        return False
    
    if missing_optional:
        print(f"⚠️  Optional environment variables not set: {', '.join(missing_optional)}")
        print("Some LLM providers may not be available.")
    
    return True

def main():
    """Main startup function."""
    print("🦆 Duck Therapy API - Starting Up")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("✓ Environment check passed")
    
    # Check if config files exist
    config_files = ["agents.yaml", "tasks.yaml"]
    for config_file in config_files:
        config_path = backend_dir / "config" / config_file
        if not config_path.exists():
            print(f"⚠️  Config file missing: {config_file}")
            print(f"   Expected at: {config_path}")
        else:
            print(f"✓ Config file found: {config_file}")
    
    print("\n🚀 Starting FastAPI server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check endpoint: http://localhost:8000/health")
    print("💬 Chat endpoint: http://localhost:8000/chat/message")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    # Import and run the app
    try:
        import uvicorn
        from src.config.settings import settings
        
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()