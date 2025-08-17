import { WarmQuote } from './index';

export const warmQuotes: WarmQuote[] = [
  {
    id: '1',
    text: '今天也要好好照顾自己哦～',
    category: 'daily'
  },
  {
    id: '2',
    text: '你已经很努力了，给自己一个拥抱吧',
    category: 'comfort'
  },
  {
    id: '3',
    text: '慢慢来，一切都会好起来的',
    category: 'encouragement'
  },
  {
    id: '4',
    text: '记得要温柔地对待自己',
    category: 'daily'
  },
  {
    id: '5',
    text: '每一天都是新的开始',
    category: 'encouragement'
  },
  {
    id: '6',
    text: '你的感受都是有意义的',
    category: 'comfort'
  },
  {
    id: '7',
    text: '小小的进步也值得庆祝',
    category: 'encouragement'
  },
  {
    id: '8',
    text: '允许自己有不完美的时刻',
    category: 'comfort'
  },
  {
    id: '9',
    text: '今天的阳光格外温暖，就像你一样',
    category: 'daily'
  },
  {
    id: '10',
    text: '每一次呼吸都是新的希望',
    category: 'encouragement'
  },
  {
    id: '11',
    text: '你比你想象的更坚强',
    category: 'comfort'
  },
  {
    id: '12',
    text: '休息不是懒惰，是为了更好地前行',
    category: 'daily'
  }
];

// 获取今日暖心话
export const getTodayQuote = (): WarmQuote => {
  const dayIndex = Math.floor(Date.now() / (1000 * 60 * 60 * 24)) % warmQuotes.length;
  return warmQuotes[dayIndex];
};

// 获取随机暖心话
export const getRandomQuote = (): WarmQuote => {
  const randomIndex = Math.floor(Math.random() * warmQuotes.length);
  return warmQuotes[randomIndex];
};

// 根据分类获取暖心话
export const getQuotesByCategory = (category: WarmQuote['category']): WarmQuote[] => {
  return warmQuotes.filter(quote => quote.category === category);
};