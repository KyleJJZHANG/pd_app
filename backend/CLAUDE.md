# CLAUDE.md

This file provides guidance to Claude Code when working with the Duck Therapy Backend project.


# Project Summary
The Duck Therapy Backend is a multi-agent system built with CrewAI and FastAPI that provides psychological companionship through intelligent conversation. The system uses specialized AI agents to analyze emotions, provide therapy suggestions, recommend content, and maintain a warm, healing communication style consistent with the duck character IP.

# Project Architecture
This is a **CrewAI-based multi-agent backend** for the Duck Therapy application:

- **Framework**: FastAPI + CrewAI (with native LLM support)
- **Agents**: 5 specialized agents (Listener, DuckStyle, ContentRecall, TherapyTips, Report)
- **Database**: Supabase (production) + SQLite (development)
- **Cache**: Redis
- **LLM Integration**: CrewAI native support with local Ollama (Deepseek R1 7B model)
- **Deployment**: Docker + Docker Compose

# Development Commands

**Package Manager**: pip with conda environment (required)

```bash
# Create environment
conda create -n duck_therapy python=3.11 -y
conda activate duck_therapy

# Install dependencies
pip install -r requirements.txt

# Start development server (recommended)
python start.py

# Alternative: Direct uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when available)
pytest tests/ -v

# Code formatting
black .
pylint **/*.py

# Health check
curl http://localhost:8000/health

# Start Ollama with Deepseek model (required before starting backend)
ollama run qwen2.5
```

# Core Application Structure

**Main Entry Points**:
- `main.py` - FastAPI application with CORS and route registration
- `start.py` - Startup script with environment checks and directory creation

**Current Implementation Status** (MVP-0.1):
- ✅ `src/agents/base_agent.py` - Base agent class with common functionality
- ✅ `src/agents/listener_agent.py` - Emotion analysis and keyword extraction
- ✅ `src/agents/duck_style_agent.py` - Maintain duck personality and healing tone
- ⚠️ `content_recall_agent.py` - Not yet implemented (TODO in crew_manager.py)
- ⚠️ `therapy_tips_agent.py` - Not yet implemented (TODO in crew_manager.py)
- ⚠️ `report_agent.py` - Not yet implemented (TODO in crew_manager.py)

**API Routes** (`src/api/`):
- ✅ `chat.py` - Complete chat messaging endpoints with session management and performance optimization
  - ✅ `POST /chat/message` - Standard chat API with caching optimization
  - ✅ `POST /chat/stream` - Real-time streaming chat with SSE progress updates  
  - ✅ `GET /chat/performance/stats` - Performance statistics and metrics
  - ✅ `POST /chat/performance/optimize` - Manual performance optimization trigger
  - ✅ Session management endpoints (get, clear, delete, list)

**Services** (`src/services/`):
- ✅ `crew_manager.py` - Multi-agent workflow orchestration with performance optimization
  - ✅ Intelligent caching system with MD5 keys and TTL management
  - ✅ Real-time streaming workflow execution (`execute_workflow_stream`)
  - ✅ Agent warm-up and performance monitoring
  - ✅ Background cache cleanup and optimization methods
- ✅ `llm_service.py` - LLM provider management with fallback

**Data Models** (`src/models/`):
- ✅ `message.py` - Chat message schemas
- ✅ `emotion.py` - Emotion analysis data models
- ✅ `content.py` - Content asset models (basic)
- ✅ `report.py` - Report generation models (basic)

**Configuration**:
- ✅ `src/config/settings.py` - Comprehensive multi-LLM settings
- ✅ `config/agents.yaml` - Agent personalities and LLM preferences
- ✅ `config/tasks.yaml` - Task templates and workflow definitions
- ✅ `src/utils/config_loader.py` - YAML configuration management

# Key Data Models

