import React, { useState } from 'react';
import { ChevronRight, Play, Heart, Wind, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import DuckIcon from '../components/ui/DuckIcon';
import { Scene } from '../data';
import { scenes, getTodayScene } from '../data/scenes';
import { warmQuotes } from '../data/quotes';

const MapExplore: React.FC = () => {
  const [currentScene, setCurrentScene] = useState<Scene | null>(null);
  const [isInteracting, setIsInteracting] = useState(false);
  const [step, setStep] = useState(0);
  const [enableAnimation, setEnableAnimation] = useState(true);

  const todayScene = getTodayScene();
  
  const currentWarmScene = scenes[step % scenes.length];

  const getCurrentQuote = () => {
    return warmQuotes[step % warmQuotes.length].text;
  };

  const handleSceneEnter = (scene: Scene) => {
    setCurrentScene(scene);
  };

  const handleWarmSceneStart = () => {
    setCurrentScene(null);
    setStep(0);
  };

  const handleNextScene = () => {
    setStep(prev => prev + 1);
  };

  const handleInteraction = () => {
    setIsInteracting(true);
    setTimeout(() => {
      setIsInteracting(false);
    }, 4000);
  };

  const handleBackToMap = () => {
    setCurrentScene(null);
    setStep(0);
  };

  // 温暖的场景体验组件
  const WarmSceneExperience = () => {
    const scene = currentWarmScene;
    
    return (
      <div className="h-full bg-gradient-to-br from-yellow-50 via-orange-50 to-pink-50 flex flex-col relative overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-white/85 to-yellow-50/80 backdrop-blur-md border-b border-yellow-200/30 p-4 flex-shrink-0 shadow-sm">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackToMap}
              className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 mr-3"
            >
              <ArrowLeft size={20} />
            </Button>
            <DuckIcon 
              variant="head" 
              size="lg" 
              background="soft"
              animated={false}
              className="mr-2"
            />
            <h1 className="text-xl font-semibold text-amber-800">鸭鸭的治愈旅行</h1>
          </div>
        </div>

        {/* Scene Content */}
        <div className="flex-1 flex flex-col p-6">
          {/* 漫画化场景背景 */}
          <div className={`relative h-64 w-full overflow-hidden rounded-3xl bg-gradient-to-b ${scene.color} mb-6 flex-shrink-0`}>
            {/* 漂浮的光效 */}
            <div className="absolute -left-10 top-6 h-24 w-24 rounded-full bg-white/70 blur-xl animate-pulse" />
            <div className="absolute left-8 top-16 h-32 w-32 rounded-full bg-white/60 blur-xl animate-pulse delay-1000" />
            <div className="absolute right-4 top-8 h-16 w-16 rounded-full bg-white/50 blur-lg animate-pulse delay-500" />
            
            {/* 场景装饰 */}
            <div className="absolute bottom-0 h-24 w-full bg-gradient-to-t from-white/30 to-transparent" />
            
            {/* 鸭鸭和场景图标 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4 animate-gentle-bounce">{scene.emoji}</div>
                <DuckIcon 
                  variant="letter" 
                  size="3xl" 
                  animated={true}
                  background="soft"
                />
              </div>
            </div>
            
            {/* 浮动动画背景 */}
            <div className="absolute inset-0 opacity-30">
              {/* 更多漂浮装饰 */}
              <div className="absolute top-4 left-8 w-2 h-2 bg-white/40 rounded-full animate-feather-drift" style={{animationDelay: '1s'}}></div>
              <div className="absolute top-12 right-12 w-3 h-3 bg-white/30 rounded-full animate-float" style={{animationDelay: '2s'}}></div>
              <div className="absolute bottom-8 left-16 w-2 h-2 bg-white/35 rounded-full animate-gentle-bounce" style={{animationDelay: '3s'}}></div>
            </div>
          </div>

          {/* 场景标题和故事 */}
          <div className="flex-1 flex flex-col justify-center space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-medium text-gray-800 mb-4">{scene.title}</h3>
              
              {/* 故事气泡 */}
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 mx-4 shadow-lg border border-amber-100 relative">
                {/* 手绘风格装饰角落 */}
                <div className="absolute top-2 right-2 w-3 h-3 border-r border-t border-amber-200 rounded-tr-lg opacity-50"></div>
                <div className="absolute bottom-2 left-2 w-3 h-3 border-l border-b border-amber-200 rounded-bl-lg opacity-50"></div>
                
                <div className="flex items-start space-x-3 mb-4">
                  <DuckIcon 
                    variant="head" 
                    size="lg" 
                    background="warm"
                    className="mt-1 flex-shrink-0"
                  />
                  <div className="flex-1 text-left">
                    <p className="text-gray-700 leading-relaxed">
                      {scene.story}
                    </p>
                  </div>
                  {/* 小星星装饰 */}
                  <div className="text-amber-300/40 text-xs animate-pulse" style={{animationDelay: '1s'}}>✦</div>
                </div>
                
                {/* 交互按钮 */}
                <div className="space-y-4">
                  <Button
                    onClick={handleInteraction}
                    disabled={isInteracting}
                    className="w-full bg-gradient-to-r from-amber-400 to-yellow-500 text-white hover:from-amber-500 hover:to-yellow-600 active:from-amber-600 active:to-yellow-700 h-12 rounded-xl transition-all duration-200 touch-manipulation"
                    style={{ WebkitTapHighlightColor: 'transparent' }}
                  >
                    {isInteracting ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-pulse mr-2">🦆</div>
                        鸭鸭陪着你...
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        {scene.interaction.type === 'breathing' && <Wind className="mr-2" size={18} />}
                        {scene.interaction.type === 'listening' && <Heart className="mr-2" size={18} />}
                        {scene.interaction.type === 'watching' && <span className="mr-2">👀</span>}
                        {scene.interaction.instruction}
                      </div>
                    )}
                  </Button>
                  
                  {isInteracting && (
                    <div className="text-center animate-fade-in">
                      <p className="text-sm text-amber-700 mb-2">
                        {scene.interaction.type === 'breathing' && "慢慢呼吸，让心像湖水一样平静..."}
                        {scene.interaction.type === 'listening' && "静静聆听，内心的声音最真实..."}
                        {scene.interaction.type === 'watching' && "用心感受，这一刻只属于你..."}
                      </p>
                      <div className="flex justify-center">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-r from-amber-200 to-yellow-200 flex items-center justify-center animate-ping">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-amber-400 to-yellow-400 animate-pulse"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {!isInteracting && (
                    <div className="space-y-3">
                      {/* 心理鸭金句 */}
                      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl p-4 border border-amber-100 relative">
                        {/* 手绘风格引号装饰 */}
                        <div className="absolute top-1 left-1 text-amber-200 text-xs opacity-60">"</div>
                        <div className="absolute bottom-1 right-1 text-amber-200 text-xs opacity-60">"</div>
                        
                        <div className="flex items-start space-x-2 relative">
                          <DuckIcon 
                            variant="head" 
                            size="sm" 
                            background="warm"
                            className="mt-0.5 flex-shrink-0"
                          />
                          <p className="text-sm text-amber-800 font-medium italic">
                            "{getCurrentQuote()}"
                          </p>
                          {/* 小心心装饰 */}
                          <div className="text-amber-300/50 text-xs animate-pulse" style={{animationDelay: '2s'}}>♡</div>
                        </div>
                      </div>
                      
                      <Button
                        onClick={handleNextScene}
                        variant="outline"
                        className="w-full border-amber-200 text-amber-700 hover:bg-amber-50 active:bg-amber-100 h-12 rounded-xl transition-all duration-200 touch-manipulation"
                        style={{ WebkitTapHighlightColor: 'transparent' }}
                      >
                        🚶‍♀️ 和鸭鸭继续旅行
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 渲染温暖场景体验
  if (currentScene === null && step > 0) {
    return <WarmSceneExperience />;
  }

  if (currentScene) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-indigo-50 p-4 relative">
        <div className="bg-white/80 backdrop-blur-md rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={handleBackToMap}
              className="text-gray-600"
            >
              ← 返回地图
            </Button>
            <div className="flex items-center">
              <span className="text-2xl mr-2">{currentScene.emoji}</span>
              <h1 className="text-lg font-semibold text-gray-800">{currentScene.title}</h1>
            </div>
          </div>
        </div>

        <div className="max-w-md mx-auto space-y-6">
          <Card className={`bg-gradient-to-br ${currentScene.color} text-white overflow-hidden`}>
            <CardContent className="p-8 text-center">
              <div className="text-6xl mb-4">{currentScene.emoji}</div>
              {/* <DuckIcon 
                variant="letter" 
                size="2xl" 
                animated={false}
                background="transparent"
                className="mb-4"
              /> */}
              <p className="text-sm opacity-90">鸭鸭和你一起在{currentScene.title}</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center mb-4">
                <DuckIcon 
                  variant="head" 
                  size="md" 
                  background="soft"
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-600">鸭鸭的话</span>
              </div>
              <p className="text-gray-700 leading-relaxed text-sm">
                {currentScene.story}
              </p>
            </CardContent>
          </Card>

          {currentScene.interaction && (
            <Card>
              <CardContent className="p-6 text-center">
                <div className="mb-4">
                  {currentScene.interaction.type === 'breathing' && <Wind className="mx-auto text-blue-500" size={32} />}
                  {currentScene.interaction.type === 'listening' && <Heart className="mx-auto text-pink-500" size={32} />}
                  {currentScene.interaction.type === 'watching' && <span className="text-3xl">👀</span>}
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  {currentScene.interaction.instruction}
                </p>
                <Button
                  onClick={handleInteraction}
                  disabled={isInteracting}
                  className="bg-gradient-to-r from-amber-400 to-yellow-500 text-white hover:from-amber-500 hover:to-yellow-600"
                >
                  {isInteracting ? (
                    <div className="flex items-center">
                      <div className="animate-pulse mr-2">💛</div>
                      感受中...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <Play size={16} className="mr-2" />
                      开始体验
                    </div>
                  )}
                </Button>
                {isInteracting && (
                  <p className="text-xs text-gray-500 mt-2">
                    深呼吸，让心灵平静下来...
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-25 via-orange-25 to-pink-25 p-4 relative overflow-hidden touch-pan-y">
      {/* 装饰性背景元素 */}
      <div className="absolute inset-0 pointer-events-none">
        {/* 飘散的羽毛 */}
        <div className="absolute top-20 left-10 w-3 h-3 bg-white/40 rounded-full animate-feather-drift"></div>
        <div className="absolute top-40 right-20 w-2 h-2 bg-yellow-200/50 rounded-full animate-gentle-bounce" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-60 left-1/3 w-4 h-4 bg-orange-200/40 rounded-full animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-32 right-1/4 w-2 h-2 bg-pink-200/30 rounded-full animate-feather-drift" style={{animationDelay: '3s'}}></div>
        
        {/* 水彩晕染效果 */}
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-gradient-radial from-yellow-100/25 to-transparent rounded-full blur-2xl animate-float-slow"></div>
        <div className="absolute top-1/3 -right-10 w-60 h-60 bg-gradient-radial from-orange-100/20 to-transparent rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-20 left-20 w-50 h-50 bg-gradient-radial from-pink-100/25 to-transparent rounded-full blur-2xl animate-gentle-bounce" style={{animationDelay: '4s'}}></div>
      </div>

      <div className="bg-gradient-to-r from-white/70 to-yellow-50/60 backdrop-blur-md rounded-2xl p-6 mb-6 shadow-lg border border-yellow-100/50 relative">
        <div className="text-center">
          {/* 可爱的鸭鸭表情动画 */}
          {/* <div className="mb-2">
            <DuckIcon 
              variant="letter" 
              size="xl" 
              animated={true}
              background="warm"
              className="mx-auto"
            />
          </div> */}
          <h1 className="text-xl font-bold text-orange-800 mb-2">鸭鸭的治愈小世界</h1>
          <p className="text-sm text-orange-700/80 leading-relaxed">来这里找个安静的角落坐一坐，让心情慢慢舒展开来～</p>
        </div>
      </div>

      <div className="max-w-md mx-auto mb-8 relative">
        <div className="text-center mb-6">
          <div className="inline-flex items-center bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-700 px-4 py-2 rounded-full text-sm shadow-sm border border-yellow-200/50 font-medium">
            ✨ 鸭鸭今天想和你去这里 ✨
          </div>
        </div>
        
        <Card 
          className="hover:scale-105 active:scale-95 transition-all duration-300 cursor-pointer overflow-hidden shadow-xl hover:shadow-2xl active:shadow-lg border-0 relative touch-manipulation" 
          onClick={() => handleSceneEnter(todayScene)}
          style={{ WebkitTapHighlightColor: 'transparent' }}
        >
          {/* 手绘风格外框装饰 */}
          <div className="absolute -top-1 -left-1 w-4 h-4 border-l-2 border-t-2 border-yellow-300 rounded-tl-lg opacity-60"></div>
          <div className="absolute -top-1 -right-1 w-4 h-4 border-r-2 border-t-2 border-orange-300 rounded-tr-lg opacity-60"></div>
          <div className="absolute -bottom-1 -left-1 w-4 h-4 border-l-2 border-b-2 border-pink-300 rounded-bl-lg opacity-60"></div>
          <div className="absolute -bottom-1 -right-1 w-4 h-4 border-r-2 border-b-2 border-yellow-300 rounded-br-lg opacity-60"></div>
          
          <CardContent className={`p-0 bg-gradient-to-br ${todayScene.color} text-white relative`}>
            {/* 装饰性光效 */}
            <div className="absolute top-2 right-2 w-8 h-8 bg-white/20 rounded-full blur-sm animate-pulse"></div>
            <div className="absolute bottom-4 left-4 w-6 h-6 bg-white/15 rounded-full blur-md animate-pulse" style={{animationDelay: '1s'}}></div>
            {/* 手绘风格星星装饰 */}
            <div className="absolute top-4 left-4 text-white/30 text-xs animate-pulse" style={{animationDelay: '2s'}}>✦</div>
            <div className="absolute top-8 right-8 text-white/25 text-sm animate-float" style={{animationDelay: '1.5s'}}>✧</div>
            
            <div className="p-6 relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="animate-float text-4xl">
                    {todayScene.emoji}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-1">{todayScene.title}</h3>
                    <p className="text-sm opacity-90 leading-relaxed">{todayScene.description}</p>
                  </div>
                </div>
                <ChevronRight size={24} className="text-white/80" />
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-white/20">
                <div className="flex items-center space-x-2">
                  <DuckIcon 
                    variant="head" 
                    size="lg" 
                    animated={false}
                    background="transparent"
                  />
                  <span className="text-sm opacity-75">和鸭鸭一起</span>
                </div>
                <span className="text-xs opacity-75 bg-white/10 px-2 py-1 rounded-full">轻触开始</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="max-w-md mx-auto relative">
        <div className="text-center mb-6">
          <h2 className="text-lg font-bold text-orange-800 mb-2">🌈 更多治愈小天地</h2>
          <p className="text-sm text-orange-600/80">每个地方都藏着不一样的温暖</p>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          {scenes.map((scene, index) => (
            <Card
              key={scene.id}
              className="hover:scale-105 active:scale-95 hover:-translate-y-1 active:translate-y-0 transition-all duration-300 cursor-pointer bg-gradient-to-br from-white/80 to-white/60 backdrop-blur-sm border-0 shadow-md hover:shadow-lg active:shadow-sm touch-manipulation"
              onClick={() => handleSceneEnter(scene)}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              <CardHeader className="pb-2 pt-4">
                <div className="text-center">
                  <div 
                    className={`text-3xl mb-3 ${index % 3 === 0 ? 'animate-gentle-bounce' : index % 3 === 1 ? 'animate-float' : 'animate-float-slow'}`}
                    style={{
                      animationDelay: `${index * 0.3}s`
                    }}
                  >
                    {scene.emoji}
                  </div>
                  <CardTitle className="text-sm font-bold text-gray-800 leading-tight">
                    {scene.title}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pt-1 pb-4">
                <p className="text-xs text-gray-600 text-center leading-relaxed px-1">
                  {scene.description}
                </p>
                {/* 小装饰 */}
                <div className="flex justify-center mt-2">
                  <div className="w-8 h-0.5 bg-gradient-to-r from-transparent via-orange-200 to-transparent rounded-full"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {/* 底部装饰 */}
        <div className="text-center mt-8 opacity-60">
          <div className="flex justify-center items-center space-x-2 mb-2">
            <div className="w-8 h-0.5 bg-gradient-to-r from-transparent via-orange-300 to-transparent rounded-full"></div>
            <span className="text-2xl animate-pulse">🦆</span>
            <div className="w-8 h-0.5 bg-gradient-to-r from-transparent via-orange-300 to-transparent rounded-full"></div>
          </div>
          <p className="text-xs text-orange-600 mb-4">选择一个你喜欢的地方吧～</p>
          
          {/* 手绘风格装饰线条 */}
          <div className="flex justify-center space-x-6 opacity-40">
            <div className="w-12 h-12 rounded-full border-2 border-dashed border-yellow-300 flex items-center justify-center">
              <div className="w-2 h-2 bg-yellow-300 rounded-full"></div>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-200/50 to-pink-200/50"></div>
            <div className="w-10 h-10 rounded-full border border-pink-300 flex items-center justify-center">
              <div className="w-1 h-1 bg-pink-300 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapExplore;