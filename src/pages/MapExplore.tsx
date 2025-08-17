import React, { useState } from 'react';
import { ChevronRight, Play, Heart, Wind } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Scene } from '../data';
import { scenes, getTodayScene } from '../data/scenes';

const MapExplore: React.FC = () => {
  const [currentScene, setCurrentScene] = useState<Scene | null>(null);
  const [isInteracting, setIsInteracting] = useState(false);

  const todayScene = getTodayScene();

  const handleSceneEnter = (scene: Scene) => {
    setCurrentScene(scene);
  };

  const handleInteraction = () => {
    setIsInteracting(true);
    setTimeout(() => {
      setIsInteracting(false);
    }, 3000);
  };

  const handleBackToMap = () => {
    setCurrentScene(null);
  };

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
          <h1 className="text-xl font-semibold text-gray-800 mb-1">一起走走</h1>
          <p className="text-sm text-gray-600">和鸭鸭探索疗愈的场景</p>
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