# 前后端集成指南

## 1. 集成概述

本文档详细说明如何将现有的 React 前端应用与新开发的 CrewAI 后端服务进行集成。前端目前使用 localStorage 进行数据存储，需要逐步迁移到后端 API 调用。

### 1.1 集成策略

- **渐进式迁移**：保持现有功能可用，逐步替换为 API 调用
- **向后兼容**：提供降级机制，API 不可用时回退到本地存储
- **性能优化**：合理使用缓存，减少不必要的 API 调用
- **用户体验**：平滑过渡，用户无感知切换

### 1.2 技术架构对比

**当前架构（前端只）**：
```
React App → StorageService → localStorage
```

**目标架构（前后端分离）**：
```
React App → ApiService → Backend API → CrewAI Agents
             ↓ (fallback)
           StorageService → localStorage
```

## 2. API 客户端设计

### 2.1 API 客户端基础类

```typescript
// src/services/api/ApiClient.ts
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  useCache?: boolean;
  fallbackToLocal?: boolean;
}

export class ApiClient {
  private baseUrl: string;
  private sessionId: string;
  
  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
    this.sessionId = this.getOrCreateSessionId();
  }
  
  private getOrCreateSessionId(): string {
    let sessionId = localStorage.getItem('duck_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('duck_session_id', sessionId);
    }
    return sessionId;
  }
  
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    config: ApiRequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const { timeout = 10000, retries = 3, useCache = false } = config;
    
    // 检查缓存
    if (useCache && options.method === 'GET') {
      const cached = this.getFromCache(endpoint);
      if (cached) return cached;
    }
    
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'X-Session-ID': this.sessionId,
    };
    
    const requestOptions: RequestInit = {
      ...options,
      headers: { ...defaultHeaders, ...options.headers },
    };
    
    // 实现重试机制
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result: ApiResponse<T> = await response.json();
        
        // 缓存成功响应
        if (useCache && result.success) {
          this.setCache(endpoint, result);
        }
        
        return result;
        
      } catch (error) {
        console.warn(`API request attempt ${attempt} failed:`, error);
        
        if (attempt === retries) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            timestamp: new Date().toISOString(),
          };
        }
        
        // 指数退避
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
    
    // 不应该到这里，但为了类型安全
    return {
      success: false,
      error: 'Max retries exceeded',
      timestamp: new Date().toISOString(),
    };
  }
  
  private getFromCache(key: string): ApiResponse<any> | null {
    try {
      const cached = sessionStorage.getItem(`api_cache_${key}`);
      if (!cached) return null;
      
      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - new Date(timestamp).getTime();
      
      // 缓存5分钟有效
      if (age < 5 * 60 * 1000) {
        return data;
      }
      
      sessionStorage.removeItem(`api_cache_${key}`);
      return null;
    } catch {
      return null;
    }
  }
  
  private setCache(key: string, data: ApiResponse<any>): void {
    try {
      sessionStorage.setItem(`api_cache_${key}`, JSON.stringify({
        data,
        timestamp: new Date().toISOString(),
      }));
    } catch {
      // 忽略缓存错误
    }
  }
}
```

### 2.2 聊天 API 服务

```typescript
// src/services/api/ChatApiService.ts
import { ApiClient, ApiResponse } from './ApiClient';
import { Message } from '../data';

export interface ChatRequest {
  text: string;
  session_id: string;
  context?: string[];
}

export interface ChatResponse {
  user_message: Message;
  duck_response: Message;
  emotion_analysis: {
    sentiment: 'positive' | 'neutral' | 'negative';
    intensity: number;
    primary_emotions: string[];
    keywords: string[];
  };
  processing_time_ms: number;
}

export class ChatApiService {
  private apiClient: ApiClient;
  
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }
  
  async sendMessage(
    text: string, 
    context?: string[]
  ): Promise<ApiResponse<ChatResponse>> {
    return this.apiClient.request<ChatResponse>('/chat/messages', {
      method: 'POST',
      body: JSON.stringify({
        text,
        session_id: this.apiClient['sessionId'],
        context,
      }),
    }, {
      fallbackToLocal: true,
      retries: 2,
    });
  }
  
  async getChatHistory(
    limit: number = 50,
    offset: number = 0
  ): Promise<ApiResponse<{ messages: Message[]; total_count: number }>> {
    const sessionId = this.apiClient['sessionId'];
    return this.apiClient.request(
      `/chat/history/${sessionId}?limit=${limit}&offset=${offset}`,
      { method: 'GET' },
      { useCache: true, fallbackToLocal: true }
    );
  }
}
```

