import { WarmQuote } from './index';

// 基于心理鸭经典内容的治愈金句
export const warmQuotes: WarmQuote[] = [
  {
    id: '1',
    text: '不必害怕离别，因为你本就勇敢而自由',
    category: 'comfort'
  },
  {
    id: '2',
    text: '请拥抱你那热烈而敏感的灵魂，哪怕孤身一人',
    category: 'encouragement'
  },
  {
    id: '3',
    text: '事已至此，先吃点东西吧',
    category: 'daily'
  },
  {
    id: '4',
    text: '那些都是使我成为我的理由',
    category: 'comfort'
  },
  {
    id: '5',
    text: '你一定要有自己的秘密项目',
    category: 'encouragement'
  },
  {
    id: '6',
    text: '等一下，最后看一眼这片天空吧',
    category: 'daily'
  },
  {
    id: '7',
    text: '人类离开后的城市，鸭鸭的旅行仍在继续',
    category: 'encouragement'
  },
  {
    id: '8',
    text: '当你被日复一日的生活困住，就坐船来这里',
    category: 'comfort'
  },
  {
    id: '9',
    text: '今天也要好好照顾自己哦～',
    category: 'daily'
  },
  {
    id: '10',
    text: '你已经很努力了，给自己一个拥抱吧',
    category: 'comfort'
  },
  {
    id: '11',
    text: '慢慢来，一切都会好起来的',
    category: 'encouragement'
  },
  {
    id: '12',
    text: '记得要温柔地对待自己',
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