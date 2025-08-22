# 心理鸭后端开发指南

## 1. 开发规范和最佳实践

### 1.1 代码风格

#### Python 代码规范
- **PEP 8**: 遵循 Python 官方代码规范
- **类型注解**: 所有函数和方法必须添加类型注解
- **文档字符串**: 使用 Google 风格的 docstring

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

async def analyze_emotion(
    text: str, 
    context: Optional[List[str]] = None
) -> Dict[str, Any]:
    """分析文本情绪。
    
    Args:
        text: 要分析的文本内容
        context: 可选的上下文信息
        
    Returns:
        包含情绪分析结果的字典
        
    Raises:
        ValueError: 当文本为空时抛出
    """
    if not text.strip():
        raise ValueError("文本不能为空")
        
    # 实现逻辑...
    return {"sentiment": "positive", "confidence": 0.8}
```

#### 命名约定
```python
# 变量和函数：snake_case
user_message = "Hello"
def process_user_input():
    pass

# 类名：PascalCase
class EmotionAnalyzer:
    pass

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_MODEL = "gpt-4"

# 私有方法：前缀下划线
def _internal_helper():
    pass
```

### 1.2 项目结构规范

```
backend/
├── app.py                     # 应用入口
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量模板
├── pyproject.toml            # 项目配置
├── src/
     ├── app.py                     # FastAPI main application
     ├── __init__.py
     ├── agents/                    # CrewAI agents
     │   ├── __init__.py
     │   ├── base_agent.py         # Base agent with multi-LLM support
     │   ├── listener_agent.py     # Emotion analysis agent
     │   ├── duck_style_agent.py   # Duck personality agent
     │   ├── content_recall_agent.py # Content recommendation agent
     │   ├── therapy_tips_agent.py # Therapy guidance agent
     │   ├── report_agent.py       # Daily report agent
     │   └── crew_manager.py       # Agent orchestration
     ├── models/                   # Pydantic data models
     │   ├── __init__.py
     │   ├── message.py           # Chat message models
     │   ├── emotion.py           # Emotion analysis models
     │   ├── content.py           # Content asset models
     │   └── report.py            # Report models
     ├── api/                     # FastAPI routes
     │   ├── __init__.py
     │   ├── chat.py             # Chat endpoints
     │   ├── emotion.py          # Emotion analysis endpoints
     │   ├── content.py          # Content recommendation endpoints
     │   └── report.py           # Report generation endpoints
     ├── config/                  # Configuration
     │   ├── __init__.py
     │   ├── settings.py         # App settings with multi-LLM config
     │   ├── database.py         # Database configuration
     │   └── llm_config.py       # LLM provider configuration
     ├── services/               # Business logic
     │   ├── __init__.py
     │   ├── chat_service.py     # Chat orchestration
     │   ├── emotion_service.py  # Emotion analysis
     │   └── llm_service.py      # Multi-LLM management
     ├── tools/                  # CrewAI tools
     │   ├── __init__.py
     │   ├── emotion_analyzer.py # Emotion detection tool
     │   ├── content_matcher.py  # Content matching tool
     │   └── safety_checker.py   # Content safety tool
     └── utils/                  # Utilities
         ├── __init__.py
         ├── exceptions.py       # Custom exceptions
         └── helpers.py          # Helper functions
├── tests/                  # 测试文件
│   ├── __init__.py
│   ├── test_agents/        # 智能体测试
│   ├── test_api/          # API 测试
│   └── test_tools/        # 工具测试
├── data/                   # 数据文件
│   ├── content.json        # 内容索引
│   ├── emotion_keywords.json # 情绪关键词
│   └── therapy_tips.json   # 心理建议库
├── logs/                   # 日志文件
├── docs/                   # 文档
└── scripts/               # 脚本文件
    ├── init_db.py         # 数据库初始化
    └── load_content.py    # 内容加载
```

## 2. 智能体开发指南

### 2.1 基础智能体类

所有智能体都继承自基础智能体类：

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from crewai import Agent, Task
from pydantic import BaseModel

class BaseAgentInput(BaseModel):
    """智能体输入基类"""
    session_id: str
    timestamp: str
    
class BaseAgentOutput(BaseModel):
    """智能体输出基类"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )
    
    @abstractmethod
    async def process(self, input_data: BaseAgentInput) -> BaseAgentOutput:
        """处理输入数据，返回处理结果"""
        pass
    
    def _validate_input(self, input_data: BaseAgentInput) -> bool:
        """验证输入数据"""
        return True
    
    def _log_processing(self, input_data: BaseAgentInput, output: BaseAgentOutput):
        """记录处理日志"""
        pass
```

