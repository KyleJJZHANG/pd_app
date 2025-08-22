# 心理鸭后端 API 文档

## 1. API 概述

心理鸭后端提供 RESTful API 和 WebSocket 接口，支持实时聊天、情绪分析、内容推荐和报告生成等功能。所有 API 遵循 RESTful 设计原则，使用 JSON 格式进行数据交换。

### 1.1 API 基础信息

- **Base URL**: `http://localhost:8000/api/v1` (开发环境)
- **Content-Type**: `application/json`
- **字符编码**: UTF-8
- **API 版本**: v1

### 1.2 认证方式

目前阶段采用 Session-based 认证，后续可扩展为 JWT 认证。

```http
# 请求头示例
Content-Type: application/json
X-Session-ID: {session_id}
```

## 2. 数据模型

### 2.1 基础数据结构

#### Message（消息模型）
```json
{
  "id": "string",                    // 消息唯一标识
  "role": "user" | "duck",          // 消息角色
  "text": "string",                 // 消息内容
  "emotion_tags": ["string"],       // 情绪标签（可选）
  "emotion_intensity": 0.0,         // 情绪强度 0.0-1.0（可选）
  "panel_url": "string",           // 漫画URL（可选）
  "video_url": "string",           // 视频URL（可选）
  "created_at": "2024-01-01T12:00:00Z",
  "session_id": "string"
}
```

#### EmotionAnalysis（情绪分析结果）
```json
{
  "sentiment": "positive" | "neutral" | "negative",
  "intensity": 0.8,                // 情绪强度
  "primary_emotions": ["开心", "兴奋"],
  "secondary_emotions": ["期待"],
  "keywords": ["工作", "成功", "团队"],
  "topics": ["职业发展", "团队合作"],
  "psychological_needs": ["成就感", "认可"],
  "urgency_level": 2,              // 1-5级紧急程度
  "support_type": "celebration",   // 所需支持类型
  "confidence_score": 0.85         // 分析置信度
}
```

#### ContentRecommendation（内容推荐）
```json
{
  "panels": [
    {
      "id": "panel_001",
      "url": "/panels/celebration_duck.jpg",
      "title": "庆祝成功的鸭鸭",
      "relevance_score": 0.9
    }
  ],
  "videos": [
    {
      "id": "video_001", 
      "url": "/videos/happy_dance.mp4",
      "title": "开心小舞蹈",
      "duration": 15,
      "relevance_score": 0.8
    }
  ]
}
```

#### TherapyTip（心理建议）
```json
{
  "id": "breathing_001",
  "category": "breathing",
  "title": "4-7-8呼吸法",
  "description": "一种简单有效的放松呼吸技巧",
  "steps": [
    "舒适地坐好，背部挺直",
    "用鼻子吸气4秒",
    "屏住呼吸7秒",
    "用嘴巴呼气8秒"
  ],
  "duration_minutes": 3,
  "difficulty": "easy",
  "applicable_emotions": ["焦虑", "紧张"]
}
```

### 2.2 通用响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据内容
  },
  "message": "操作成功",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "field": "text",
      "reason": "消息内容不能为空"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 3. 聊天相关 API

### 3.1 发送聊天消息

**端点**: `POST /api/v1/chat/messages`

发送用户消息并获取鸭鸭回复。

#### 请求参数
```json
{
  "text": "今天工作很顺利，成功完成了项目演示！",
  "session_id": "session_123456",
  "context": {
    "include_content": true,      // 是否包含内容推荐
    "include_therapy": false,     // 是否包含心理建议
    "response_style": "standard"  // 回复风格：standard | detailed | brief
  }
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "user_message": {
      "id": "msg_001",
      "role": "user",
      "text": "今天工作很顺利，成功完成了项目演示！",
      "created_at": "2024-01-01T12:00:00Z",
      "session_id": "session_123456"
    },
    "duck_response": {
      "id": "msg_002",
      "role": "duck",
      "text": "哇，太棒了！鸭鸭为你感到开心呢～能成功完成项目演示真的很不容易，你一定付出了很多努力。这种成就感是不是很棒呀？记得给自己一些小奖励哦！",
      "panel_url": "/panels/celebration_duck.jpg",
      "created_at": "2024-01-01T12:00:10Z",
      "session_id": "session_123456"
    },
    "emotion_analysis": {
      "sentiment": "positive",
      "intensity": 0.85,
      "primary_emotions": ["开心", "自豪"],
      "keywords": ["工作", "成功", "项目", "演示"],
      "confidence_score": 0.9
    },
    "processing_time_ms": 1200
  }
}
```

### 3.2 获取聊天历史

**端点**: `GET /api/v1/chat/history/{session_id}`

获取指定会话的聊天历史记录。

