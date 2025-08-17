import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, Map, BookOpen, Heart } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { getTodayQuote } from '../data/quotes';
import StorageService from '../services/storage';

const Home: React.FC = () => {
  const [duckAnimation, setDuckAnimation] = useState('🦆');
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const storageService = StorageService.getInstance();
  
  // 模拟鸭鸭动画（更丰富的表情）
  useEffect(() => {
    const expressions = ['🦆', '😊', '🥰', '😌', '✨'];
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      currentIndex = (currentIndex + 1) % expressions.length;
      setDuckAnimation(expressions[currentIndex]);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  // 检查是否有新消息
  useEffect(() => {
    const messages = storageService.getMessages();
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      // 如果最后一条消息是鸭鸭回复，则认为有新消息
      setHasNewMessage(lastMessage.role === 'duck');
    }
  }, []);

  const todayQuote = getTodayQuote();

  const features = [
    {
      title: "和鸭鸭聊聊",
      description: "倾诉心事，获得温暖陪伴",
      icon: MessageCircle,
      path: "/chat",
      color: "bg-gradient-to-br from-amber-400 to-orange-400",
      textColor: "text-white",
      hasNotification: hasNewMessage
    },
    {
      title: "一起走走",
      description: "探索疗愈故事场景",
      icon: Map,
      path: "/map",
      color: "bg-gradient-to-br from-blue-400 to-indigo-400",
      textColor: "text-white"
    },
    {
      title: "记忆封存",
      description: "珍藏美好时光片段",
      icon: BookOpen,
      path: "/memories",
      color: "bg-gradient-to-br from-pink-400 to-rose-400",
      textColor: "text-white"
    }
  ];

  return (
    <div className="h-full bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex flex-col">
      {/* 动态心理鸭 */}
      <div className="text-center pt-6 pb-4 flex-shrink-0">
        <div className="relative inline-block">
          <div className="text-6xl mb-3 transition-all duration-500 transform hover:scale-110">
            {duckAnimation}
          </div>
          <div className="absolute -inset-2 bg-gradient-to-r from-amber-200 to-yellow-200 opacity-30 blur-xl rounded-full animate-pulse"></div>
        </div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent mb-1">
          心理鸭
        </h1>
        <p className="text-sm text-amber-700/80">
          你的贴心陪伴小伙伴 ✨
        </p>
      </div>

      {/* 每日暖心话 */}
      <div className="px-6 pb-3 flex-shrink-0">
        <Card className="w-full max-w-sm mx-auto bg-gradient-to-r from-pink-50 to-rose-50 border-pink-200/50 shadow-lg shadow-pink-100/50">
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Heart className="text-pink-500 mr-2 animate-pulse" size={18} />
              <span className="text-sm font-medium text-rose-700">今日暖心话</span>
            </div>
            <p className="text-gray-700 leading-relaxed text-sm">
              {todayQuote.text}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 三大功能入口 */}
      <div className="flex-1 px-6 pb-4 flex flex-col justify-center">
        <div className="w-full max-w-sm mx-auto space-y-4">
          {features.map((feature, index) => (
            <Link key={index} to={feature.path}>
              <Card className="group hover:scale-105 hover:shadow-xl transition-all duration-300 overflow-hidden relative">
                <CardContent className={`p-0 ${feature.color} relative`}>
                  {/* 温暖的新消息提示 */}
                  {feature.hasNotification && (
                    <div className="absolute top-3 right-3 z-10">
                      <div className="relative">
                        <div className="w-4 h-4 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full flex items-center justify-center animate-bounce">
                          <span className="text-[8px]">✨</span>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full animate-ping opacity-30"></div>
                      </div>
                    </div>
                  )}
                  
                  <div className="p-6 flex items-center relative overflow-hidden">
                    {/* 背景光效 */}
                    <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent group-hover:from-white/20 transition-all duration-300"></div>
                    
                    <div className="flex-shrink-0 mr-4 relative z-10">
                      <div className="w-11 h-11 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                        <feature.icon className={feature.textColor} size={22} />
                      </div>
                    </div>
                    <div className="flex-1 relative z-10">
                      <h3 className={`text-base font-semibold ${feature.textColor} mb-1`}>
                        {feature.title}
                        {feature.hasNotification && (
                          <span className="ml-2 text-xs bg-gradient-to-r from-amber-200 to-yellow-200 text-amber-800 px-2 py-1 rounded-full font-medium">
                            🦆 鸭鸭找你
                          </span>
                        )}
                      </h3>
                      <p className={`text-xs ${feature.textColor} opacity-90 leading-relaxed`}>
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* 底部装饰 */}
      <div className="text-center pb-4 flex-shrink-0">
        <p className="text-xs text-amber-600/60">
          ✨ 一起创造温暖的回忆 ✨
        </p>
      </div>
    </div>
  );
};

export default Home;