### 2.2 智能体实现示例

```python
from tools.emotion_analyzer import EmotionAnalyzer
from models.emotion import EmotionAnalysis, EmotionInput

class ListenerAgent(BaseAgent):
    """情绪识别智能体"""
    
    def __init__(self):
        super().__init__(
            name="listener",
            role="心理倾听专家",
            goal="准确识别用户的情绪状态和心理需求",
            backstory="""
            你是一位经验丰富的心理倾听专家，擅长从用户的文字表达中
            敏锐地捕捉情绪变化、识别关键主题，并评估用户的心理需求。
            """
        )
        self.emotion_tool = EmotionAnalyzer()
    
    async def process(self, input_data: EmotionInput) -> BaseAgentOutput:
        """处理情绪识别任务"""
        start_time = time.time()
        
        try:
            # 验证输入
            if not self._validate_input(input_data):
                return BaseAgentOutput(
                    success=False,
                    error="输入数据验证失败"
                )
            
            # 创建任务
            task = Task(
                description=f"""
                分析以下用户消息的情绪状态：
                消息内容：{input_data.text}
                上下文：{input_data.context or '无'}
                
                请提供：
                1. 情绪极性（正面/中性/负面）
                2. 情绪强度（0-1）
                3. 具体情绪标签
                4. 关键词提取
                5. 心理需求评估
                """,
                agent=self.agent,
                expected_output="JSON格式的情绪分析结果"
            )
            
            # 执行分析
            result = await self._execute_task(task, input_data)
            
            # 格式化输出
            emotion_analysis = EmotionAnalysis(**result)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return BaseAgentOutput(
                success=True,
                data=emotion_analysis.dict(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            return BaseAgentOutput(
                success=False,
                error=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    async def _execute_task(self, task: Task, input_data: EmotionInput) -> Dict[str, Any]:
        """执行具体的情绪分析任务"""
        # 使用工具进行情绪分析
        emotion_result = await self.emotion_tool.analyze(input_data.text)
        
        # 结合 LLM 进行深度分析
        llm_result = await self.agent.execute(task)
        
        # 合并结果
        return {
            **emotion_result,
            "llm_insights": llm_result
        }
```

### 2.3 智能体协调器

```python
from typing import List, Dict
import asyncio

class CrewManager:
    """智能体协调管理器"""
    
    def __init__(self):
        self.agents = {
            "listener": ListenerAgent(),
            "duck_style": DuckStyleAgent(),
            "content_recall": ContentRecallAgent(),
            "therapy_tips": TherapyTipsAgent(),
            "report": ReportAgent()
        }
        self.active_sessions = {}
    
    async def process_chat_message(
        self, 
        message: str, 
        session_id: str,
        context: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """处理聊天消息的主流程"""
        
        # 阶段1：情绪分析（必须首先完成）
        emotion_input = EmotionInput(
            text=message,
            session_id=session_id,
            context=context,
            timestamp=datetime.now().isoformat()
        )
        
        emotion_result = await self.agents["listener"].process(emotion_input)
        
        if not emotion_result.success:
            return {"error": "情绪分析失败", "details": emotion_result.error}
        
        # 阶段2：决定需要激活的智能体
        active_agents = self._determine_active_agents(emotion_result.data)
        
        # 阶段3：并行执行相关智能体
        parallel_tasks = []
        
        for agent_name in active_agents:
            if agent_name == "listener":
                continue  # 已经执行过
                
            agent_input = self._prepare_agent_input(
                agent_name, message, session_id, emotion_result.data
            )
            
            task = self.agents[agent_name].process(agent_input)
            parallel_tasks.append((agent_name, task))
        
        # 等待所有任务完成
        results = {"emotion_analysis": emotion_result.data}
        
        for agent_name, task in parallel_tasks:
            try:
                result = await task
                results[agent_name] = result.data if result.success else {"error": result.error}
            except Exception as e:
                results[agent_name] = {"error": str(e)}
        
        # 阶段4：整合最终回复
        final_response = await self._integrate_responses(results, session_id)
        
        return final_response
    
    def _determine_active_agents(self, emotion_data: Dict[str, Any]) -> List[str]:
        """根据情绪数据决定激活哪些智能体"""
        agents = ["duck_style"]  # 始终激活风格智能体
        
        # 基于情绪强度决定是否需要心理建议
        intensity = emotion_data.get("intensity", 0)
        sentiment = emotion_data.get("sentiment", "neutral")
        
        if intensity > 0.7 and sentiment == "negative":
            agents.append("therapy_tips")
        
        # 基于话题决定是否需要内容召回
        topics = emotion_data.get("topics", [])
        emotional_topics = ["孤独", "悲伤", "压力", "焦虑", "开心", "兴奋"]
        
        if any(topic in emotional_topics for topic in topics):
            agents.append("content_recall")
        
        return agents
    
    async def _integrate_responses(
        self, 
        results: Dict[str, Any], 
        session_id: str
    ) -> Dict[str, Any]:
        """整合各智能体的回复结果"""
        
        # 基础回复（来自 duck_style 智能体）
        duck_response = results.get("duck_style", {})
        base_reply = duck_response.get("text", "抱歉，我现在有点困惑，请稍后再试。")
        
        # 内容推荐（如果有）
        content_recommendations = results.get("content_recall", {})
        
        # 心理建议（如果有）
        therapy_tips = results.get("therapy_tips", {})
        
        # 构建最终回复
        final_response = {
            "text": base_reply,
            "emotion_analysis": results["emotion_analysis"],
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        # 添加媒体内容
        if content_recommendations.get("panels"):
            final_response["panel_url"] = content_recommendations["panels"][0]["url"]
        
        if content_recommendations.get("videos"):
            final_response["video_url"] = content_recommendations["videos"][0]["url"]
        
        # 添加心理建议
        if therapy_tips.get("primary_tip"):
            final_response["therapy_tip"] = therapy_tips["primary_tip"]
        
        return final_response
```