#### 查询参数
- `limit`: 返回消息数量限制（默认：50，最大：200）
- `offset`: 偏移量，用于分页（默认：0）
- `since`: 获取指定时间之后的消息（ISO 8601 格式）

#### 响应示例
```json
{
  "success": true,
  "data": {
    "messages": [
      // Message 对象数组
    ],
    "total_count": 25,
    "has_more": false,
    "pagination": {
      "limit": 50,
      "offset": 0,
      "total_pages": 1
    }
  }
}
```

### 3.3 创建新会话

**端点**: `POST /api/v1/chat/sessions`

创建新的聊天会话。

#### 请求参数
```json
{
  "user_id": "user_123",          // 可选，用户标识
  "metadata": {                   // 可选，会话元数据
    "device": "mobile",
    "platform": "ios"
  }
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "session_id": "session_789",
    "created_at": "2024-01-01T12:00:00Z",
    "status": "active"
  }
}
```

## 4. 情绪分析 API

### 4.1 获取情绪分析详情

**端点**: `GET /api/v1/emotions/analysis/{session_id}`

获取指定会话的详细情绪分析结果。

#### 查询参数
- `period`: 分析时间段 `today` | `week` | `month`（默认：today）
- `include_trends`: 是否包含趋势分析（默认：false）

#### 响应示例
```json
{
  "success": true,
  "data": {
    "summary": {
      "dominant_emotion": "开心",
      "average_intensity": 0.7,
      "positive_ratio": 0.8,
      "total_messages": 15
    },
    "emotion_distribution": {
      "开心": 0.4,
      "平静": 0.3,
      "兴奋": 0.2,
      "紧张": 0.1
    },
    "daily_trends": [
      {
        "date": "2024-01-01",
        "average_sentiment": 0.75,
        "message_count": 8
      }
    ],
    "insights": [
      "今天的情绪整体比较积极",
      "在工作话题上表现出较高的成就感"
    ]
  }
}
```

### 4.2 单条消息情绪分析

**端点**: `POST /api/v1/emotions/analyze`

对单条消息进行情绪分析（独立分析，不依赖会话上下文）。

#### 请求参数
```json
{
  "text": "最近工作压力有点大，感觉有些疲惫",
  "context": {
    "analyze_depth": "detailed"   // basic | standard | detailed
  }
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "emotion_analysis": {
      "sentiment": "negative",
      "intensity": 0.6,
      "primary_emotions": ["疲惫", "压力"],
      "secondary_emotions": ["担忧"],
      "keywords": ["工作", "压力", "疲惫"],
      "topics": ["工作压力", "身心健康"],
      "psychological_needs": ["休息", "支持", "减压"],
      "urgency_level": 3,
      "support_type": "stress_relief",
      "confidence_score": 0.88
    },
    "suggestions": {
      "immediate_support": "看起来你需要一些放松的时间",
      "therapy_recommendation": true,
      "content_recommendation": true
    }
  }
}
```

## 5. 内容推荐 API

### 5.1 获取内容推荐

**端点**: `POST /api/v1/content/recommend`

基于情绪状态获取相关的漫画和视频推荐。

#### 请求参数
```json
{
  "emotion_analysis": {
    "sentiment": "negative",
    "primary_emotions": ["压力", "疲惫"],
    "intensity": 0.6
  },
  "preferences": {
    "content_types": ["panel", "video"],  // 可选，指定内容类型
    "max_items": 5,                       // 最大推荐数量
    "duration_preference": "short"        // short | medium | long（仅视频）
  },
  "session_id": "session_123"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "recommendations": {
      "panels": [
        {
          "id": "panel_comfort_01",
          "url": "/panels/gentle_hug.jpg",
          "title": "温暖的拥抱",
          "tags": ["安慰", "拥抱", "温暖"],
          "relevance_score": 0.95,
          "emotion_match": ["疲惫", "需要安慰"]
        }
      ],
      "videos": [
        {
          "id": "video_relax_01",
          "url": "/videos/breathing_exercise.mp4", 
          "title": "简单呼吸练习",
          "duration": 120,
          "tags": ["放松", "呼吸", "减压"],
          "relevance_score": 0.92,
          "emotion_match": ["压力", "紧张"]
        }
      ]
    },
    "match_explanation": "基于你当前的压力状态，推荐一些能帮助放松的内容",
    "total_matches": 8,
    "recommendation_id": "rec_456"
  }
}
```

### 5.2 内容反馈

**端点**: `POST /api/v1/content/feedback`

用户对推荐内容的反馈，用于优化推荐算法。

#### 请求参数
```json
{
  "recommendation_id": "rec_456",
  "content_id": "panel_comfort_01",
  "feedback_type": "helpful",        // helpful | not_helpful | inappropriate
  "rating": 4,                       // 1-5 星评分（可选）
  "comment": "很温暖的图片，看了心情好多了"  // 可选
}
```