### 2.3 情绪分析 API 服务

```typescript
// src/services/api/EmotionApiService.ts
export interface EmotionAnalysisResponse {
  summary: {
    dominant_emotion: string;
    average_intensity: number;
    positive_ratio: number;
    total_messages: number;
  };
  emotion_distribution: Record<string, number>;
  daily_trends: Array<{
    date: string;
    average_sentiment: number;
    message_count: number;
  }>;
  insights: string[];
}

export class EmotionApiService {
  private apiClient: ApiClient;
  
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }
  
  async getEmotionAnalysis(
    period: 'today' | 'week' | 'month' = 'today'
  ): Promise<ApiResponse<EmotionAnalysisResponse>> {
    const sessionId = this.apiClient['sessionId'];
    return this.apiClient.request(
      `/emotions/analysis/${sessionId}?period=${period}`,
      { method: 'GET' },
      { useCache: true, fallbackToLocal: true }
    );
  }
  
  async analyzeSingleMessage(
    text: string
  ): Promise<ApiResponse<any>> {
    return this.apiClient.request('/emotions/analyze', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }
}
```

## 3. 混合服务层设计

### 3.1 混合聊天服务

```typescript
// src/services/HybridChatService.ts
import { StorageService } from './storage';
import { ChatApiService } from './api/ChatApiService';
import { EmotionAnalyzer } from './emotionAnalyzer';
import { Message } from '../data';

export class HybridChatService {
  private apiService: ChatApiService;
  private storageService: StorageService;
  private emotionAnalyzer: EmotionAnalyzer;
  private isOnline: boolean = true;
  
  constructor(
    apiService: ChatApiService,
    storageService: StorageService,
    emotionAnalyzer: EmotionAnalyzer
  ) {
    this.apiService = apiService;
    this.storageService = storageService;
    this.emotionAnalyzer = emotionAnalyzer;
    
    // 监听网络状态
    this.setupNetworkMonitoring();
  }
  
  async sendMessage(text: string): Promise<Message> {
    // 先保存用户消息
    const userMessage: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      text,
      createdAt: new Date(),
    };
    
    // 立即保存到本地
    this.storageService.addMessage(userMessage);
    
    try {
      // 尝试调用 API
      if (this.isOnline) {
        const response = await this.apiService.sendMessage(text, this.getRecentContext());
        
        if (response.success && response.data) {
          const duckResponse = response.data.duck_response;
          
          // 保存 API 返回的回复
          this.storageService.addMessage(duckResponse);
          
          // 保存情绪分析结果
          this.storageService.saveEmotionAnalysis(
            userMessage.id,
            response.data.emotion_analysis
          );
          
          return duckResponse;
        }
      }
      
      // API 失败或离线，使用本地逻辑
      return this.generateLocalResponse(userMessage);
      
    } catch (error) {
      console.warn('API 调用失败，使用本地响应:', error);
      return this.generateLocalResponse(userMessage);
    }
  }
  
  private async generateLocalResponse(userMessage: Message): Promise<Message> {
    // 使用本地情绪分析
    const emotion = await this.emotionAnalyzer.analyzeEmotion(userMessage.text);
    
    // 生成本地回复（简化版）
    const localResponse = this.generateDuckResponse(userMessage.text, emotion);
    
    const duckMessage: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: 'duck',
      text: localResponse.text,
      panelUrl: localResponse.panel,
      createdAt: new Date(),
    };
    
    this.storageService.addMessage(duckMessage);
    return duckMessage;
  }
  
  private generateDuckResponse(text: string, emotion: any): { text: string; panel?: string } {
    // 基于情绪生成简单回复
    const responses = {
      positive: [
        "哇，听起来你心情很好呢！鸭鸭也为你开心～",
        "太棒了！你的快乐让鸭鸭也感到温暖。",
      ],
      negative: [
        "鸭鸭感受到了你的情绪，想给你一个温暖的拥抱。",
        "遇到困难时，记得鸭鸭一直在这里陪着你哦。",
      ],
      neutral: [
        "嗯嗯，鸭鸭在认真听你说话呢。",
        "谢谢你和鸭鸭分享这些，我会一直陪着你的。",
      ],
    };
    
    const sentiment = emotion.sentiment || 'neutral';
    const responseList = responses[sentiment] || responses.neutral;
    const randomResponse = responseList[Math.floor(Math.random() * responseList.length)];
    
    return {
      text: randomResponse,
      panel: sentiment === 'positive' ? '/panels/happy_duck.jpg' : 
             sentiment === 'negative' ? '/panels/comfort_duck.jpg' : undefined,
    };
  }
  
  private getRecentContext(): string[] {
    const messages = this.storageService.getMessages();
    return messages
      .slice(-6) // 最近6条消息
      .map(m => `${m.role}: ${m.text}`);
  }
  
  private setupNetworkMonitoring(): void {
    // 监听网络状态变化
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.syncWithServer();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
    
    // 定期检查 API 可用性
    setInterval(() => this.checkApiHealth(), 30000);
  }
  
  private async checkApiHealth(): Promise<void> {
    try {
      const response = await fetch('/api/v1/health', { 
        method: 'GET',
        signal: AbortSignal.timeout(5000) 
      });
      this.isOnline = response.ok;
    } catch {
      this.isOnline = false;
    }
  }
  
  private async syncWithServer(): Promise<void> {
    if (!this.isOnline) return;
    
    try {
      // 同步本地消息到服务器
      const localMessages = this.storageService.getMessages();
      const lastSyncTime = localStorage.getItem('last_sync_time');
      
      const unsyncedMessages = lastSyncTime
        ? localMessages.filter(m => m.createdAt > new Date(lastSyncTime))
        : localMessages;
      
      // 批量上传未同步的消息
      for (const message of unsyncedMessages) {
        if (message.role === 'user') {
          // 只同步用户消息，让服务器重新生成回复
          await this.apiService.sendMessage(message.text);
        }
      }
      
      localStorage.setItem('last_sync_time', new Date().toISOString());
    } catch (error) {
      console.warn('同步失败:', error);
    }
  }
}
```