## 3. API 开发规范

### 3.1 FastAPI 路由结构

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# API 路由模块
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# 请求/响应模型
class ChatRequest(BaseModel):
    text: str
    session_id: str
    context: Optional[List[str]] = None
    
class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# 依赖注入
async def get_crew_manager() -> CrewManager:
    """获取智能体管理器实例"""
    return CrewManager()

# API 端点
@router.post("/messages", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    crew_manager: CrewManager = Depends(get_crew_manager)
):
    """发送聊天消息"""
    try:
        result = await crew_manager.process_chat_message(
            message=request.text,
            session_id=request.session_id,
            context=request.context
        )
        
        return ChatResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理消息时发生错误: {str(e)}"
        )
```

### 3.2 错误处理规范

```python
from fastapi import HTTPException
from utils.exceptions import (
    AgentProcessingError,
    ValidationError,
    ExternalServiceError
)

class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_agent_error(error: Exception) -> HTTPException:
        """处理智能体相关错误"""
        if isinstance(error, AgentProcessingError):
            return HTTPException(
                status_code=422,
                detail={
                    "code": "AGENT_PROCESSING_ERROR",
                    "message": str(error),
                    "agent": error.agent_name
                }
            )
        elif isinstance(error, ValidationError):
            return HTTPException(
                status_code=400,
                detail={
                    "code": "VALIDATION_ERROR", 
                    "message": str(error),
                    "field": error.field_name
                }
            )
        else:
            return HTTPException(
                status_code=500,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "内部服务器错误"
                }
            )

# 在路由中使用
@router.post("/messages")
async def send_message(request: ChatRequest):
    try:
        # 处理逻辑...
        pass
    except Exception as e:
        raise ErrorHandler.handle_agent_error(e)
```

## 4. 测试开发规范

### 4.1 单元测试

```python
import pytest
from unittest.mock import Mock, patch
from agents.listener_agent import ListenerAgent
from models.emotion import EmotionInput

class TestListenerAgent:
    """情绪识别智能体测试"""
    
    @pytest.fixture
    def listener_agent(self):
        """测试智能体实例"""
        return ListenerAgent()
    
    @pytest.fixture
    def sample_input(self):
        """示例输入数据"""
        return EmotionInput(
            text="今天心情不太好，工作压力很大",
            session_id="test_session",
            timestamp="2024-01-01T12:00:00Z"
        )
    
    @pytest.mark.asyncio
    async def test_process_negative_emotion(self, listener_agent, sample_input):
        """测试负面情绪识别"""
        result = await listener_agent.process(sample_input)
        
        assert result.success is True
        assert result.data is not None
        assert result.data["sentiment"] == "negative"
        assert "压力" in result.data["keywords"]
    
    @pytest.mark.asyncio
    async def test_process_empty_text(self, listener_agent):
        """测试空文本输入"""
        empty_input = EmotionInput(
            text="",
            session_id="test_session",
            timestamp="2024-01-01T12:00:00Z"
        )
        
        result = await listener_agent.process(empty_input)
        assert result.success is False
        assert "输入数据验证失败" in result.error
    
    @patch('agents.listener_agent.EmotionAnalyzer')
    @pytest.mark.asyncio
    async def test_tool_failure_handling(self, mock_analyzer, listener_agent, sample_input):
        """测试工具失败处理"""
        mock_analyzer.return_value.analyze.side_effect = Exception("工具错误")
        
        result = await listener_agent.process(sample_input)
        assert result.success is False
        assert "工具错误" in result.error