## 6. 心理建议 API

### 6.1 获取心理建议

**端点**: `POST /api/v1/therapy/tips`

基于用户情绪状态提供个性化的心理调节建议。

#### 请求参数
```json
{
  "emotion_analysis": {
    "sentiment": "negative",
    "primary_emotions": ["焦虑", "紧张"],
    "intensity": 0.8,
    "psychological_needs": ["放松", "减压"]
  },
  "user_preferences": {
    "experience_level": "beginner",   // beginner | intermediate | advanced
    "time_available": 5,              // 可用时间（分钟）
    "preferred_methods": ["breathing", "mindfulness"]
  },
  "session_id": "session_123"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "primary_tip": {
      "id": "breathing_478",
      "category": "breathing",
      "title": "快速放松呼吸法",
      "description": "在焦虑时可以快速使用的呼吸技巧",
      "steps": [
        "找一个安静的地方坐下或站立",
        "慢慢用鼻子吸气，数到4",
        "屏住呼吸，数到4", 
        "慢慢用嘴呼气，数到6",
        "重复这个过程5次"
      ],
      "duration_minutes": 3,
      "difficulty": "easy",
      "effectiveness_for_emotions": {
        "焦虑": 0.9,
        "紧张": 0.85
      }
    },
    "alternative_tips": [
      // 其他可选建议
    ],
    "follow_up_suggestions": [
      "练习后观察身体的放松感受",
      "如果继续感到焦虑，可以尝试正念冥想"
    ],
    "safety_notes": [
      "如果在练习过程中感到头晕，请停止并正常呼吸",
      "持续的严重焦虑建议寻求专业帮助"
    ]
  }
}
```

### 6.2 练习记录

**端点**: `POST /api/v1/therapy/practice`

记录用户完成的心理练习。

#### 请求参数
```json
{
  "tip_id": "breathing_478",
  "session_id": "session_123", 
  "completion_status": "completed",  // completed | partial | skipped
  "duration_actual": 4,              // 实际练习时长（分钟）
  "effectiveness_rating": 4,         // 1-5 效果评分
  "mood_before": 0.3,               // 练习前情绪状态 0-1
  "mood_after": 0.7,                // 练习后情绪状态 0-1
  "notes": "感觉放松了很多，呼吸变得更平稳"
}
```

## 7. 报告生成 API

### 7.1 生成每日报告

**端点**: `GET /api/v1/reports/daily/{session_id}`

生成指定会话的每日情绪报告。

#### 查询参数
- `date`: 指定日期（YYYY-MM-DD 格式，默认今天）
- `include_trends`: 是否包含趋势对比（默认：true）
- `language`: 报告语言（默认：zh-CN）

#### 响应示例
```json
{
  "success": true,
  "data": {
    "report": {
      "date": "2024-01-01",
      "summary": {
        "total_interactions": 12,
        "dominant_emotion": "开心",
        "emotion_stability": 0.8,
        "positive_moments": 8,
        "growth_indicators": ["表达更积极", "主动分享成就"]
      },
      "emotion_journey": [
        {
          "time": "09:00",
          "emotion": "平静",
          "intensity": 0.6,
          "trigger": "morning_routine"
        },
        {
          "time": "14:30", 
          "emotion": "兴奋",
          "intensity": 0.9,
          "trigger": "work_achievement"
        }
      ],
      "key_topics": {
        "工作": 0.4,
        "人际关系": 0.3,
        "个人成长": 0.2,
        "休闲娱乐": 0.1
      },
      "achievements": [
        "今天情绪整体很稳定",
        "在工作上表现出很强的成就感",
        "主动分享了积极的经历"
      ],
      "gentle_suggestions": [
        "继续保持这种积极的状态",
        "记得在忙碌时也要关照自己的感受",
        "可以尝试记录这些美好的时刻"
      ],
      "duck_encouragement": "亲爱的朋友，今天的你闪闪发光呢！鸭鸭看到你的努力和成长，真的很为你开心。记得给自己一个大大的拥抱哦～"
    },
    "comparison": {
      "vs_yesterday": {
        "emotion_improvement": 0.15,
        "interaction_increase": 2,
        "positivity_change": "+12%"
      },
      "vs_week_average": {
        "stability_score": "+0.1",
        "engagement_level": "高于平均"
      }
    }
  }
}
```

### 7.2 生成周报告

**端点**: `GET /api/v1/reports/weekly/{session_id}`

生成指定会话的周情绪报告。

#### 查询参数
- `week_start`: 周开始日期（YYYY-MM-DD 格式）
- `include_daily_breakdown`: 是否包含每日详细数据

