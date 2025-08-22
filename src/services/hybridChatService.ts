import { Message } from '../data';
import { generateDuckReply, greetingMessage } from '../data/chatReplies';
import { ChatApiService, convertApiResponseToMessage, ChatApiError } from './chatApi';

/**
 * 混合聊天服务
 * 优先使用 API，失败时回退到本地模式
 */
export class HybridChatService {
  private static instance: HybridChatService;
  private chatApi: ChatApiService;
  private isApiAvailable: boolean = false;
  private apiCheckPromise: Promise<boolean> | null = null;

  private constructor() {
    this.chatApi = ChatApiService.getInstance();
  }

  public static getInstance(): HybridChatService {
    if (!HybridChatService.instance) {
      HybridChatService.instance = new HybridChatService();
    }
    return HybridChatService.instance;
  }

  /**
   * 检查 API 可用性（缓存结果）
   */
  async checkApiAvailability(): Promise<boolean> {
    if (this.apiCheckPromise) {
      return this.apiCheckPromise;
    }

    this.apiCheckPromise = this.chatApi.checkHealth();
    this.isApiAvailable = await this.apiCheckPromise;
    
    // 清除缓存，5秒后可重新检查
    setTimeout(() => {
      this.apiCheckPromise = null;
    }, 5000);

    return this.isApiAvailable;
  }

  /**
   * 获取问候消息
   */
  getGreetingMessage(): string {
    return greetingMessage;
  }

  /**
   * 生成回复消息
   * 优先使用 API，失败时回退到本地模式
   */
  async generateReply(userText: string): Promise<{
    message: Omit<Message, 'id' | 'timestamp'>;
    source: 'api' | 'local';
    apiData?: any;
  }> {
    const isApiAvailable = await this.checkApiAvailability();

    // 优先尝试使用 API
    if (isApiAvailable) {
      try {
        const apiResponse = await this.chatApi.sendMessage(userText, {
          responseStyle: 'standard',
          analysisDepth: 'standard'
        });

        const message = convertApiResponseToMessage(apiResponse);
        
        return {
          message,
          source: 'api',
          apiData: {
            emotionAnalysis: apiResponse.emotion_analysis,
            executionTime: apiResponse.execution_time_ms,
            llmProviders: apiResponse.llm_providers_used,
            therapySuggestions: apiResponse.therapy_suggestions
          }
        };
      } catch (error) {
        console.warn('API 调用失败，回退到本地模式:', error);
        
        // API 错误时标记为不可用，触发后续的本地模式
        this.isApiAvailable = false;
      }
    }

    // 使用本地模式作为回退
    const localMessage = generateDuckReply(userText);
    
    return {
      message: localMessage,
      source: 'local'
    };
  }

  /**
   * 获取当前会话状态
   */
  async getSessionInfo() {
    if (this.isApiAvailable) {
      return await this.chatApi.getSessionInfo();
    }
    return null;
  }

  /**
   * 清除会话（仅当使用 API 时）
   */
  async clearSession(): Promise<boolean> {
    if (this.isApiAvailable) {
      return await this.chatApi.clearSession();
    }
    return true; // 本地模式总是成功
  }

  /**
   * 开始新会话
   */
  async startNewSession(): Promise<string | null> {
    if (this.isApiAvailable) {
      return this.chatApi.startNewSession();
    }
    return null; // 本地模式不需要会话 ID
  }

  /**
   * 获取当前使用的模式
   */
  getCurrentMode(): 'api' | 'local' {
    return this.isApiAvailable ? 'api' : 'local';
  }

  /**
   * 强制重新检查 API 可用性
   */
  async forceApiCheck(): Promise<boolean> {
    this.apiCheckPromise = null;
    return await this.checkApiAvailability();
  }
}