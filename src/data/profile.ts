export interface UserProfile {
  id: string;
  nickname: string;
  avatar: string;
  bio: string;
  createdAt: Date;
  lastUpdated: Date;
  preferences: {
    dailyReminder: boolean;
    animations: boolean;
    soundEffects: boolean;
    theme: 'light' | 'dark' | 'auto';
  };
}

const DEFAULT_PROFILE: UserProfile = {
  id: 'user_default',
  nickname: '鸭鸭的朋友',
  avatar: '🌟',
  bio: '和心理鸭一起成长的小伙伴',
  createdAt: new Date(),
  lastUpdated: new Date(),
  preferences: {
    dailyReminder: true,
    animations: true,
    soundEffects: false,
    theme: 'light'
  }
};

// 获取用户配置
export const getUserProfile = (): UserProfile => {
  const stored = localStorage.getItem('duck_user_profile');
  if (!stored) {
    // 如果没有存储的配置，创建默认配置
    const defaultProfile = { ...DEFAULT_PROFILE };
    saveUserProfile(defaultProfile);
    return defaultProfile;
  }
  
  try {
    const parsed = JSON.parse(stored);
    return {
      ...parsed,
      createdAt: new Date(parsed.createdAt),
      lastUpdated: new Date(parsed.lastUpdated)
    };
  } catch (error) {
    console.error('Error parsing user profile:', error);
    return { ...DEFAULT_PROFILE };
  }
};

// 保存用户配置
export const saveUserProfile = (profile: UserProfile): void => {
  localStorage.setItem('duck_user_profile', JSON.stringify(profile));
};

// 更新用户偏好设置
export const updateUserPreferences = (preferences: Partial<UserProfile['preferences']>): void => {
  const currentProfile = getUserProfile();
  const updatedProfile = {
    ...currentProfile,
    preferences: {
      ...currentProfile.preferences,
      ...preferences
    },
    lastUpdated: new Date()
  };
  saveUserProfile(updatedProfile);
};

// 获取用户统计信息
export const getUserStats = () => {
  const messages = JSON.parse(localStorage.getItem('duck_messages') || '[]');
  const memories = JSON.parse(localStorage.getItem('duck_memories') || '[]');
  const timeline = JSON.parse(localStorage.getItem('duck_timeline') || '[]');
  
  // 计算使用天数（基于时间线中的唯一日期）
  const usageDates = new Set(
    timeline.map((entry: { createdAt: string }) => 
      new Date(entry.createdAt).toDateString()
    )
  );

  return {
    totalMessages: messages.filter((m: { role: string }) => m.role === 'user').length,
    totalMemories: memories.length,
    daysUsed: usageDates.size,
    firstUseDate: timeline.length > 0 ? new Date(timeline[timeline.length - 1].createdAt) : new Date()
  };
};

// 导出用户数据
export const exportUserData = () => {
  const profile = getUserProfile();
  const messages = JSON.parse(localStorage.getItem('duck_messages') || '[]');
  const memories = JSON.parse(localStorage.getItem('duck_memories') || '[]');
  const timeline = JSON.parse(localStorage.getItem('duck_timeline') || '[]');
  
  return {
    profile,
    messages,
    memories,
    timeline,
    exportDate: new Date().toISOString(),
    version: '1.0'
  };
};