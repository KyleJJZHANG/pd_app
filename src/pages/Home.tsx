import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, Map, BookOpen, Heart } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { getTodayQuote } from '../data/quotes';

const Home: React.FC = () => {
  const [duckAnimation, setDuckAnimation] = useState('🦆');
  
  // 模拟鸭鸭动画（眨眼等）
  useEffect(() => {
    const interval = setInterval(() => {
      setDuckAnimation(prev => prev === '🦆' ? '😊' : '🦆');
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const todayQuote = getTodayQuote();

  const features = [
    {
      title: "和鸭鸭聊聊",
      description: "倾诉心事，获得温暖陪伴",
      icon: MessageCircle,
      path: "/chat",
      color: "bg-gradient-to-br from-amber-400 to-yellow-500",
      textColor: "text-white"
    },
    {
      title: "一起走走",
      description: "探索疗愈故事场景",
      icon: Map,
      path: "/map",
      color: "bg-gradient-to-br from-blue-400 to-cyan-500",
      textColor: "text-white"
    },
    {
      title: "记忆封存",
      description: "珍藏美好时光片段",
      icon: BookOpen,
      path: "/memories",
      color: "bg-gradient-to-br from-green-400 to-emerald-500",
      textColor: "text-white"
    }
  ];

  return (
    <div className="min-h-screen p-6 flex flex-col items-center">
      {/* 动态心理鸭 */}
      <div className="text-center mt-8 mb-8">
        <div className="text-8xl mb-4 animate-bounce">
          {duckAnimation}
        </div>
        <h1 className="text-3xl font-bold text-amber-700 mb-2">
          心理鸭
        </h1>
        <p className="text-sm text-gray-600">
          你的贴心陪伴小伙伴
        </p>
      </div>

      {/* 每日暖心话 */}
      <Card className="w-full max-w-md mb-8 bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200">
        <CardContent className="p-6 text-center">
          <div className="flex items-center justify-center mb-3">
            <Heart className="text-pink-500 mr-2" size={20} />
            <span className="text-sm font-medium text-amber-700">今日暖心话</span>
          </div>
          <p className="text-gray-700 leading-relaxed">
            {todayQuote.text}
          </p>
        </CardContent>
      </Card>

      {/* 三大功能入口 */}
      <div className="w-full max-w-md space-y-4">
        {features.map((feature, index) => (
          <Link key={index} to={feature.path}>
            <Card className="hover:scale-105 transition-transform duration-200 overflow-hidden">
              <CardContent className={`p-0 ${feature.color}`}>
                <div className="p-6 flex items-center">
                  <div className="flex-shrink-0 mr-4">
                    <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                      <feature.icon className={feature.textColor} size={24} />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className={`text-lg font-semibold ${feature.textColor} mb-1`}>
                      {feature.title}
                    </h3>
                    <p className={`text-sm ${feature.textColor} opacity-90`}>
                      {feature.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* 底部装饰 */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-400">
          ✨ 一起创造温暖的回忆 ✨
        </p>
      </div>
    </div>
  );
};

export default Home;