```

### 4.2 集成测试

```python
import pytest
from fastapi.testclient import TestClient
from app import app

class TestChatAPI:
    """聊天 API 集成测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)
    
    def test_send_message_success(self, client):
        """测试成功发送消息"""
        response = client.post("/api/v1/chat/messages", json={
            "text": "你好，鸭鸭！",
            "session_id": "test_session_123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "text" in data["data"]
        assert data["data"]["session_id"] == "test_session_123"
    
    def test_send_empty_message(self, client):
        """测试发送空消息"""
        response = client.post("/api/v1/chat/messages", json={
            "text": "",
            "session_id": "test_session_123"
        })
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """测试 WebSocket 连接"""
        from fastapi.testclient import TestClient
        
        with TestClient(app).websocket_connect("/ws/chat/test_session") as websocket:
            websocket.send_text("你好")
            data = websocket.receive_json()
            assert data["type"] == "duck_response"
```

### 4.3 性能测试

```python
import time
import asyncio
import pytest
from agents.crew_manager import CrewManager

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """测试响应时间"""
        crew_manager = CrewManager()
        
        start_time = time.time()
        result = await crew_manager.process_chat_message(
            message="测试消息",
            session_id="perf_test"
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 毫秒
        
        assert response_time < 5000  # 5秒内响应
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        crew_manager = CrewManager()
        
        # 创建10个并发请求
        tasks = []
        for i in range(10):
            task = crew_manager.process_chat_message(
                message=f"并发测试消息 {i}",
                session_id=f"concurrent_session_{i}"
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 所有请求都应该成功
        assert all(result is not None for result in results)
        
        # 并发处理应该比串行处理快
        total_time = (end_time - start_time) * 1000
        assert total_time < 10000  # 10秒内完成
```

## 5. 日志和监控

### 5.1 日志配置

```python
import logging
from loguru import logger
import sys

# 配置 loguru
logger.remove()  # 移除默认处理器

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 文件输出
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)

# 错误日志单独记录
logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",
    retention="90 days"
)
```

### 5.2 业务日志记录

```python
from functools import wraps
import time
from loguru import logger

def log_agent_processing(func):
    """智能体处理日志装饰器"""
    @wraps(func)
    async def wrapper(self, input_data, *args, **kwargs):
        agent_name = self.__class__.__name__
        session_id = getattr(input_data, 'session_id', 'unknown')
        
        logger.info(
            f"Agent processing started",
            extra={
                "agent": agent_name,
                "session_id": session_id,
                "input_length": len(getattr(input_data, 'text', ''))
            }
        )
        
        start_time = time.time()
        try:
            result = await func(self, input_data, *args, **kwargs)
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Agent processing completed",
                extra={
                    "agent": agent_name,
                    "session_id": session_id,
                    "processing_time_ms": processing_time,
                    "success": result.success
                }
            )
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(
                f"Agent processing failed",
                extra={
                    "agent": agent_name,
                    "session_id": session_id,
                    "processing_time_ms": processing_time,
                    "error": str(e)
                }
            )
            raise
    
    return wrapper

# 使用示例
class ListenerAgent(BaseAgent):
    @log_agent_processing
    async def process(self, input_data: EmotionInput) -> BaseAgentOutput:
        # 处理逻辑...
        pass
```

### 5.3 性能监控

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义监控指标
REQUEST_COUNT = Counter('chat_requests_total', 'Total chat requests', ['endpoint'])
REQUEST_DURATION = Histogram('chat_request_duration_seconds', 'Chat request duration')
ACTIVE_SESSIONS = Gauge('active_sessions', 'Number of active chat sessions')
AGENT_PROCESSING_TIME = Histogram(
    'agent_processing_duration_seconds', 
    'Agent processing duration', 
    ['agent_name']
)

class MetricsCollector:
    """监控指标收集器"""
    
    @staticmethod
    def record_request(endpoint: str):
        """记录请求计数"""
        REQUEST_COUNT.labels(endpoint=endpoint).inc()
    
    @staticmethod
    def record_request_duration(duration: float):
        """记录请求耗时"""
        REQUEST_DURATION.observe(duration)
    
    @staticmethod
    def record_agent_processing(agent_name: str, duration: float):
        """记录智能体处理耗时"""
        AGENT_PROCESSING_TIME.labels(agent_name=agent_name).observe(duration)
    
    @staticmethod
    def update_active_sessions(count: int):
        """更新活跃会话数"""
        ACTIVE_SESSIONS.set(count)

# 在 API 路由中使用
@router.post("/messages")
async def send_message(request: ChatRequest):
    start_time = time.time()
    
    try:
        MetricsCollector.record_request("chat_messages")
        
        # 处理逻辑...
        result = await process_message(request)
        
        duration = time.time() - start_time
        MetricsCollector.record_request_duration(duration)
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        MetricsCollector.record_request_duration(duration)
        raise
```

## 6. 安全规范

### 6.1 输入验证

```python
from pydantic import BaseModel, validator
import re

class ChatRequest(BaseModel):
    text: str
    session_id: str
    
    @validator('text')
    def validate_text(cls, v):
        """验证文本输入"""
        if not v or not v.strip():
            raise ValueError('消息内容不能为空')
        
        if len(v) > 2000:
            raise ValueError('消息长度不能超过2000字符')
        
        # 检查恶意内容
        malicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('检测到不安全的内容')
        
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """验证会话ID"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('会话ID格式不正确')
        
        if len(v) > 100:
            raise ValueError('会话ID过长')
        
        return v