### 3.2 混合情绪服务

```typescript
// src/services/HybridEmotionService.ts
import { EmotionApiService } from './api/EmotionApiService';
import { StorageService } from './storage';
import { EmotionAnalyzer } from './emotionAnalyzer';

export class HybridEmotionService {
  private apiService: EmotionApiService;
  private storageService: StorageService;
  private localAnalyzer: EmotionAnalyzer;
  
  constructor(
    apiService: EmotionApiService,
    storageService: StorageService,
    localAnalyzer: EmotionAnalyzer
  ) {
    this.apiService = apiService;
    this.storageService = storageService;
    this.localAnalyzer = localAnalyzer;
  }
  
  async getEmotionAnalysis(period: 'today' | 'week' | 'month' = 'today') {
    try {
      // 尝试从 API 获取
      const response = await this.apiService.getEmotionAnalysis(period);
      
      if (response.success && response.data) {
        return response.data;
      }
    } catch (error) {
      console.warn('API 情绪分析失败，使用本地分析:', error);
    }
    
    // 降级到本地分析
    return this.generateLocalEmotionAnalysis(period);
  }
  
  private generateLocalEmotionAnalysis(period: 'today' | 'week' | 'month') {
    const messages = this.storageService.getMessages();
    const now = new Date();
    let startDate: Date;
    
    switch (period) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        break;
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
        break;
    }
    
    const filteredMessages = messages.filter(
      m => m.role === 'user' && m.createdAt >= startDate
    );
    
    if (filteredMessages.length === 0) {
      return {
        summary: {
          dominant_emotion: '平静',
          average_intensity: 0.5,
          positive_ratio: 0.5,
          total_messages: 0,
        },
        emotion_distribution: { '平静': 1.0 },
        daily_trends: [],
        insights: ['暂无数据可分析'],
      };
    }
    
    // 分析每条消息
    const emotions = filteredMessages.map(m => 
      this.localAnalyzer.analyzeEmotion(m.text)
    );
    
    // 计算统计数据
    const positiveCount = emotions.filter(e => e.sentiment === 'positive').length;
    const totalIntensity = emotions.reduce((sum, e) => sum + e.intensity, 0);
    
    // 情绪分布统计
    const emotionCounts: Record<string, number> = {};
    emotions.forEach(e => {
      e.tags.forEach(tag => {
        emotionCounts[tag] = (emotionCounts[tag] || 0) + 1;
      });
    });
    
    const totalTags = Object.values(emotionCounts).reduce((sum, count) => sum + count, 0);
    const emotionDistribution: Record<string, number> = {};
    Object.entries(emotionCounts).forEach(([emotion, count]) => {
      emotionDistribution[emotion] = count / totalTags;
    });
    
    const dominantEmotion = Object.entries(emotionDistribution)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || '平静';
    
    return {
      summary: {
        dominant_emotion: dominantEmotion,
        average_intensity: totalIntensity / emotions.length,
        positive_ratio: positiveCount / emotions.length,
        total_messages: filteredMessages.length,
      },
      emotion_distribution: emotionDistribution,
      daily_trends: this.calculateDailyTrends(filteredMessages, emotions),
      insights: this.generateInsights(emotions),
    };
  }
  
  private calculateDailyTrends(messages: any[], emotions: any[]) {
    const dailyData: Record<string, { sentiments: number[]; count: number }> = {};
    
    messages.forEach((message, index) => {
      const date = message.createdAt.toISOString().split('T')[0];
      if (!dailyData[date]) {
        dailyData[date] = { sentiments: [], count: 0 };
      }
      
      const emotion = emotions[index];
      const sentimentScore = emotion.sentiment === 'positive' ? 1 :
                           emotion.sentiment === 'negative' ? -1 : 0;
      
      dailyData[date].sentiments.push(sentimentScore);
      dailyData[date].count++;
    });
    
    return Object.entries(dailyData).map(([date, data]) => ({
      date,
      average_sentiment: data.sentiments.reduce((sum, s) => sum + s, 0) / data.sentiments.length,
      message_count: data.count,
    }));
  }
  
  private generateInsights(emotions: any[]): string[] {
    const insights: string[] = [];
    
    const positiveRatio = emotions.filter(e => e.sentiment === 'positive').length / emotions.length;
    const avgIntensity = emotions.reduce((sum, e) => sum + e.intensity, 0) / emotions.length;
    
    if (positiveRatio > 0.7) {
      insights.push('你的情绪状态整体很积极，继续保持！');
    } else if (positiveRatio < 0.3) {
      insights.push('最近可能有些挑战，记得照顾好自己的情绪');
    }
    
    if (avgIntensity > 0.8) {
      insights.push('你的情绪表达很丰富，这说明你很敏感');
    } else if (avgIntensity < 0.3) {
      insights.push('你的情绪比较平稳，这是很好的状态');
    }
    
    return insights;
  }
}
```

