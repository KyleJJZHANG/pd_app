# 心理鸭对话多智能体 PRD & 架构文档

## 一、产品需求文档（PRD）

### 1. 产品定位

心理鸭是一个以 IP（鸭鸭漫画形象）为核心的 **轻陪伴对话应用**，通过拟人化、疗愈风格的多智能体协作，实现：

* 情绪倾听与陪伴
* 简单的心理调节建议
* 漫画/视频素材的贴合式回应
* 每日对话小结与情绪足迹

### 2. 核心目标

* **降低使用门槛**：点开即可聊天
* **维持 IP 风格**：语言与插画统一
* **轻心理辅助**：提供正向心理学的工具（呼吸练习、正念练习、CBT重述）
* **形成闭环**：对话 → 情绪识别 → 建议 → 记忆沉淀 → 小结

### 3. 主要功能

1. **对话陪伴**

   * 即时聊天（鸭鸭语气）
   * 插入漫画/视频片段
2. **轻心理建议**

   * 情绪调节小练习
   * 正念/呼吸引导
3. **内容召回**

   * 从已有漫画/视频库中匹配内容
4. **小结生成**

   * 当日情绪趋势、关键词标签、温柔鼓励
5. **情绪足迹**

   * 保存到本地数据库，形成时间轴

---

## 二、技术架构文档

### 1. 技术栈

* **前端**：React + TypeScript + TailwindCSS + shadcn/ui（你已实现）
* **后端（可轻量化）**：FastAPI / Flask（REST接口层）
* **智能体框架**：CrewAI（或基于 LangChain 多Agent编排）
* **存储**：

  * 本地：IndexedDB（对话、足迹、记忆）
  * 静态内容：content.json 索引 + CDN漫画/视频资源
* **模型**：

  * LLM：GPT 系列 / 本地 LLM
  * 规则/关键词：情绪识别、内容匹配

---

### 2. 项目结构（建议）

```
duck-therapy-ai/
├── frontend/                  # 已实现的 React 前端
│   └── ...
├── backend/
│   ├── app.py                 # FastAPI 主入口
│   ├── agents/                # 多智能体定义
│   │   ├── listener_agent.py
│   │   ├── tips_agent.py
│   │   ├── recall_agent.py
│   │   ├── duckstyle_agent.py
│   │   └── report_agent.py
│   ├── tools/                 # 工具函数
│   │   ├── keyword_tag.py
│   │   ├── sentiment.py
│   │   └── content_index.py
│   ├── data/
│   │   └── content.json       # 漫画/视频索引
│   └── tests/
│       └── ...
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   └── diagrams/              # 类图/时序图
└── requirements.txt
```

---

### 3. 类图（Class Diagram）

```mermaid
classDiagram
  class Message {
    +string id
    +string role  // "user" | "duck"
    +string text
    +string panel?  // 漫画URL
    +string video?  // 视频URL
    +Date createdAt
  }

  class ListenerOutput {
    +sentiment: string
    +intensity: float
    +emotion_tags: string[]
    +topics: string[]
    +needs: string[]
  }

  class TherapyTip {
    +id: string
    +title: string
    +steps: string[]
    +duration_s: int
  }

  class ContentAsset {
    +id: string
    +type: string // "image"|"video"
    +url: string
    +tags: string[]
  }

  class Report {
    +tags: string[]
    +trend: string
    +summary: string
    +gentle_tip: string
  }

  Message --> ListenerOutput : 解析
  ListenerOutput --> TherapyTip : 生成建议
  ListenerOutput --> ContentAsset : 召回素材
  Message --> Report : 聚合生成
```

---

### 4. 时序图（Sequence Diagrams）

#### 单轮对话流程

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant L as ListenerAgent
  participant T as TherapyTipsAgent
  participant C as ContentRecallAgent
  participant D as DuckStyleAgent
  participant FE as Frontend

  U->>FE: 输入消息
  FE->>L: 传入消息 + 上下文
  L-->>FE: 情绪/关键词 JSON
  par 并行
    FE->>T: 请求轻心理建议
    FE->>C: 请求相关漫画/视频
  end
  T-->>FE: 返回步骤化建议
  C-->>FE: 返回漫画/视频
  FE->>D: 合并内容并润色为鸭鸭语气
  D-->>FE: 返回最终回复
  FE-->>U: 展示鸭鸭对话 + 插画
```

#### 每日小结流程

```mermaid
sequenceDiagram
  autonumber
  participant FE as Frontend
  participant R as ReportAgent
  participant DB as LocalDB

  FE->>DB: 读取今日消息
  FE->>R: 请求小结
  R-->>FE: 标签 + 趋势 + 温柔提示
  FE-->>U: 显示“今日小结”弹窗
```

---

## 三、迭代计划（高层）

* **MVP-0.1**：对话闭环（Listener + DuckStyle + 前端展示）
* **MVP-0.2**：接入漫画/视频召回（ContentRecall）
* **MVP-0.3**：加入 TherapyTips，输出可执行练习
* **MVP-0.4**：生成 Report（情绪足迹 + 今日小结）
* **MVP-0.5**：优化体验，灰度上线
