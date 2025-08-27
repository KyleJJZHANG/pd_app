import { Scene } from './index';

// 基于心理鸭内容特点优化的场景数据
export const scenes: Scene[] = [
  {
    id: 'abandoned_city',
    title: '废弃城市的午后',
    description: '人类离开后的城市，只有时间慢慢流淌',
    story: '人类离开后的城市很安静，只有风在窗台间穿过。这里没有匆忙，只有时间慢慢流淌。让我们在这里坐一会儿，感受内心的宁静。',
    emoji: '🏙️',
    color: 'from-slate-400 to-blue-500',
    interaction: {
      type: 'breathing',
      instruction: '在废弃的城市中，和鸭鸭一起做深呼吸练习'
    }
  },
  {
    id: 'phone_booth',
    title: '废弃的电话亭',
    description: '一个可以倾诉心声的地方',
    story: '"废弃的电话亭？还可以用吗？" 有时候我们都需要一个地方，可以对着无人接听的电话，说出心里话。',
    emoji: '📞',
    color: 'from-red-400 to-pink-500',
    interaction: {
      type: 'listening',
      instruction: '在电话亭里，倾听内心最真实的声音'
    }
  },
  {
    id: 'summer_memory',
    title: '粘稠的夏日记忆',
    description: '回到那个温暖的夏日午后',
    story: '"给我3秒钟，带你回到那个粘稠夏日。" 蝉鸣声里藏着童年，树荫下有微风轻抚。那个夏天已经过去很多年了，你过得还好吗？',
    emoji: '☀️',
    color: 'from-yellow-400 to-orange-500',
    interaction: {
      type: 'watching',
      instruction: '闭上眼睛，回到那个温暖的夏日午后'
    }
  },
  {
    id: 'washing_machine',
    title: '今晚住在洗衣机里',
    description: '一个温暖安全的小空间',
    story: '"今晚就住在洗衣机里吧。" 有时候想要一个更小的空间，像洗衣机一样温暖安全，可以蜷缩起来不被打扰。',
    emoji: '🌀',
    color: 'from-cyan-400 to-teal-500',
    interaction: {
      type: 'breathing',
      instruction: '在这个小小的安全空间里，放松身心'
    }
  },
  {
    id: 'campus_typhoon',
    title: '台风天的校园',
    description: '雨声中的校园回忆',
    story: '"又幻想了，回到了那个台风天的校园。" 雨点打在窗上，教室里很安静。那时的我们，是否也曾感到孤单却又勇敢？',
    emoji: '🌪️',
    color: 'from-gray-400 to-slate-500',
    interaction: {
      type: 'listening',
      instruction: '听着雨声，回忆校园时光的美好与忧伤'
    }
  },
  {
    id: 'spring_planting',
    title: '在废弃城市种春天',
    description: '即使荒芜，也要种下希望',
    story: '"在废弃的人类城市种下春天。" 即使周围一片荒芜，我们依然可以种下希望。每一片新绿都是生命的勇敢。',
    emoji: '🌱',
    color: 'from-green-400 to-emerald-500',
    interaction: {
      type: 'watching',
      instruction: '种下一颗希望的种子，看它慢慢发芽'
    }
  },
  {
    id: 'quiet_lake',
    title: '宁静湖边',
    description: '在湖边聆听内心的声音',
    story: '湖水平静如镜，倒映着天空的云朵。鸭鸭坐在湖边的石头上，轻轻拍打着水面。"有时候心情就像这湖水，会有波澜，也会有平静。但你看，不管怎样，湖水都能包容一切，最终归于宁静。"',
    emoji: '🏞️',
    color: 'from-blue-400 to-cyan-500',
    interaction: {
      type: 'listening',
      instruction: '闭上眼睛，听听湖水轻拍岸边的声音'
    }
  },
  {
    id: 'starry_night',
    title: '星空下的思考',
    description: '夜晚的温柔与宁静',
    story: '夜空中繁星点点，鸭鸭和你一起躺在草地上仰望星空。"每一颗星星都在自己的轨道上闪耀，就像每个人都有自己独特的光芒。即使在最黑暗的夜里，星星也从未停止发光。"',
    emoji: '✨',
    color: 'from-purple-400 to-indigo-500',
    interaction: {
      type: 'breathing',
      instruction: '在星空下放松身心，释放一天的疲惫'
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