## 4. React 组件集成

### 4.1 聊天组件更新

```typescript
// src/pages/Chat.tsx
import React, { useState, useEffect } from 'react';
import { HybridChatService } from '../services/HybridChatService';
import { ApiClient } from '../services/api/ApiClient';
import { ChatApiService } from '../services/api/ChatApiService';
import { StorageService } from '../services/storage';
import { EmotionAnalyzer } from '../services/emotionAnalyzer';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline'>('online');
  
  // 初始化服务
  const [chatService] = useState(() => {
    const apiClient = new ApiClient();
    const chatApiService = new ChatApiService(apiClient);
    const storageService = StorageService.getInstance();
    const emotionAnalyzer = EmotionAnalyzer.getInstance();
    
    return new HybridChatService(chatApiService, storageService, emotionAnalyzer);
  });
  
  useEffect(() => {
    // 加载历史消息
    loadMessages();
    
    // 监听网络状态
    const handleOnline = () => setConnectionStatus('online');
    const handleOffline = () => setConnectionStatus('offline');
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  const loadMessages = () => {
    // 从本地存储加载消息（即时可用）
    const storageService = StorageService.getInstance();
    const localMessages = storageService.getMessages();
    setMessages(localMessages);
  };
  
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;
    
    const userText = inputText.trim();
    setInputText('');
    setIsLoading(true);
    
    try {
      // 立即显示用户消息
      const userMessage: Message = {
        id: `temp_${Date.now()}`,
        role: 'user',
        text: userText,
        createdAt: new Date(),
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // 发送到混合服务
      const duckResponse = await chatService.sendMessage(userText);
      
      // 更新消息列表（包含最终的服务器响应）
      loadMessages();
      
    } catch (error) {
      console.error('发送消息失败:', error);
      // 显示错误提示
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="chat-container">
      {/* 连接状态指示器 */}
      <div className={`status-indicator ${connectionStatus}`}>
        {connectionStatus === 'online' ? '🟢 在线' : '🔴 离线模式'}
      </div>
      
      {/* 消息列表 */}
      <div className="messages">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <LoadingIndicator />}
      </div>
      
      {/* 输入区域 */}
      <div className="input-area">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="和鸭鸭说点什么..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading || !inputText.trim()}>
          发送
        </button>
      </div>
    </div>
  );
};
```

