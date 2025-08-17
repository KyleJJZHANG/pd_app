import { Scene } from './index';

export const scenes: Scene[] = [
  {
    id: 'forest',
    title: '静谧森林',
    description: '鸭鸭带你走进充满生机的森林',
    story: '阳光透过树叶洒在小径上，鸭鸭慢慢走在你身边。"你听，"它轻声说，"树叶在风中沙沙作响，就像在低声安慰着什么。每一棵树都有自己的故事，就像每个人都有自己的节奏。不用急，慢慢走就好。"',
    emoji: '🌲',
    color: 'from-green-400 to-emerald-500',
    interaction: {
      type: 'breathing',
      instruction: '和鸭鸭一起深呼吸，感受森林的清新空气'
    }
  },
  {
    id: 'lake',
    title: '宁静湖边',
    description: '在湖边聆听内心的声音',
    story: '湖水平静如镜，倒映着天空的云朵。鸭鸭坐在湖边的石头上，轻轻拍打着水面。"有时候心情就像这湖水，"它说，"会有波澜，也会有平静。但你看，不管怎样，湖水都能包容一切，最终归于宁静。"',
    emoji: '🏞️',
    color: 'from-blue-400 to-cyan-500',
    interaction: {
      type: 'listening',
      instruction: '闭上眼睛，听听湖水轻拍岸边的声音'
    }
  },
  {
    id: 'garden',
    title: '花园小径',
    description: '在花香中找到生活的美好',
    story: '小径两旁开满了各色花朵，蝴蝶在花间翩翩起舞。鸭鸭停在一朵向日葵前，"你知道吗？"它转过头看着你，"向日葵总是朝着太阳的方向。即使在阴天，它们也会努力寻找光明。我们也可以这样，总是向着温暖的方向生长。"',
    emoji: '🌻',
    color: 'from-yellow-400 to-orange-500',
    interaction: {
      type: 'watching',
      instruction: '观察花朵摇摆，感受生命的韵律'
    }
  },
  {
    id: 'starry',
    title: '星空下',
    description: '夜晚的温柔与宁静',
    story: '夜空中繁星点点，鸭鸭和你一起躺在草地上仰望星空。"每一颗星星都在自己的轨道上闪耀，"它轻声说道，"就像每个人都有自己独特的光芒。即使在最黑暗的夜里，星星也从未停止发光。你也是这样的星星。"',
    emoji: '✨',
    color: 'from-purple-400 to-indigo-500',
    interaction: {
      type: 'breathing',
      instruction: '在星空下放松身心，释放一天的疲惫'
    }
  },
  {
    id: 'meadow',
    title: '温暖草地',
    description: '在阳光草地上感受生命力',
    story: '微风轻拂过广阔的草地，野花点缀其间。鸭鸭在草地上自由地奔跑，然后回到你身边。"你看这些小草，"它说，"每一根都在努力向上生长，即使被风吹倒，也会重新站起来。坚韧而温柔，这就是生命的力量。"',
    emoji: '🌾',
    color: 'from-green-300 to-lime-400',
    interaction: {
      type: 'watching',
      instruction: '感受草地上的阳光，让温暖包围你'
    }
  },
  {
    id: 'mountain',
    title: '远山云海',
    description: '站在山顶俯瞰云海',
    story: '站在山顶上，云海在脚下翻滚。鸭鸭展开翅膀，仿佛要拥抱整个世界。"从这里看下去，"它说，"所有的烦恼都变得那么渺小。有时候我们需要站得高一些，才能看清楚什么是真正重要的。"',
    emoji: '⛰️',
    color: 'from-gray-400 to-blue-400',
    interaction: {
      type: 'breathing',
      instruction: '在山顶深呼吸，感受天地的广阔'
    }
  }
];

// 获取今日场景
export const getTodayScene = (): Scene => {
  const dayIndex = Math.floor(Date.now() / (1000 * 60 * 60 * 24)) % scenes.length;
  return scenes[dayIndex];
};

// 根据ID获取场景
export const getSceneById = (id: string): Scene | undefined => {
  return scenes.find(scene => scene.id === id);
};