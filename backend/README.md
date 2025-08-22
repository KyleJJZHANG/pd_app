# Duck Therapy Backend API

A multi-agent psychological support system built with CrewAI, FastAPI, and multiple LLM providers. The backend provides therapeutic chat functionality with emotion analysis and duck personality-driven responses.

## 🏗️ Architecture Overview

### Multi-Agent System
- **ListenerAgent**: Emotion analysis and psychological needs assessment
- **DuckStyleAgent**: Maintains duck personality consistency and generates therapeutic responses
- **CrewManager**: Orchestrates multi-agent workflows with intelligent LLM routing

### LLM Provider Support
- **OpenAI**: GPT-4 models for advanced reasoning
- **Anthropic**: Claude models for nuanced conversation
- **Ollama**: Local LLM deployment for privacy
- **Intelligent Fallback**: Automatic failover between providers

### YAML-Driven Configuration
- **agents.yaml**: Agent personalities, LLM preferences, and capabilities
- **tasks.yaml**: Task templates, workflows, and execution parameters
- **Runtime Reload**: Configuration changes without server restart

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+ and conda
python --version
conda --version
```

### Environment Setup
```bash
# Create conda environment
conda create -n duck_therapy python=3.11 -y

# Activate environment
conda activate duck_therapy

# Install dependencies
pip install -r requirements.txt

# Alternative: Install with conda (recommended)
conda install -c conda-forge fastapi uvicorn pydantic loguru pyyaml -y
pip install pydantic-settings crewai langchain-openai langchain-anthropic langchain-ollama ollama
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys (optional but recommended)
# At minimum, set one LLM provider:
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key

# Or export directly (alternative)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Start the Server
```bash
# Ensure conda environment is activated
conda activate duck-therapy

# Using the startup script (recommended)
python start.py

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 API Endpoints

### Core Chat API
```http
POST /chat/message
Content-Type: application/json

{
  "text": "我今天感觉很焦虑",
  "session_id": "user-session-123",
  "workflow_type": "basic_chat_flow",
  "response_style": "standard"
}
```

**Response:**
```json
{
  "message_id": "uuid",
  "response_text": "鸭鸭能感受到你的焦虑，想给你一个温暖的拥抱...",
  "emotion_analysis": {
    "sentiment": "negative",
    "intensity": 0.7,
    "primary_emotions": ["焦虑", "紧张"],
    "psychological_needs": ["安抚", "指导"],
    "urgency_level": 2
  },
  "execution_time_ms": 1500,
  "success_rate": 1.0,
  "llm_providers_used": ["openai"]
}
```

### Session Management
- `GET /chat/session/{session_id}` - Get session info
- `GET /chat/session/{session_id}/messages` - Get conversation history
- `GET /chat/session/{session_id}/emotion-history` - Get emotion analysis history
- `POST /chat/session/{session_id}/clear` - Clear session
- `DELETE /chat/session/{session_id}` - Delete session

### System Health
- `GET /health` - Comprehensive system health check
- `GET /health/llm` - LLM provider health status
- `GET /info/agents` - Available agents information
- `GET /info/workflows` - Available workflows

### Administration
- `POST /admin/reload-config` - Reload YAML configurations
- `GET /admin/config/validate` - Validate all configurations

## 🤖 Workflow Types

### Basic Chat Flow
Simple emotion analysis → duck response generation
```json
{
  "workflow_type": "basic_chat_flow",
  "text": "User message"
}
```

### Enhanced Chat Flow
Emotion analysis → (content recommendation + therapy suggestions) → duck response
```json
{
  "workflow_type": "enhanced_chat_flow",
  "text": "User message",
  "user_preferences": {"topics": ["meditation", "exercise"]}
}
```

## 🔧 Configuration

### Agent Configuration (`config/agents.yaml`)
```yaml
agents:
  listener_agent:
    name: "情绪倾听者"
    role: "专业的情绪分析师"
    goal: "准确分析用户情绪状态和心理需求"
    backstory: "我是一个善解人意的AI助手..."
    llm_provider: "openai"
    personality_traits:
      语气特征: ["温和", "理解", "包容"]
      表达方式: ["简洁清晰", "情感丰富"]