### 4.2 情绪报告组件更新

```typescript
// src/components/EmotionReport.tsx
import React, { useState, useEffect } from 'react';
import { HybridEmotionService } from '../services/HybridEmotionService';

export const EmotionReport: React.FC = () => {
  const [emotionData, setEmotionData] = useState<any>(null);
  const [period, setPeriod] = useState<'today' | 'week' | 'month'>('today');
  const [isLoading, setIsLoading] = useState(true);
  const [dataSource, setDataSource] = useState<'api' | 'local'>('api');
  
  const emotionService = useMemo(() => {
    const apiClient = new ApiClient();
    const emotionApiService = new EmotionApiService(apiClient);
    const storageService = StorageService.getInstance();
    const localAnalyzer = EmotionAnalyzer.getInstance();
    
    return new HybridEmotionService(emotionApiService, storageService, localAnalyzer);
  }, []);
  
  useEffect(() => {
    loadEmotionData();
  }, [period]);
  
  const loadEmotionData = async () => {
    setIsLoading(true);
    
    try {
      const data = await emotionService.getEmotionAnalysis(period);
      setEmotionData(data);
      
      // 检查数据来源（可以通过 API 响应判断）
      setDataSource(navigator.onLine ? 'api' : 'local');
      
    } catch (error) {
      console.error('加载情绪数据失败:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <div className="loading">正在分析你的情绪数据...</div>;
  }
  
  if (!emotionData) {
    return <div className="error">暂无情绪数据</div>;
  }
  
  return (
    <div className="emotion-report">
      {/* 数据来源指示器 */}
      <div className={`data-source ${dataSource}`}>
        {dataSource === 'api' ? '🌐 云端分析' : '📱 本地分析'}
      </div>
      
      {/* 时间段选择 */}
      <div className="period-selector">
        {['today', 'week', 'month'].map(p => (
          <button
            key={p}
            className={period === p ? 'active' : ''}
            onClick={() => setPeriod(p as any)}
          >
            {p === 'today' ? '今天' : p === 'week' ? '本周' : '本月'}
          </button>
        ))}
      </div>
      
      {/* 情绪概览 */}
      <div className="emotion-summary">
        <h3>情绪概览</h3>
        <div className="stats">
          <div className="stat">
            <span className="label">主导情绪</span>
            <span className="value">{emotionData.summary.dominant_emotion}</span>
          </div>
          <div className="stat">
            <span className="label">积极比例</span>
            <span className="value">
              {(emotionData.summary.positive_ratio * 100).toFixed(1)}%
            </span>
          </div>
          <div className="stat">
            <span className="label">互动次数</span>
            <span className="value">{emotionData.summary.total_messages}</span>
          </div>
        </div>
      </div>
      
      {/* 情绪分布 */}
      <div className="emotion-distribution">
        <h3>情绪分布</h3>
        {Object.entries(emotionData.emotion_distribution).map(([emotion, ratio]) => (
          <div key={emotion} className="emotion-bar">
            <span className="emotion-name">{emotion}</span>
            <div className="bar">
              <div 
                className="fill" 
                style={{ width: `${(ratio as number) * 100}%` }}
              />
            </div>
            <span className="percentage">
              {((ratio as number) * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
      
      {/* 洞察建议 */}
      <div className="insights">
        <h3>鸭鸭的观察</h3>
        {emotionData.insights.map((insight: string, index: number) => (
          <div key={index} className="insight">
            💭 {insight}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 5. 渐进式迁移策略

### 5.1 功能特性开关

```typescript
// src/config/features.ts
export interface FeatureFlags {
  useBackendChat: boolean;
  useBackendEmotion: boolean;
  useBackendContent: boolean;
  useBackendReports: boolean;
  enableSync: boolean;
}

export const getFeatureFlags = (): FeatureFlags => {
  // 可以通过环境变量或配置文件控制
  return {
    useBackendChat: process.env.REACT_APP_ENABLE_BACKEND_CHAT === 'true',
    useBackendEmotion: process.env.REACT_APP_ENABLE_BACKEND_EMOTION === 'true',
    useBackendContent: process.env.REACT_APP_ENABLE_BACKEND_CONTENT === 'true',
    useBackendReports: process.env.REACT_APP_ENABLE_BACKEND_REPORTS === 'true',
    enableSync: process.env.REACT_APP_ENABLE_SYNC === 'true',
  };
};