```

### 6.2 敏感信息过滤

```python
import re
from typing import List

class SafetyChecker:
    """安全检查器"""
    
    def __init__(self):
        # 敏感信息模式
        self.sensitive_patterns = {
            'phone': r'1[3-9]\d{9}',
            'id_card': r'\d{15}|\d{18}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'credit_card': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
        }
        
        # 不当内容关键词
        self.inappropriate_keywords = [
            '自杀', '自残', '死亡', '暴力', '违法'
        ]
    
    def check_sensitive_info(self, text: str) -> Dict[str, List[str]]:
        """检查敏感信息"""
        found_info = {}
        
        for info_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found_info[info_type] = matches
        
        return found_info
    
    def check_inappropriate_content(self, text: str) -> List[str]:
        """检查不当内容"""
        found_keywords = []
        
        for keyword in self.inappropriate_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def sanitize_output(self, text: str) -> str:
        """清理输出内容"""
        # 移除可能的敏感信息
        for pattern in self.sensitive_patterns.values():
            text = re.sub(pattern, '[已屏蔽]', text)
        
        return text

# 在智能体中使用
class DuckStyleAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.safety_checker = SafetyChecker()
    
    async def process(self, input_data):
        # 检查输入安全性
        sensitive_info = self.safety_checker.check_sensitive_info(input_data.text)
        if sensitive_info:
            logger.warning(f"检测到敏感信息: {sensitive_info}")
        
        inappropriate = self.safety_checker.check_inappropriate_content(input_data.text)
        if inappropriate:
            logger.warning(f"检测到不当内容: {inappropriate}")
            
            # 返回安全提示
            return BaseAgentOutput(
                success=True,
                data={
                    "text": "鸭鸭注意到你可能遇到了一些困难。如果需要专业帮助，建议联系心理健康专家。",
                    "safety_triggered": True
                }
            )
        
        # 正常处理...
        result = await self._normal_processing(input_data)
        
        # 清理输出
        if result.success and result.data:
            result.data["text"] = self.safety_checker.sanitize_output(result.data["text"])
        
        return result
```

## 7. 部署准备

### 7.1 Docker 配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  duck-therapy-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/duck_therapy
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: duck_therapy
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 7.2 环境配置

```python
# config/settings.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    app_name: str = "Duck Therapy Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str
    
    # LLM 配置
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 安全配置
    secret_key: str
    allowed_origins: List[str] = ["*"]
    
    # 缓存配置
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = True
    
    # 日志配置
    log_level: str = "INFO"
    log_file_path: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局设置实例
settings = Settings()
```

这个开发指南为团队提供了完整的开发规范和最佳实践，确保代码质量和项目的可维护性。开发者可以按照这个指南进行智能体和 API 的开发工作。