**Message**: Chat messages with emotion analysis
**EmotionAnalysis**: Sentiment, intensity, emotion tags, keywords
**ContentAsset**: Comics/videos with emotion relevance scores
**TherapyTip**: Structured psychological exercises and guidance
**DailyReport**: Emotion trends and encouraging insights

# Environment Variables

Required environment variables in `.env`:
```bash
# Application
APP_NAME="Duck Therapy Backend"
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./duck_therapy.db  # Development
# DATABASE_URL=postgresql://user:pass@host:5432/duck_therapy  # Production

# Local LLM (Ollama) Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5
OLLAMA_TIMEOUT=30

# LLM Provider Settings (configured to use Ollama only)
PRIMARY_LLM_PROVIDER=ollama
FALLBACK_LLM_PROVIDER=ollama
ENABLE_LLM_FALLBACK=true

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Cache (optional)
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false  # Set to true in production
```

# Development Workflow

## Current MVP Status
- **MVP-0.1** ✅ **IMPLEMENTED**: Basic chat flow (Listener + DuckStyle + API endpoints)
  - ✅ FastAPI application with CORS and health endpoints
  - ✅ Multi-agent CrewAI system with ListenerAgent and DuckStyleAgent
  - ✅ Complete chat API with session management and streaming
  - ✅ YAML-driven configuration system
  - ✅ CrewAI native LLM support with local Ollama (Deepseek R1 7B)
  - ✅ Comprehensive logging and error handling

- **MVP-0.1.5** ✅ **IMPLEMENTED**: Performance Optimization & Streaming
  - ✅ **Intelligent Caching System**: 30-min TTL emotion analysis cache with 75%+ speed improvement
  - ✅ **Real-time Streaming API**: `/chat/stream` endpoint with live progress updates
  - ✅ **Agent Warm-up**: Automatic first-time initialization to reduce cold start latency
  - ✅ **Performance Monitoring**: Comprehensive metrics, cache statistics, and optimization tools
  - ✅ **Optimized Data Transfer**: Essential-field-only transmission to reduce overhead
  - ✅ **Natural Language Processing**: Analytical phrase filtering for more natural duck responses
  - ✅ **Background Cache Management**: Automatic cleanup and TTL management
  - ✅ **Performance APIs**: `/chat/performance/stats` and `/chat/performance/optimize` endpoints

- **MVP-0.2** 🚧 **IN PROGRESS**: Content integration
  - ⚠️ ContentRecallAgent implementation needed
  - ⚠️ Media asset indexing system
  - ⚠️ Content recommendation workflow integration

- **MVP-0.3** 📋 **PLANNED**: Therapy features
  - ⚠️ TherapyTipsAgent implementation needed
  - ⚠️ Structured psychological exercises
  - ⚠️ Safety validation for therapeutic content

- **MVP-0.4** 📋 **PLANNED**: Analytics and reporting
  - ⚠️ ReportAgent implementation needed
  - ⚠️ Daily emotion summaries and trend analysis
  - ⚠️ User progress tracking

## Implementation Priority (Next Steps)
1. **Complete Content System**: Implement ContentRecallAgent and media indexing
2. **Therapy Features**: Add TherapyTipsAgent with safety validation
3. **Analytics Module**: Implement ReportAgent for daily summaries
4. **Database Integration**: Replace in-memory storage with persistent database
5. **Enhanced Workflows**: Complete enhanced_chat_flow and daily_report_flow
6. **Testing Suite**: Add comprehensive unit and integration tests

# Performance Optimization Features (MVP-0.1.5)

## Intelligent Caching System
- **Emotion Analysis Cache**: MD5-hashed keys with 30-minute TTL
- **Cache Hit Performance**: 75%+ faster response times on cached requests
- **Context-Aware Caching**: Includes last 3 conversation messages in cache key
- **Automatic Cleanup**: Background TTL management and memory optimization (max 1000 entries)
- **Cache Statistics**: Real-time hit/miss rates and performance tracking

