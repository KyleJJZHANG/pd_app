import { Message, MemoryItem, TimelineEntry, EmotionStats, EmotionTag } from '../data';
import { EmotionAnalyzer } from './emotionAnalyzer';

class StorageService {
  private static instance: StorageService;
  
  private constructor() {}
  
  static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService();
    }
    return StorageService.instance;
  }

  // 消息相关
  saveMessage(message: Message): void {
    const messages = this.getMessages();
    messages.push(message);
    localStorage.setItem('duck_messages', JSON.stringify(messages));
  }

  getMessages(): Message[] {
    const stored = localStorage.getItem('duck_messages');
    if (!stored) return [];
    
    return JSON.parse(stored).map((msg: Message & { timestamp: string }) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));
  }

  clearMessages(): void {
    localStorage.removeItem('duck_messages');
  }

  // 记忆相关
  saveMemory(memory: MemoryItem): void {
    const memories = this.getMemories();
    memories.push(memory);
    localStorage.setItem('duck_memories', JSON.stringify(memories));
    
    // 同时保存到时间线
    this.saveTimelineEntry({
      id: `timeline_${Date.now()}`,
      type: 'memory',
      refId: memory.id,
      createdAt: memory.createdAt
    });
  }

  getMemories(): MemoryItem[] {
    const stored = localStorage.getItem('duck_memories');
    if (!stored) return [];
    
    return JSON.parse(stored).map((memory: MemoryItem & { createdAt: string }) => ({
      ...memory,
      createdAt: new Date(memory.createdAt)
    }));
  }

  deleteMemory(id: string): void {
    const memories = this.getMemories().filter(memory => memory.id !== id);
    localStorage.setItem('duck_memories', JSON.stringify(memories));
    
    // 同时从时间线删除
    const timeline = this.getTimeline().filter(entry => 
      !(entry.type === 'memory' && entry.refId === id)
    );
    localStorage.setItem('duck_timeline', JSON.stringify(timeline));
  }

  // 时间线相关
  saveTimelineEntry(entry: TimelineEntry): void {
    const timeline = this.getTimeline();
    timeline.push(entry);
    timeline.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    localStorage.setItem('duck_timeline', JSON.stringify(timeline));
  }

  getTimeline(): TimelineEntry[] {
    const stored = localStorage.getItem('duck_timeline');
    if (!stored) return [];
    
    return JSON.parse(stored).map((entry: TimelineEntry & { createdAt: string }) => ({
      ...entry,
      createdAt: new Date(entry.createdAt)
    }));
  }

  // 用户偏好设置
  saveUserPrefs(prefs: Record<string, unknown>): void {
    localStorage.setItem('duck_user_prefs', JSON.stringify(prefs));
  }

  getUserPrefs(): Record<string, unknown> {
    const stored = localStorage.getItem('duck_user_prefs');
    return stored ? JSON.parse(stored) : {};
  }

  // 情绪统计相关
  saveEmotionStats(stats: EmotionStats): void {
    const allStats = this.getEmotionStats();
    const existingIndex = allStats.findIndex(s => s.date === stats.date);
    
    if (existingIndex >= 0) {
      allStats[existingIndex] = stats;
    } else {
      allStats.push(stats);
    }
    
    // 按日期倒序排序
    allStats.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    
    localStorage.setItem('duck_emotion_stats', JSON.stringify(allStats));
  }

  getEmotionStats(): EmotionStats[] {
    const stored = localStorage.getItem('duck_emotion_stats');
    return stored ? JSON.parse(stored) : [];
  }

  getTodayEmotionStats(): EmotionStats | null {
    const today = new Date().toISOString().split('T')[0];
    const allStats = this.getEmotionStats();
    return allStats.find(stats => stats.date === today) || null;
  }

  generateTodayEmotionStats(): EmotionStats | null {
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    
    // 获取今天的用户消息
    const messages = this.getMessages();
    const todayMessages = messages.filter(msg => 
      msg.role === 'user' && 
      msg.timestamp.toISOString().split('T')[0] === todayString
    );

    if (todayMessages.length === 0) {
      return null;
    }

    // 分析所有今天的消息
    const emotionAnalyzer = EmotionAnalyzer.getInstance();
    const allEmotions: EmotionTag[] = [];

    for (const message of todayMessages) {
      const emotions = emotionAnalyzer.analyzeText(message.text);
      allEmotions.push(...emotions);
    }

    if (allEmotions.length === 0) {
      return null;
    }

    // 生成统计数据
    const stats = emotionAnalyzer.generateEmotionStats(allEmotions, today);
    
    // 保存统计数据
    this.saveEmotionStats(stats);
    
    return stats;
  }

  // 清除所有数据
  clearAllData(): void {
    localStorage.removeItem('duck_messages');
    localStorage.removeItem('duck_memories');
    localStorage.removeItem('duck_timeline');
    localStorage.removeItem('duck_user_prefs');
    localStorage.removeItem('duck_emotion_stats');
  }
}

export default StorageService;