// 特性开关服务
export class FeatureToggleService {
  private flags: FeatureFlags;
  
  constructor() {
    this.flags = getFeatureFlags();
  }
  
  isEnabled(feature: keyof FeatureFlags): boolean {
    return this.flags[feature];
  }
  
  // 动态更新特性开关（用于 A/B 测试）
  updateFlag(feature: keyof FeatureFlags, enabled: boolean): void {
    this.flags[feature] = enabled;
    localStorage.setItem('feature_flags', JSON.stringify(this.flags));
  }
}
```

### 5.2 A/B 测试支持

```typescript
// src/services/ABTestService.ts
export class ABTestService {
  private userId: string;
  private variant: 'A' | 'B';
  
  constructor() {
    this.userId = this.getUserId();
    this.variant = this.determineVariant();
  }
  
  private getUserId(): string {
    let userId = localStorage.getItem('user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('user_id', userId);
    }
    return userId;
  }
  
  private determineVariant(): 'A' | 'B' {
    // 基于用户ID的哈希进行分组
    const hash = this.hashCode(this.userId);
    return hash % 2 === 0 ? 'A' : 'B';
  }
  
  private hashCode(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    return Math.abs(hash);
  }
  
  shouldUseBackend(): boolean {
    // A组使用后端，B组使用本地
    return this.variant === 'A';
  }
  
  getVariant(): 'A' | 'B' {
    return this.variant;
  }
  
  // 记录测试事件
  trackEvent(event: string, properties?: any): void {
    const eventData = {
      userId: this.userId,
      variant: this.variant,
      event,
      properties,
      timestamp: new Date().toISOString(),
    };
    
    // 发送到分析服务
    this.sendAnalytics(eventData);
  }
  
  private sendAnalytics(data: any): void {
    // 发送到分析平台（如 Google Analytics, Mixpanel 等）
    try {
      fetch('/api/analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      // 静默失败，不影响用户体验
      console.warn('Analytics sending failed:', error);
    }
  }
}
```

### 5.3 迁移监控

```typescript
// src/services/MigrationMonitor.ts
export class MigrationMonitor {
  private static instance: MigrationMonitor;
  
  static getInstance(): MigrationMonitor {
    if (!this.instance) {
      this.instance = new MigrationMonitor();
    }
    return this.instance;
  }
  
  // 记录 API 调用成功率
  recordApiCall(endpoint: string, success: boolean, responseTime: number): void {
    const metrics = this.getApiMetrics();
    
    if (!metrics[endpoint]) {
      metrics[endpoint] = {
        totalCalls: 0,
        successCalls: 0,
        totalResponseTime: 0,
        averageResponseTime: 0,
        successRate: 0,
      };
    }
    
    const endpointMetrics = metrics[endpoint];
    endpointMetrics.totalCalls++;
    endpointMetrics.totalResponseTime += responseTime;
    
    if (success) {
      endpointMetrics.successCalls++;
    }
    
    endpointMetrics.averageResponseTime = endpointMetrics.totalResponseTime / endpointMetrics.totalCalls;
    endpointMetrics.successRate = endpointMetrics.successCalls / endpointMetrics.totalCalls;
    
    localStorage.setItem('api_metrics', JSON.stringify(metrics));
  }
  
  // 记录降级事件
  recordFallback(feature: string, reason: string): void {
    const fallbacks = this.getFallbackMetrics();
    
    if (!fallbacks[feature]) {
      fallbacks[feature] = [];
    }
    
    fallbacks[feature].push({
      timestamp: new Date().toISOString(),
      reason,
    });
    
    // 只保留最近50次记录
    if (fallbacks[feature].length > 50) {
      fallbacks[feature] = fallbacks[feature].slice(-50);
    }
    
    localStorage.setItem('fallback_metrics', JSON.stringify(fallbacks));
  }
  
  // 获取迁移统计
  getMigrationStats(): any {
    return {
      apiMetrics: this.getApiMetrics(),
      fallbackMetrics: this.getFallbackMetrics(),
      connectionStatus: navigator.onLine ? 'online' : 'offline',
      lastSyncTime: localStorage.getItem('last_sync_time'),
    };
  }
  
  private getApiMetrics(): any {
    try {
      return JSON.parse(localStorage.getItem('api_metrics') || '{}');
    } catch {
      return {};
    }
  }
  
