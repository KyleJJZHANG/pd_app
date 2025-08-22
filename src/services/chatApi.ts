import { Message } from '../data';

// API 基础配置
const API_BASE_URL = '/api';

// API 接口类型定义
export interface ChatMessageRequest {
  text: string;
  session_id: string;
  context?: string[];
  user_preferences?: Record<string, any>;
  workflow_type?: string;
  response_style?: 'brief' | 'standard' | 'detailed';
  analysis_depth?: 'basic' | 'standard' | 'detailed';
}

export interface EmotionAnalysis {
  sentiment: string;
  emotions: string[];
  intensity: number;
  keywords?: string[];
}

export interface ChatResponse {
  message_id: string;
  response_text: string;
  emotion_analysis?: EmotionAnalysis;
  content_recommendations?: Array<{
    type: string;
    path: string;
    relevance_score: number;
  }>;
  therapy_suggestions?: Array<{
    title: string;
    description: string;
    type: string;
  }>;
  workflow_executed: string;
  execution_time_ms: number;
  success_rate: number;
  llm_providers_used: string[];
  timestamp: string;
}

// API 错误类型
export class ChatApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ChatApiError';
  }
}

// Chat API 服务类
export class ChatApiService {
  private static instance: ChatApiService;
  private sessionId: string;

  private constructor() {
    this.sessionId = this.generateSessionId();
  }

  public static getInstance(): ChatApiService {
    if (!ChatApiService.instance) {
      ChatApiService.instance = new ChatApiService();
    }
    return ChatApiService.instance;
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 检查 API 服务器状态
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      console.warn('API 服务器不可用，将使用本地模式');
      return false;
    }
  }

  // 发送消息到 API
  async sendMessage(
    text: string,
    options: {
      context?: string[];
      responseStyle?: 'brief' | 'standard' | 'detailed';
      analysisDepth?: 'basic' | 'standard' | 'detailed';
    } = {}
  ): Promise<ChatResponse> {
    const requestData: ChatMessageRequest = {
      text,
      session_id: this.sessionId,
      context: options.context,
      workflow_type: 'basic_chat_flow',
      response_style: options.responseStyle || 'standard',
      analysis_depth: options.analysisDepth || 'standard'
    };

    try {
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        let errorDetails;
        try {
          errorDetails = await response.json();
        } catch {
          errorDetails = { message: 'Network error' };
        }
        
        throw new ChatApiError(
          `API request failed: ${response.status}`,
          response.status,
          errorDetails
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ChatApiError) {
        throw error;
      }
      throw new ChatApiError('Failed to send message', 500, error);
    }
  }

  // 流式发送消息（暂时返回 Promise，后续可改为 EventSource）
  async sendMessageStream(
    text: string,
    onProgress?: (data: any) => void
  ): Promise<ChatResponse> {
    // TODO: 实现 Server-Sent Events 流式响应
    // 目前先调用常规 API
    return this.sendMessage(text);
  }

  // 获取会话信息
  async getSessionInfo(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/session/${this.sessionId}`);
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.warn('获取会话信息失败:', error);
      return null;
    }
  }

  // 获取会话消息历史
  async getSessionMessages(limit: number = 50, offset: number = 0): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/session/${this.sessionId}/messages?limit=${limit}&offset=${offset}`
      );
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.warn('获取消息历史失败:', error);
      return null;
    }
  }

  // 清除当前会话
  async clearSession(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/session/${this.sessionId}/clear`, {
        method: 'POST'
      });
      return response.ok;
    } catch (error) {
      console.warn('清除会话失败:', error);
      return false;
    }
  }

  // 获取当前会话 ID
  getSessionId(): string {
    return this.sessionId;
  }

  // 重新生成会话 ID（开始新会话）
  startNewSession(): string {
    this.sessionId = this.generateSessionId();
    return this.sessionId;
  }
}

// Fallback 转换函数：将 API 响应转换为前端 Message 格式
export function convertApiResponseToMessage(apiResponse: ChatResponse): Omit<Message, 'id' | 'timestamp'> {
  const result: Omit<Message, 'id' | 'timestamp'> = {
    role: 'duck',
    text: apiResponse.response_text
  };

  // 根据内容推荐添加 panel 或 video
  if (apiResponse.content_recommendations && apiResponse.content_recommendations.length > 0) {
    const recommendation = apiResponse.content_recommendations[0];
    if (recommendation.type === 'panel') {
      result.panel = recommendation.path;
    } else if (recommendation.type === 'video') {
      result.video = recommendation.path;
    }
  }

  return result;
}