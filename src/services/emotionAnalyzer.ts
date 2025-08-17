import { EmotionTag, EmotionStats } from '../data';

export interface EmotionPattern {
  emotion: string;
  keywords: string[];
  intensity: number;
  mood: number; // -1 to 1
}

export const emotionPatterns: EmotionPattern[] = [
  {
    emotion: '难过',
    keywords: ['难过', '伤心', '哭', '痛苦', '难受', '沮丧', '失望', '绝望'],
    intensity: 0.8,
    mood: -0.7
  },
  {
    emotion: '开心',
    keywords: ['开心', '高兴', '快乐', '兴奋', '愉快', '欣喜', '满足', '幸福'],
    intensity: 0.8,
    mood: 0.8
  },
  {
    emotion: '疲惫',
    keywords: ['累', '疲惫', '辛苦', '疲劳', '力不从心', '筋疲力尽'],
    intensity: 0.6,
    mood: -0.4
  },
  {
    emotion: '孤独',
    keywords: ['孤独', '一个人', '没人', '寂寞', '孤单', '无助'],
    intensity: 0.7,
    mood: -0.6
  },
  {
    emotion: '焦虑',
    keywords: ['焦虑', '紧张', '不安', '担心', '恐惧', '害怕', '忐忑'],
    intensity: 0.7,
    mood: -0.5
  },
  {
    emotion: '感恩',
    keywords: ['谢谢', '感谢', '感恩', '感激', '温暖', '幸运'],
    intensity: 0.6,
    mood: 0.6
  },
  {
    emotion: '愤怒',
    keywords: ['生气', '愤怒', '气愤', '恼火', '烦躁', '暴躁'],
    intensity: 0.8,
    mood: -0.4
  },
  {
    emotion: '平静',
    keywords: ['平静', '安静', '放松', '淡定', '宁静', '舒缓'],
    intensity: 0.5,
    mood: 0.3
  },
  {
    emotion: '困惑',
    keywords: ['困惑', '迷茫', '不知道', '不明白', '疑惑', '纠结'],
    intensity: 0.5,
    mood: -0.2
  },
  {
    emotion: '希望',
    keywords: ['希望', '期待', '憧憬', '乐观', '向往', '梦想'],
    intensity: 0.7,
    mood: 0.7
  }
];

export class EmotionAnalyzer {
  private static instance: EmotionAnalyzer;
  
  private constructor() {}
  
  static getInstance(): EmotionAnalyzer {
    if (!EmotionAnalyzer.instance) {
      EmotionAnalyzer.instance = new EmotionAnalyzer();
    }
    return EmotionAnalyzer.instance;
  }

  analyzeText(text: string): EmotionTag[] {
    const lowerText = text.toLowerCase();
    const detectedEmotions: EmotionTag[] = [];

    for (const pattern of emotionPatterns) {
      const matchedKeywords = pattern.keywords.filter(keyword => 
        lowerText.includes(keyword)
      );

      if (matchedKeywords.length > 0) {
        // Calculate intensity based on number of matches and pattern intensity
        const intensity = Math.min(
          pattern.intensity * (matchedKeywords.length / pattern.keywords.length + 0.5),
          1
        );

        detectedEmotions.push({
          emotion: pattern.emotion,
          intensity,
          keywords: matchedKeywords
        });
      }
    }

    // If no specific emotions detected, analyze sentiment
    if (detectedEmotions.length === 0) {
      const sentiment = this.analyzeSentiment(text);
      if (sentiment !== null) {
        detectedEmotions.push(sentiment);
      }
    }

    return detectedEmotions;
  }

  private analyzeSentiment(text: string): EmotionTag | null {
    const positiveWords = ['好', '棒', '不错', '满意', '喜欢', '爱', '美好'];
    const negativeWords = ['不好', '糟糕', '讨厌', '痛', '坏', '差'];
    
    const lowerText = text.toLowerCase();
    const positiveCount = positiveWords.filter(word => lowerText.includes(word)).length;
    const negativeCount = negativeWords.filter(word => lowerText.includes(word)).length;

    if (positiveCount > negativeCount) {
      return {
        emotion: '积极',
        intensity: 0.5,
        keywords: positiveWords.filter(word => lowerText.includes(word))
      };
    } else if (negativeCount > positiveCount) {
      return {
        emotion: '消极',
        intensity: 0.5,
        keywords: negativeWords.filter(word => lowerText.includes(word))
      };
    }

    return null;
  }

  generateEmotionStats(emotions: EmotionTag[], date: Date): EmotionStats {
    if (emotions.length === 0) {
      return {
        date: date.toISOString().split('T')[0],
        emotions: [],
        dominantEmotion: '平静',
        overallMood: 0
      };
    }

    // Find dominant emotion (highest intensity)
    const dominantEmotion = emotions.reduce((prev, current) => 
      prev.intensity > current.intensity ? prev : current
    );

    // Calculate overall mood
    let totalMood = 0;
    let moodCount = 0;

    for (const emotion of emotions) {
      const pattern = emotionPatterns.find(p => p.emotion === emotion.emotion);
      if (pattern) {
        totalMood += pattern.mood * emotion.intensity;
        moodCount += emotion.intensity;
      }
    }

    const overallMood = moodCount > 0 ? totalMood / moodCount : 0;

    return {
      date: date.toISOString().split('T')[0],
      emotions,
      dominantEmotion: dominantEmotion.emotion,
      overallMood: Math.max(-1, Math.min(1, overallMood))
    };
  }

  getEmotionSummary(emotions: EmotionTag[]): string {
    if (emotions.length === 0) {
      return '今天的心情很平静呢～';
    }

    const dominantEmotion = emotions.reduce((prev, current) => 
      prev.intensity > current.intensity ? prev : current
    );

    const emotionDescriptions: Record<string, string> = {
      '难过': '今天感受到了一些难过，这种情绪需要被温柔对待',
      '开心': '今天有着很棒的快乐时光，这份美好值得珍藏',
      '疲惫': '今天感到有些疲惫，记得要好好休息和照顾自己',
      '孤独': '今天体验到了孤独的感觉，但请记住你并不孤单',
      '焦虑': '今天有一些焦虑的情绪，深呼吸，一切都会好起来的',
      '感恩': '今天心中充满了感恩，这是很珍贵的情感体验',
      '愤怒': '今天有一些愤怒的情绪，这些感受都是正常的',
      '平静': '今天心情很平静，这种内心的安宁很珍贵',
      '困惑': '今天遇到了一些困惑，慢慢思考，答案会出现的',
      '希望': '今天心中充满了希望，这是前进的力量'
    };

    return emotionDescriptions[dominantEmotion.emotion] || '今天的情绪体验很丰富呢～';
  }
}