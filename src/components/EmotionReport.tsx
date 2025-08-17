import React from 'react';
import { ArrowLeft, Heart, Brain, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { EmotionStats, EmotionTag } from '../data';
import { EmotionAnalyzer } from '../services/emotionAnalyzer';
import StorageService from '../services/storage';

interface EmotionReportProps {
  isOpen: boolean;
  onClose: () => void;
}

const EmotionReport: React.FC<EmotionReportProps> = ({ isOpen, onClose }) => {
  const storageService = StorageService.getInstance();
  const emotionAnalyzer = EmotionAnalyzer.getInstance();
  const todayStats = storageService.getTodayEmotionStats();
  const recentStats = storageService.getEmotionStats().slice(0, 7); // 最近7天

  if (!isOpen) return null;

  const getMoodColor = (mood: number) => {
    if (mood > 0.3) return 'text-green-600 bg-green-50';
    if (mood < -0.3) return 'text-red-600 bg-red-50';
    return 'text-yellow-600 bg-yellow-50';
  };

  const getMoodDescription = (mood: number) => {
    if (mood > 0.5) return '今天心情很棒！';
    if (mood > 0.2) return '今天心情不错～';
    if (mood > -0.2) return '今天心情还算平静';
    if (mood > -0.5) return '今天情绪有些低落';
    return '今天需要更多关爱';
  };

  const getEmotionIcon = (emotion: string) => {
    const icons: Record<string, string> = {
      '开心': '😊',
      '难过': '😢',
      '焦虑': '😰',
      '疲惫': '😴',
      '孤独': '😔',
      '感恩': '🙏',
      '愤怒': '😠',
      '平静': '😌',
      '困惑': '🤔',
      '希望': '✨'
    };
    return icons[emotion] || '😐';
  };

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-amber-50 to-orange-50 flex flex-col">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-amber-200/50 p-4">
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 mr-3"
          >
            <ArrowLeft size={20} />
          </Button>
          <Brain className="text-amber-600 mr-2" size={24} />
          <h1 className="text-xl font-semibold text-amber-800">情绪足迹报告</h1>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 pb-20">
        <div className="max-w-md mx-auto space-y-6">
          {/* 今日情绪概览 */}
          <div className="bg-white/60 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Heart className="text-pink-500" size={20} />
              <h3 className="font-semibold text-gray-800">今日情绪概览</h3>
            </div>
            
            {todayStats ? (
              <div className="space-y-3">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getMoodColor(todayStats.overallMood)}`}>
                  <span className="mr-2">{getEmotionIcon(todayStats.dominantEmotion)}</span>
                  {getMoodDescription(todayStats.overallMood)}
                </div>
                
                <div className="space-y-2">
                  <div className="text-sm text-gray-600">情绪分布：</div>
                  {todayStats.emotions.map((emotion, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <span className="w-16 text-sm">{emotion.emotion}</span>
                      <div className="flex-1">
                        <Progress 
                          value={emotion.intensity * 100} 
                          className="h-2"
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {Math.round(emotion.intensity * 100)}%
                      </span>
                    </div>
                  ))}
                </div>

                <div className="text-sm text-gray-600 mt-3">
                  {emotionAnalyzer.getEmotionSummary(todayStats.emotions)}
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">
                今天还没有聊天记录，快和鸭鸭聊聊天吧！🦆
              </div>
            )}
          </div>

          {/* 近期情绪趋势 */}
          {recentStats.length > 0 && (
            <div className="bg-white/60 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Sparkles className="text-purple-500" size={20} />
                <h3 className="font-semibold text-gray-800">近期情绪趋势</h3>
              </div>
              
              <div className="space-y-2">
                {recentStats.map((stats, index) => (
                  <div key={stats.date} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-500 w-20">
                        {index === 0 ? '今天' : 
                         index === 1 ? '昨天' : 
                         new Date(stats.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                      </span>
                      <Badge 
                        variant="secondary" 
                        className={`${getMoodColor(stats.overallMood)} border-0`}
                      >
                        {getEmotionIcon(stats.dominantEmotion)} {stats.dominantEmotion}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-300 ${
                            stats.overallMood > 0 ? 'bg-green-400' : 'bg-red-400'
                          }`}
                          style={{ 
                            width: `${Math.abs(stats.overallMood) * 100}%`,
                            marginLeft: stats.overallMood < 0 ? 'auto' : '0'
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 情绪小贴士 */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
            <h3 className="font-semibold text-indigo-800 mb-2">💡 情绪小贴士</h3>
            <div className="text-sm text-indigo-700 space-y-1">
              <p>• 记录情绪有助于更好地了解自己</p>
              <p>• 每种情绪都有其价值，接纳它们是成长的开始</p>
              <p>• 如果持续感到低落，记得寻求专业帮助</p>
              <p>• 和鸭鸭多聊聊，分享你的感受吧！🦆</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmotionReport;