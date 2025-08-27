import React, { useState } from 'react';
import { ChevronRight, Play, Heart, Wind, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Scene } from '../data';
import { scenes, getTodayScene } from '../data/scenes';
import { warmQuotes } from '../data/quotes';

const MapExplore: React.FC = () => {
  const [currentScene, setCurrentScene] = useState<Scene | null>(null);
  const [isInteracting, setIsInteracting] = useState(false);
  const [step, setStep] = useState(0);

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
      <div className="h-full bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex flex-col">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-md border-b border-amber-200/50 p-4 flex-shrink-0">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackToMap}
              className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 mr-3"
            >
              <ArrowLeft size={20} />
            </Button>
            <span className="text-2xl mr-2">🦆</span>
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
              <div className="text-center animate-float">
                <div className="text-6xl mb-2">{scene.emoji}</div>
                <div className="text-4xl">🦆</div>
              </div>
            </div>
            
            {/* 浮动动画背景 */}
            <div className="absolute inset-0 animate-float-slow opacity-50" />
          </div>

          {/* 场景标题和故事 */}
          <div className="flex-1 flex flex-col justify-center space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-medium text-gray-800 mb-4">{scene.title}</h3>
              
              {/* 故事气泡 */}
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 mx-4 shadow-lg border border-amber-100">
                <div className="flex items-start space-x-3 mb-4">
                  <span className="text-2xl">🦆</span>
                  <div className="flex-1 text-left">
                    <p className="text-gray-700 leading-relaxed">
                      {scene.story}
                    </p>
                  </div>
                </div>
                
                {/* 交互按钮 */}
                <div className="space-y-4">
                  <Button
                    onClick={handleInteraction}
                    disabled={isInteracting}
                    className="w-full bg-gradient-to-r from-amber-400 to-yellow-500 text-white hover:from-amber-500 hover:to-yellow-600 h-12 rounded-xl"
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
                      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl p-4 border border-amber-100">
                        <div className="flex items-start space-x-2">
                          <span className="text-sm">🦆</span>
                          <p className="text-sm text-amber-800 font-medium italic">
                            "{getCurrentQuote()}"
                          </p>
                        </div>
                      </div>
                      
                      <Button
                        onClick={handleNextScene}
                        variant="outline"
                        className="w-full border-amber-200 text-amber-700 hover:bg-amber-50 h-12 rounded-xl"
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
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
              <div className="text-4xl mb-2">🦆</div>
              <p className="text-sm opacity-90">鸭鸭和你一起在{currentScene.title}</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center mb-4">
                <span className="text-lg mr-2">🦆</span>
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
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <div className="bg-white/80 backdrop-blur-md rounded-xl p-4 mb-6">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-gray-800 mb-1">鸭鸭的治愈空间</h1>
          <p className="text-sm text-gray-600">在这些场景里，找到内心的平静</p>
        </div>
      </div>

      <div className="max-w-md mx-auto mb-8">
        <div className="text-center mb-4">
          <div className="inline-flex items-center bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-sm">
            ✨ 今日推荐场景
          </div>
        </div>
        
        <Card className="hover:scale-105 transition-transform duration-200 cursor-pointer overflow-hidden" onClick={() => handleSceneEnter(todayScene)}>
          <CardContent className={`p-0 bg-gradient-to-br ${todayScene.color} text-white`}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <span className="text-3xl mr-3">{todayScene.emoji}</span>
                  <div>
                    <h3 className="text-lg font-semibold">{todayScene.title}</h3>
                    <p className="text-sm opacity-90">{todayScene.description}</p>
                  </div>
                </div>
                <ChevronRight size={20} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-2xl">🦆</span>
                <span className="text-xs opacity-75">点击进入场景</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="max-w-md mx-auto">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 text-center">所有场景</h2>
        <div className="grid grid-cols-2 gap-4">
          {scenes.map((scene) => (
            <Card
              key={scene.id}
              className="hover:scale-105 transition-transform duration-200 cursor-pointer"
              onClick={() => handleSceneEnter(scene)}
            >
              <CardHeader className="pb-3">
                <div className="text-center">
                  <div className="text-3xl mb-2">{scene.emoji}</div>
                  <CardTitle className="text-sm">{scene.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pt-0 pb-4">
                <p className="text-xs text-gray-600 text-center leading-relaxed">
                  {scene.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MapExplore;