## Real-time Streaming API
- **Server-Sent Events (SSE)**: `/chat/stream` endpoint for live progress updates
- **Stream Chunk Types**: 
  - `emotion_start` - Emotion analysis begins
  - `emotion_result` - Analysis complete with cache status
  - `response_start` - Duck response generation begins  
  - `response_end` - Complete response with timing
  - `complete` - Full workflow finished with statistics
  - `error` - Error handling with graceful fallback

## Performance Monitoring
- **Comprehensive Metrics**: Response times, cache statistics, LLM call counts
- **Performance APIs**:
  - `GET /chat/performance/stats` - Current performance statistics
  - `POST /chat/performance/optimize` - Manual optimization trigger
- **Real-time Dashboard Data**: Average times, cache hit rates, request counts
- **Historical Tracking**: Last 100 requests with detailed metrics

## Agent Optimization
- **Smart Warm-up**: First-time agent initialization with sample data
- **Optimized Data Transfer**: Essential emotion fields only (sentiment, intensity, emotions, urgency)
- **Natural Language Enhancement**: Automatic removal of analytical phrases for friendlier responses
- **LLM Call Tracking**: Precise monitoring of model usage and performance

## Frontend Integration Support
- **Streaming Response Handling**: Complete SSE implementation examples
- **Performance Monitoring**: Client-side statistics and optimization triggers
- **Error Resilience**: Automatic fallback from streaming to regular API
- **Cache Indicators**: Visual feedback for cache-accelerated responses

## Performance Benchmarks
- **First Execution**: ~10.8s (includes warm-up and cache miss)
- **Cached Execution**: ~2.7s (75% improvement)  
- **Cache Hit Rate**: 50%+ in typical usage patterns
- **Memory Usage**: Intelligent cache management with size limits
- **Throughput**: Significantly improved concurrent request handling

# Code Standards

- **Type Hints**: All functions must have type annotations
- **Docstrings**: Google-style docstrings for all classes and methods
- **Error Handling**: Comprehensive exception handling with logging
- **Testing**: Unit tests for agents and API endpoints
- **Security**: Input validation, output sanitization, rate limiting
- **Performance**: Async/await, connection pooling, caching strategies

# Agent Development Guidelines

1. **Inherit from BaseAgent**: All agents extend `src/agents/base_agent.py`
2. **YAML Configuration**: Define agent in `config/agents.yaml` with role, goal, and backstory in Chinese
3. **Input/Output Models**: Create Pydantic models for agent input/output (see existing examples)
4. **Process Method**: Implement async `process()` method with error handling and LLM interaction
5. **Safe Processing**: Use `safe_process()` wrapper for automatic error handling and logging
6. **LLM Provider**: All agents use Ollama with Deepseek R1 7B model (configured in YAML)
7. **Health Check**: Implement `health_check()` method for system monitoring
8. **Registration**: Add agent to `CrewManager._initialize_agents()` method

# Data Storage

## Current Implementation (MVP-0.1)
- **In-Memory Storage**: `chat_sessions` dictionary in `src/api/chat.py`
- **Session Data**: Messages, emotion history, metadata
- **Persistence**: None (data lost on restart)

## Planned Database Design
- **Sessions**: User chat sessions with metadata
- **Messages**: Chat messages with emotion analysis
- **Content Assets**: Comics/videos with emotion relevance mapping  
- **Usage Stats**: Content usage and feedback for optimization
- **Emotion Logs**: Historical emotion data for trend analysis

## Storage Location Patterns
- **SQLite Development**: `duck_therapy.db` (local file)
- **Production**: PostgreSQL via `DATABASE_URL` environment variable
- **Cache**: Redis for session data and LLM response caching

# Security Considerations

- **Input Sanitization**: Validate and sanitize all user inputs
- **Output Safety**: Filter sensitive information and inappropriate content
- **API Rate Limiting**: Prevent abuse with request limits
- **Data Privacy**: Encrypt sensitive data, implement data retention policies
- **Authentication**: Session-based auth with secure token management