```

### Task Configuration (`config/tasks.yaml`)
```yaml
task_templates:
  emotion_analysis:
    name: "情绪分析任务"
    description: |
      分析用户消息：{user_message}
      请提供详细的情绪分析...
    expected_output: "JSON格式的情绪分析结果"
    agent: "listener_agent"
    timeout: 15
```

## 🗂️ Project Structure

```
backend/
├── src/
│   ├── agents/           # Multi-agent implementations
│   │   ├── base_agent.py
│   │   ├── listener_agent.py
│   │   └── duck_style_agent.py
│   ├── api/              # FastAPI routes
│   │   └── chat.py
│   ├── config/           # Configuration management
│   │   └── settings.py
│   ├── models/           # Data models
│   │   ├── emotion.py
│   │   └── message.py
│   ├── services/         # Core services
│   │   ├── llm_service.py
│   │   └── crew_manager.py
│   └── utils/            # Utilities
│       └── config_loader.py
├── config/               # YAML configurations
│   ├── agents.yaml
│   └── tasks.yaml
├── main.py              # FastAPI application
├── start.py             # Startup script
└── requirements.txt     # Dependencies
```

## 🧪 Testing

### Health Check
```bash
# Ensure server is running and conda environment is activated
conda activate duck-therapy
curl http://localhost:8000/health
```

### Send Test Message
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "text": "我今天心情不太好",
    "session_id": "test-session",
    "workflow_type": "basic_chat_flow"
  }'
```

### Check LLM Providers
```bash
curl http://localhost:8000/health/llm
```

## 🔒 Safety Features

### Content Safety
- Crisis content detection (suicide, self-harm references)
- Medical advice filtering
- Inappropriate content handling
- Automatic safety response generation

### Data Privacy
- Session-based storage (no persistent user data)
- Configurable data retention
- Optional local LLM deployment (Ollama)

## 📊 Monitoring

### Health Monitoring
The system provides comprehensive health checks for:
- Agent availability and responsiveness
- LLM provider connectivity and performance
- Configuration validity
- System resource usage

### Performance Metrics
- Workflow execution time
- Success rates per agent/provider
- LLM provider usage statistics
- Error rates and patterns

## 🔧 Development

### Adding New Agents
1. Create agent class in `src/agents/`
2. Extend `BaseAgent` with required methods
3. Add configuration to `agents.yaml`
4. Register in `CrewManager`

### Custom Workflows
1. Define workflow in `tasks.yaml`
2. Implement workflow logic in `CrewManager`
3. Add API endpoint if needed

### LLM Provider Integration
1. Add provider to `llm_service.py`
2. Update settings configuration
3. Add health check support

## 🐛 Troubleshooting

### Environment Issues

**"conda: command not found"**
```bash
# Install Miniconda or Anaconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Or use package manager
# Ubuntu/Debian: sudo apt install conda
# macOS: brew install --cask miniconda
# Windows: Download from https://docs.conda.io/en/latest/miniconda.html
```

**"Environment activation failed"**
```bash
# Initialize conda for your shell
conda init

# Restart terminal and try again
conda activate duck-therapy

# Alternative: activate manually
source ~/miniconda3/etc/profile.d/conda.sh
conda activate duck-therapy
```

**"Package conflicts during installation"**
```bash
# Clean conda cache
conda clean --all

# Create fresh environment
conda remove -n duck-therapy --all
conda create -n duck-therapy python=3.11 -y
conda activate duck-therapy

# Install step by step
conda install -c conda-forge fastapi uvicorn pydantic loguru pyyaml -y
pip install --no-deps crewai langchain-openai langchain-anthropic langchain-ollama ollama
```

### Common Application Issues

**"Agent configuration not found"**
- Check `config/agents.yaml` exists and is valid YAML
- Verify agent names match exactly
- Ensure conda environment is activated

**"No LLM provider available"**
- Set at least one LLM provider API key
- Check provider connectivity with `/health/llm`
- Verify environment variables are set in activated conda environment

**"Task execution timeout"**
- Increase timeout in task configuration
- Check LLM provider performance
- Verify network connectivity

**"Import errors or module not found"**
```bash
# Verify environment is activated
conda info --envs
conda activate duck-therapy

# Check installed packages
pip list | grep crewai
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Logs
Logs are written to `logs/duck_therapy.log` with rotation.

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Ensure YAML configurations are valid

## 📄 License

This project is part of the Duck Therapy application suite.