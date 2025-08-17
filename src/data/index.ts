// 数据类型定义
export interface Message {
  id: string;
  role: 'user' | 'duck';
  text: string;
  panel?: string;
  video?: string;
  timestamp: Date;
}

export interface Scene {
  id: string;
  title: string;
  description: string;
  story: string;
  emoji: string;
  color: string;
  interaction?: {
    type: 'breathing' | 'listening' | 'watching';
    instruction: string;
  };
}

export interface MemoryItem {
  id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: Date;
  type: 'text' | 'image';
}

export interface TimelineEntry {
  id: string;
  type: 'chat' | 'map' | 'memory';
  refId: string;
  createdAt: Date;
}

export interface WarmQuote {
  id: string;
  text: string;
  category: 'daily' | 'comfort' | 'encouragement';
}

export interface EmotionTag {
  emotion: string;
  intensity: number;
  keywords: string[];
}

export interface EmotionStats {
  date: string;
  emotions: EmotionTag[];
  dominantEmotion: string;
  overallMood: number;
}