# Integration Notes

- **Frontend Compatibility**: APIs designed to work with existing React frontend
- **Gradual Migration**: Support both local storage fallback and API modes
- **Real-time Features**: WebSocket support for live chat experience
- **Content Management**: File serving and CDN integration for media assets

# Deployment Configuration

- **Development**: SQLite + local file storage
- **Production**: Supabase + Redis + Docker deployment
- **Monitoring**: Prometheus metrics + structured logging
- **Scaling**: Horizontal scaling with stateless design

# Important Implementation Notes

1. **Chinese Language Support**: All user-facing content in Chinese
2. **Therapeutic Focus**: Maintain supportive, non-clinical tone with analytical phrase filtering
3. **Duck IP Consistency**: All responses must align with duck character - natural conversation, not analysis
4. **Safety First**: Always prioritize user safety and appropriate responses
5. **Performance Optimized**: Achieved <3s response times with 75%+ improvement on cached requests
6. **Local LLM Dependency**: Requires Ollama server running with Deepseek R1 7B model
7. **Reliability**: Implement circuit breakers, graceful degradation, and intelligent caching
8. **Real-time Experience**: Streaming API provides live progress updates for better UX
9. **Scalability**: Smart caching and performance monitoring support high concurrent usage
10. **Monitoring**: Comprehensive performance tracking with automatic optimization

# Testing Strategy

- **Unit Tests**: Individual agent and service testing
- **Integration Tests**: Full API workflow testing
- **Agent Tests**: Validate agent responses and behavior
- **Performance Tests**: Load testing and response time validation
- **Safety Tests**: Content safety and appropriateness validation

# Key Implementation Details

## Workflow System
- **Basic Chat Flow**: `emotion_analysis` → `duck_response_generation`
- **Enhanced Chat Flow**: Includes parallel content recommendation and therapy suggestions
- **Task Dependencies**: Defined in `config/tasks.yaml` with conditional execution
- **Execution**: Orchestrated by `CrewManager.execute_workflow()`

## Configuration Management
- **YAML Configs**: `config/agents.yaml` and `config/tasks.yaml`
- **Runtime Reload**: `/admin/reload-config` endpoint for hot config updates
- **Validation**: `/admin/config/validate` endpoint for configuration validation
- **Fallback Chains**: LLM provider fallback defined in YAML

## API Architecture
- **Session-based**: Each chat maintains session state with unique session_id
- **Streaming Support**: `/chat/stream` endpoint for real-time responses
- **Comprehensive Endpoints**: Session management, message history, emotion analysis
- **Health Monitoring**: Multiple health check endpoints with detailed status

## Agent Communication
- **Input/Output**: Strongly typed Pydantic models for all agent interactions
- **Error Handling**: `safe_process()` wrapper with automatic fallback and logging
- **LLM Configuration**: CrewAI native LLM class attributes (no LangChain dependency)
- **LLM Routing**: All agents configured to use local Ollama with Deepseek R1 7B model
- **Performance Tracking**: Execution time and success rate metrics

When implementing new features:
1. **Start with YAML Configuration**: Define agents and tasks in config files
2. **Create Data Models**: Add Pydantic models for input/output validation
3. **Implement Agent Class**: Extend BaseAgent with process() method
4. **Register in CrewManager**: Add to _initialize_agents() method
5. **Update Workflows**: Modify workflow execution logic if needed
6. **Add API Endpoints**: Create FastAPI routes if external access needed
7. **Update Health Checks**: Ensure new components have health monitoring

This backend serves as the intelligent heart of the Duck Therapy application, providing warm, personalized psychological support through advanced AI agent collaboration with YAML-driven flexibility and local Ollama inference using the Deepseek R1 7B model.

- add to memoty "Should not use Unicode icons in print statements and log_result calls for console output review, especially on Windows systems
  that use GBK encoding by default."