  private getFallbackMetrics(): any {
    try {
      return JSON.parse(localStorage.getItem('fallback_metrics') || '{}');
    } catch {
      return {};
    }
  }
}
```

## 6. 性能优化

### 6.1 请求缓存策略

```typescript
// src/services/CacheStrategy.ts
export class CacheStrategy {
  private static readonly CACHE_PREFIX = 'duck_cache_';
  private static readonly DEFAULT_TTL = 5 * 60 * 1000; // 5分钟
  
  static set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    try {
      const cacheItem = {
        data,
        timestamp: Date.now(),
        ttl,
      };
      
      sessionStorage.setItem(
        `${this.CACHE_PREFIX}${key}`,
        JSON.stringify(cacheItem)
      );
    } catch (error) {
      console.warn('Cache set failed:', error);
    }
  }
  
  static get<T>(key: string): T | null {
    try {
      const cached = sessionStorage.getItem(`${this.CACHE_PREFIX}${key}`);
      if (!cached) return null;
      
      const cacheItem = JSON.parse(cached);
      const now = Date.now();
      
      if (now - cacheItem.timestamp > cacheItem.ttl) {
        this.remove(key);
        return null;
      }
      
      return cacheItem.data;
    } catch (error) {
      console.warn('Cache get failed:', error);
      return null;
    }
  }
  
  static remove(key: string): void {
    sessionStorage.removeItem(`${this.CACHE_PREFIX}${key}`);
  }
  
  static clear(): void {
    const keys = Object.keys(sessionStorage);
    keys.forEach(key => {
      if (key.startsWith(this.CACHE_PREFIX)) {
        sessionStorage.removeItem(key);
      }
    });
  }
}
```

### 6.2 请求去重

```typescript
// src/services/RequestDeduplicator.ts
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();
  
  async deduplicate<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    // 如果相同请求正在进行中，返回现有的 Promise
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }
    
    // 创建新请求
    const promise = requestFn()
      .finally(() => {
        // 请求完成后清理
        this.pendingRequests.delete(key);
      });
    
    this.pendingRequests.set(key, promise);
    return promise;
  }
  
  // 取消所有待处理的请求
  cancelAll(): void {
    this.pendingRequests.clear();
  }
}

// 在 ApiClient 中使用
export class ApiClient {
  private deduplicator = new RequestDeduplicator();
  
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const key = `${options.method || 'GET'}_${endpoint}_${JSON.stringify(options.body || {})}`;
    
    return this.deduplicator.deduplicate(key, () => 
      this.executeRequest<T>(endpoint, options)
    );
  }
}
```

## 7. 错误处理和用户体验

### 7.1 优雅降级

```typescript
// src/services/GracefulDegradation.ts
export class GracefulDegradation {
  static async withFallback<T>(
    primaryAction: () => Promise<T>,
    fallbackAction: () => Promise<T>,
    errorHandler?: (error: Error) => void
  ): Promise<T> {
    try {
      return await primaryAction();
    } catch (error) {
      console.warn('Primary action failed, using fallback:', error);
      
      if (errorHandler) {
        errorHandler(error instanceof Error ? error : new Error(String(error)));
      }
      
      return await fallbackAction();
    }
  }
  
  static withTimeout<T>(
    promise: Promise<T>,
    timeoutMs: number,
    fallback: () => Promise<T>
  ): Promise<T> {
    return Promise.race([
      promise,
      new Promise<T>((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), timeoutMs)
      ),
    ]).catch(() => fallback());
  }
}
```

### 7.2 用户通知系统

```typescript
// src/components/NotificationSystem.tsx
export const NotificationSystem: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  useEffect(() => {
    // 监听网络状态变化
    const handleOnline = () => {
      addNotification({
        type: 'success',
        message: '网络连接已恢复，正在同步数据...',
        duration: 3000,
      });
    };
    
    const handleOffline = () => {
      addNotification({
        type: 'warning',
        message: '网络连接断开，切换到离线模式',
        duration: 5000,
      });
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString();
    const newNotification = { ...notification, id };
    
    setNotifications(prev => [...prev, newNotification]);
    
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }
  };
  
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };
  
  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <NotificationToast
          key={notification.id}
          notification={notification}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};
