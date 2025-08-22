import React, { useState, useRef, useEffect } from 'react';
import { Send, Image, Video, BarChart3, ArrowLeft, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';
import { Message, TimelineEntry } from '../data';
import { HybridChatService } from '../services/hybridChatService';
import StorageService from '../services/storage';
import { EmotionAnalyzer } from '../services/emotionAnalyzer';
import EmotionReport from '../components/EmotionReport';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [showEmotionReport, setShowEmotionReport] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const storageService = StorageService.getInstance();
  const emotionAnalyzer = EmotionAnalyzer.getInstance();
  const hybridChatService = HybridChatService.getInstance();

  useEffect(() => {
    // 加载历史消息
    const savedMessages = storageService.getMessages();
    if (savedMessages.length === 0) {
      // 如果没有历史消息，添加问候消息
      const welcomeMessage: Message = {
        id: '1',
        role: 'duck',
        text: hybridChatService.getGreetingMessage(),
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
      storageService.saveMessage(welcomeMessage);
    } else {
      setMessages(savedMessages);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);



  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const messageText = inputText.trim();
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    storageService.saveMessage(userMessage);
    setInputText('');
    setIsLoading(true);

    // 情绪分析
    const emotionTags = emotionAnalyzer.analyzeText(messageText);
    const today = new Date();
    
    // 获取今日已有的情绪统计
    let todayStats = storageService.getTodayEmotionStats();
    if (todayStats) {
      // 合并今日的情绪标签
      const allEmotions = [...todayStats.emotions, ...emotionTags];
      todayStats = emotionAnalyzer.generateEmotionStats(allEmotions, today);
    } else {
      // 创建新的今日情绪统计
      todayStats = emotionAnalyzer.generateEmotionStats(emotionTags, today);
    }
    
    // 保存情绪统计
    storageService.saveEmotionStats(todayStats);

    // 保存到时间线
    const timelineEntry: TimelineEntry = {
      id: `timeline_${Date.now()}`,
      type: 'chat',
      refId: userMessage.id,
      createdAt: today
    };
    storageService.saveTimelineEntry(timelineEntry);

    // 生成鸭鸭回复（API 优先，本地回退）
    setTimeout(async () => {
      try {
        const replyResult = await hybridChatService.generateReply(messageText);
        const duckMessage: Message = {
          id: (Date.now() + 1).toString(),
          ...replyResult.message,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, duckMessage]);
        storageService.saveMessage(duckMessage);
        
        // 如果使用了 API 模式，可以在控制台输出额外信息
        if (replyResult.source === 'api' && replyResult.apiData) {
          console.log('API 回复数据:', replyResult.apiData);
        }
      } catch (error) {
        console.error('生成回复失败:', error);
        // 出错时显示错误消息
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'duck',
          text: '抱歉，鸭鸭暂时无法回复，请稍后再试～',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
        storageService.saveMessage(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-blue-50 to-yellow-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-amber-200/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleGoBack}
              className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 mr-3"
            >
              <ArrowLeft size={20} />
            </Button>
            <span className="text-2xl mr-2">🦆</span>
            <h1 className="text-xl font-semibold text-amber-700">和鸭鸭聊聊</h1>
          </div>
          
          {/* 情绪报告按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowEmotionReport(true)}
            className="text-amber-600 hover:text-amber-700 hover:bg-amber-50"
          >
            <BarChart3 size={18} className="mr-1" />
            情绪足迹
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs lg:max-w-md`}>
              {message.role === 'duck' && (
                <div className="flex items-center mb-1">
                  <span className="text-lg mr-1">🦆</span>
                  <span className="text-xs text-gray-500">心理鸭</span>
                </div>
              )}
              
              <Card className={`${
                message.role === 'user' 
                  ? 'bg-amber-400 text-white' 
                  : 'bg-white border-amber-200'
              }`}>
                <CardContent className="p-3">
                  <p className="text-sm leading-relaxed">{message.text}</p>
                  
                  {/* 漫画面板 */}
                  {message.panel && (
                    <div className="mt-3 rounded-lg overflow-hidden">
                      <div className="w-full h-32 bg-gradient-to-r from-amber-100 to-yellow-100 flex items-center justify-center">
                        <Image className="text-amber-500" size={32} />
                        <span className="ml-2 text-sm text-amber-600">温暖插画</span>
                      </div>
                    </div>
                  )}
                  
                  {/* 视频 */}
                  {message.video && (
                    <div className="mt-3 rounded-lg overflow-hidden">
                      <div className="w-full h-32 bg-gradient-to-r from-blue-100 to-cyan-100 flex items-center justify-center">
                        <Video className="text-blue-500" size={32} />
                        <span className="ml-2 text-sm text-blue-600">疗愈视频</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              <div className="text-xs text-gray-400 mt-1 px-2">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        
        {/* 鸭鸭思考中的加载状态 */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md">
              <div className="flex items-center mb-1">
                <span className="text-lg mr-1">🦆</span>
                <span className="text-xs text-gray-500">心理鸭</span>
              </div>
              
              <Card className="bg-white border-amber-200">
                <CardContent className="p-3">
                  {/* <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-amber-500" />
                    <span className="text-sm text-gray-600">鸭鸭正在思考中...</span>
                  </div> */}
                  
                  {/* 思考动画点点 */}
                  <div className="flex space-x-1 mt-2">
                    <div className="w-2 h-2 bg-amber-300 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                    <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                  </div>
                </CardContent>
              </Card>
              
              <div className="text-xs text-gray-400 mt-1 px-2">
                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white/80 backdrop-blur-md border-t border-amber-200/50 p-4">
        <div className="flex items-center space-x-2 max-w-4xl mx-auto">
          <Input
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isLoading ? "鸭鸭正在回复中..." : "和鸭鸭说说心里话..."}
            className="flex-1 border-amber-200 focus:border-amber-400"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            size="icon"
            className="bg-amber-500 hover:bg-amber-600 text-white disabled:bg-gray-300"
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </Button>
        </div>
      </div>

      {/* 情绪报告弹窗 */}
      <EmotionReport 
        isOpen={showEmotionReport}
        onClose={() => setShowEmotionReport(false)}
      />
    </div>
  );
};

export default Chat;