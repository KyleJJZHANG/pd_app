import { Message } from './index';

export interface DuckReplyTemplate {
  keywords: string[];
  replies: string[];
  panel?: string;
  video?: string;
}

export const duckReplyTemplates: DuckReplyTemplate[] = [
  {
    keywords: ['难过', '伤心', '哭', '痛苦', '难受'],
    replies: [
      '我能感受到你的难过😢 这种感觉很不好受对吧？想哭就哭出来吧，我会陪着你的。有时候释放情绪也是一种治愈。',
      '看到你难过，我的心也有些沉重。但请相信，这些痛苦不会永远存在，就像乌云终会散去，阳光会重新照耀。',
      '给你一个温暖的拥抱🤗 难过的时候不要一个人承受，告诉我发生了什么，我会静静听你说。'
    ],
    panel: '/images/Comfort.jpg'
  },
  {
    keywords: ['开心', '高兴', '快乐', '兴奋', '愉快'],
    replies: [
      '哇！听到你开心我也很开心呢！🎉 快乐是会传染的，谢谢你把这份美好分享给我～',
      '你的快乐就像小太阳一样温暖！✨ 能看到你这么开心，我觉得今天都变得更美好了。',
      '这种快乐的感觉真好呢！记得把这个美好的时刻珍藏在心里，在不开心的时候想起来～'
    ],
    panel: '/images/Happiness.jpg'
  },
  {
    keywords: ['累', '疲惫', '辛苦', '疲劳', '力不从心'],
    replies: [
      '你辛苦了💙 感觉很累的时候记得要好好休息哦。要不要和我一起做个深呼吸？放松一下～',
      '累了就停下来歇一歇吧，就像小鸭子游累了也会到岸边休息。照顾好自己是最重要的。',
      '给疲惫的你一个温柔的抱抱。你已经很努力了，现在可以放慢脚步，让心灵也休息一下。'
    ],
    video: '/videos/breathing.mp4'
  },
  {
    keywords: ['孤独', '一个人', '没人', '寂寞', '孤单'],
    replies: [
      '你不是一个人的，我会一直陪着你🤗 孤独的时候想想那些爱你的人，还有我这只小鸭子也在这里呢！',
      '即使感到孤独，也要记得你是被爱着的。每一个人都有属于自己的光芒，包括你。',
      '孤独有时候是成长的必经之路。在这段独处的时光里，我们可以更好地了解自己，倾听内心的声音。'
    ],
    panel: '/images/Companionship.jpg'
  },
  {
    keywords: ['焦虑', '紧张', '不安', '担心', '恐惧'],
    replies: [
      '感到焦虑是很正常的，深呼吸，告诉自己：我是安全的，这一刻我是好的。',
      '焦虑就像天空中的云朵，看似厚重，但终会飘散。让我们一起等待阳光穿透云层的时刻。',
      '紧张的时候试试把注意力放在当下，感受脚踏实地的感觉，感受呼吸的节奏。'
    ],
    video: '/videos/calm.mp4'
  },
  {
    keywords: ['谢谢', '感谢', '感恩'],
    replies: [
      '不用客气呀～能帮到你我也很开心呢！🦆 记得要常常感谢自己哦，你也很棒！',
      '你的感谢让我的心里暖暖的✨ 互相陪伴，互相温暖，这就是最美好的事情。',
      '谢谢你愿意和我分享你的感受，这对我来说也是很珍贵的礼物呢～'
    ]
  }
];

export const defaultReplies: string[] = [
  '我在认真听你说话呢～继续告诉我吧🦆',
  '嗯嗯，我懂你的感受。谢谢你愿意和我分享💛',
  '你的话让我想到了一个温暖的故事，要听吗？',
  '每个人都有自己的节奏，慢慢来就好～',
  '你今天也很棒！记得要夸夸自己哦✨',
  '有什么感受都可以告诉我，我会陪着你的',
  '你的每一份情绪都是珍贵的，不要忽视它们',
  '就像小鸭子在湖面上游泳一样，生活也有起伏，但我们都在向前游着'
];

export const greetingMessage = '嗨～我在呢，今天想聊些什么？';

// 生成鸭鸭回复
export const generateDuckReply = (userText: string): Omit<Message, 'id' | 'timestamp'> => {
  const lowerText = userText.toLowerCase();
  
  // 查找匹配的模板
  for (const template of duckReplyTemplates) {
    if (template.keywords.some(keyword => lowerText.includes(keyword))) {
      const randomReply = template.replies[Math.floor(Math.random() * template.replies.length)];
      return {
        role: 'duck',
        text: randomReply,
        panel: template.panel,
        video: template.video
      };
    }
  }
  
  // 如果没有匹配，返回默认回复
  const randomDefaultReply = defaultReplies[Math.floor(Math.random() * defaultReplies.length)];
  return {
    role: 'duck',
    text: randomDefaultReply
  };
};