```

## 8. 测试策略

### 8.1 集成测试

```typescript
// src/__tests__/integration/ChatIntegration.test.tsx
describe('Chat Integration', () => {
  let mockApiClient: jest.Mocked<ApiClient>;
  let hybridChatService: HybridChatService;
  
  beforeEach(() => {
    mockApiClient = {
      request: jest.fn(),
    } as any;
    
    hybridChatService = new HybridChatService(
      new ChatApiService(mockApiClient),
      StorageService.getInstance(),
      EmotionAnalyzer.getInstance()
    );
  });
  
  it('should use API when online and fallback to local when offline', async () => {
    // 模拟在线状态，API 成功
    mockApiClient.request.mockResolvedValueOnce({
      success: true,
      data: {
        duck_response: {
          id: 'api_response',
          role: 'duck',
          text: 'API 回复',
          createdAt: new Date(),
        },
        emotion_analysis: {
          sentiment: 'positive',
          intensity: 0.8,
        },
      },
    });
    
    const response = await hybridChatService.sendMessage('你好');
    expect(response.text).toBe('API 回复');
    
    // 模拟离线状态，使用本地逻辑
    mockApiClient.request.mockRejectedValueOnce(new Error('Network error'));
    
    const fallbackResponse = await hybridChatService.sendMessage('再次你好');
    expect(fallbackResponse.text).toContain('鸭鸭');
  });
  
  it('should handle API timeout gracefully', async () => {
    // 模拟 API 超时
    mockApiClient.request.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(resolve, 10000))
    );
    
    const response = await Promise.race([
      hybridChatService.sendMessage('测试超时'),
      new Promise(resolve => setTimeout(() => resolve('timeout'), 1000)),
    ]);
    
    expect(response).toBe('timeout');
  });
});
```

### 8.2 端到端测试

```typescript
// cypress/integration/chat.spec.ts
describe('Chat E2E', () => {
  beforeEach(() => {
    cy.visit('/chat');
  });
  
  it('should work in online mode', () => {
    // 模拟在线状态
    cy.window().then(win => {
      Object.defineProperty(win.navigator, 'onLine', {
        writable: true,
        value: true,
      });
    });
    
    cy.get('[data-testid="chat-input"]').type('你好，鸭鸭');
    cy.get('[data-testid="send-button"]').click();
    
    // 验证消息发送
    cy.get('[data-testid="message-user"]').should('contain', '你好，鸭鸭');
    
    // 验证收到回复
    cy.get('[data-testid="message-duck"]', { timeout: 10000 })
      .should('be.visible')
      .and('contain.text', '鸭鸭');
  });
  
  it('should work in offline mode', () => {
    // 模拟离线状态
    cy.window().then(win => {
      Object.defineProperty(win.navigator, 'onLine', {
        writable: true,
        value: false,
      });
      win.dispatchEvent(new Event('offline'));
    });
    
    cy.get('[data-testid="status-indicator"]').should('contain', '离线模式');
    
    cy.get('[data-testid="chat-input"]').type('离线测试');
    cy.get('[data-testid="send-button"]').click();
    
    // 验证离线模式下仍能正常聊天
    cy.get('[data-testid="message-duck"]')
      .should('be.visible')
      .and('contain.text', '鸭鸭');
  });
});
```

## 9. 部署和监控

### 9.1 环境配置

```env
# .env.production
REACT_APP_API_BASE_URL=https://api.ducktherapy.com/api/v1
REACT_APP_ENABLE_BACKEND_CHAT=true
REACT_APP_ENABLE_BACKEND_EMOTION=true
REACT_APP_ENABLE_SYNC=true
REACT_APP_SENTRY_DSN=your_sentry_dsn_here

# .env.development
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENABLE_BACKEND_CHAT=false
REACT_APP_ENABLE_BACKEND_EMOTION=false
REACT_APP_ENABLE_SYNC=false
```

### 9.2 监控配置

```typescript
// src/monitoring/setup.ts
import * as Sentry from '@sentry/react';

export const setupMonitoring = () => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.init({
      dsn: process.env.REACT_APP_SENTRY_DSN,
      environment: process.env.NODE_ENV,
      beforeSend(event, hint) {
        // 过滤敏感信息
        if (event.extra) {
          delete event.extra.userMessage;
          delete event.extra.duckResponse;
        }
        return event;
      },
    });
  }
  
  // 设置性能监控
  if ('performance' in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          console.log('Page load time:', entry.duration);
        }
      }
    });
    
    observer.observe({ entryTypes: ['navigation'] });
  }
};
```

这个前后端集成指南提供了完整的迁移策略，确保现有前端功能的平滑过渡和新后端服务的无缝集成。