#### 响应示例
```json
{
  "success": true,
  "data": {
    "week_summary": {
      "period": "2024-01-01 to 2024-01-07",
      "total_interactions": 84,
      "average_daily_mood": 0.72,
      "mood_trend": "improving",
      "most_active_day": "Wednesday",
      "emotional_growth": [
        "表达情绪更加细腻",
        "开始主动寻求建议",
        "对积极事件的感受更深"
      ]
    },
    "daily_breakdown": [
      {
        "date": "2024-01-01",
        "mood_score": 0.75,
        "interaction_count": 12,
        "highlight": "成功完成重要项目"
      }
      // ... 其他日期
    ],
    "patterns_insights": {
      "peak_mood_times": ["14:00-16:00", "19:00-21:00"],
      "common_stress_triggers": ["工作压力", "人际冲突"],
      "effective_coping_strategies": ["深呼吸", "与鸭鸭聊天"],
      "improvement_areas": ["睡眠质量", "压力管理"]
    }
  }
}
```

## 8. WebSocket 实时通信

### 8.1 连接建立

**端点**: `ws://localhost:8000/ws/chat/{session_id}`

建立 WebSocket 连接进行实时聊天。

#### 连接参数
- `session_id`: 会话标识符（必需）
- `user_id`: 用户标识符（可选）

#### 连接示例
```javascript
const websocket = new WebSocket('ws://localhost:8000/ws/chat/session_123');

websocket.onopen = function(event) {
    console.log('WebSocket 连接已建立');
};

websocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};
```

### 8.2 消息格式

#### 发送消息格式
```json
{
  "type": "user_message",
  "data": {
    "text": "你好，鸭鸭！",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 接收消息格式
```json
{
  "type": "duck_response",
  "data": {
    "message": {
      "id": "msg_001",
      "text": "你好呀！很高兴见到你～",
      "panel_url": "/panels/greeting.jpg"
    },
    "emotion_analysis": {
      "sentiment": "positive",
      "intensity": 0.8
    },
    "processing_time_ms": 800
  }
}
```

#### 系统消息格式
```json
{
  "type": "system_notification",
  "data": {
    "message": "已为你生成今日情绪报告",
    "action": "report_generated",
    "report_id": "report_001"
  }
}
```

## 9. 错误处理

### 9.1 HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

### 9.2 错误代码

```json
{
  "error_codes": {
    "VALIDATION_ERROR": "请求参数验证失败",
    "SESSION_NOT_FOUND": "会话不存在",
    "EMOTION_ANALYSIS_FAILED": "情绪分析失败",
    "CONTENT_NOT_AVAILABLE": "内容不可用",
    "LLM_SERVICE_ERROR": "大语言模型服务错误",
    "RATE_LIMIT_EXCEEDED": "请求频率超限",
    "AGENT_TIMEOUT": "智能体处理超时"
  }
}
```

### 9.3 重试机制

客户端应实现指数退避重试策略：

```javascript
async function retryRequest(requestFn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

## 10. 限流和配额

### 10.1 请求限制

- **聊天 API**: 60 请求/分钟
- **情绪分析 API**: 30 请求/分钟  
- **内容推荐 API**: 20 请求/分钟
- **报告生成 API**: 10 请求/分钟

### 10.2 响应头

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## 11. 版本控制

API 采用 URL 路径版本控制：

- `v1`: 当前稳定版本
- `v2`: 下一个主要版本（开发中）

版本兼容性策略：
- 向后兼容的变更在同一版本内发布
- 破坏性变更需要新版本号
- 旧版本至少维护6个月

## 12. SDK 和示例

### 12.1 JavaScript SDK 示例

```javascript
// Duck Therapy API 客户端
class DuckTherapyClient {
  constructor(baseUrl, sessionId) {
    this.baseUrl = baseUrl;
    this.sessionId = sessionId;
  }

  async sendMessage(text) {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': this.sessionId
      },
      body: JSON.stringify({ text, session_id: this.sessionId })
    });
    return response.json();
  }

  async getEmotionAnalysis(period = 'today') {
    const response = await fetch(
      `${this.baseUrl}/api/v1/emotions/analysis/${this.sessionId}?period=${period}`
    );
    return response.json();
  }

  async getDailyReport(date = null) {
    const dateParam = date ? `?date=${date}` : '';
    const response = await fetch(
      `${this.baseUrl}/api/v1/reports/daily/${this.sessionId}${dateParam}`
    );
    return response.json();
  }
}

// 使用示例
const client = new DuckTherapyClient('http://localhost:8000', 'session_123');

// 发送消息
const response = await client.sendMessage('今天心情不太好');
console.log(response.data.duck_response.text);

// 获取情绪分析
const emotions = await client.getEmotionAnalysis('today');
console.log(emotions.data.summary);
```

这个 API 文档为前端开发者提供了完整的后端接口规范，确保前后端能够顺利集成和协作。