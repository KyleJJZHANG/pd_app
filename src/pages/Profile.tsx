import React, { useState, useEffect } from 'react';
import { User, Settings, Download, Trash2, BarChart3, HelpCircle, Edit2, Save, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import StorageService from '../services/storage';
import { UserProfile, getUserProfile, saveUserProfile } from '../data/profile';

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>(getUserProfile());
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    nickname: profile.nickname,
    bio: profile.bio
  });
  const [stats, setStats] = useState({
    totalMessages: 0,
    totalMemories: 0,
    daysUsed: 0,
    favoriteScene: ''
  });

  const storageService = StorageService.getInstance();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = () => {
    const messages = storageService.getMessages();
    const memories = storageService.getMemories();
    const timeline = storageService.getTimeline();
    
    // Calculate usage days (unique dates)
    const usageDates = new Set(
      timeline.map(entry => entry.createdAt.toDateString())
    );

    setStats({
      totalMessages: messages.filter(m => m.role === 'user').length,
      totalMemories: memories.length,
      daysUsed: usageDates.size,
      favoriteScene: '静谧森林' // 可以基于使用频率计算
    });
  };

  const handleSaveProfile = () => {
    const updatedProfile = {
      ...profile,
      nickname: editForm.nickname,
      bio: editForm.bio,
      lastUpdated: new Date()
    };
    setProfile(updatedProfile);
    saveUserProfile(updatedProfile);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditForm({
      nickname: profile.nickname,
      bio: profile.bio
    });
    setIsEditing(false);
  };

  const handlePreferenceChange = (key: keyof UserProfile['preferences'], value: boolean) => {
    const updatedProfile = {
      ...profile,
      preferences: {
        ...profile.preferences,
        [key]: value
      },
      lastUpdated: new Date()
    };
    setProfile(updatedProfile);
    saveUserProfile(updatedProfile);
  };

  const handleExportData = () => {
    const data = {
      profile,
      messages: storageService.getMessages(),
      memories: storageService.getMemories(),
      timeline: storageService.getTimeline(),
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `心理鸭数据_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleClearAllData = () => {
    if (window.confirm('确定要清除所有数据吗？此操作不可撤销。')) {
      storageService.clearAllData();
      // 重置为默认配置
      const defaultProfile = getUserProfile();
      setProfile(defaultProfile);
      saveUserProfile(defaultProfile);
      setStats({
        totalMessages: 0,
        totalMemories: 0,
        daysUsed: 0,
        favoriteScene: ''
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-4">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800 mb-1">我的</h1>
            <p className="text-sm text-gray-600">个人资料与设置</p>
          </div>
          <span className="text-2xl">👤</span>
        </div>
      </div>

      <div className="max-w-md mx-auto space-y-6">
        {/* Profile Card */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">个人资料</CardTitle>
              {!isEditing && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit2 size={16} />
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center text-2xl">
                {profile.avatar}
              </div>
              <div className="flex-1">
                {isEditing ? (
                  <Input
                    value={editForm.nickname}
                    onChange={(e) => setEditForm({...editForm, nickname: e.target.value})}
                    placeholder="昵称"
                    className="mb-2"
                  />
                ) : (
                  <h3 className="text-lg font-semibold text-gray-800">{profile.nickname}</h3>
                )}
                <p className="text-sm text-gray-500">
                  加入于 {profile.createdAt.toLocaleDateString('zh-CN')}
                </p>
              </div>
            </div>
            
            {isEditing ? (
              <div className="space-y-3">
                <Input
                  value={editForm.bio}
                  onChange={(e) => setEditForm({...editForm, bio: e.target.value})}
                  placeholder="个人简介"
                />
                <div className="flex space-x-2">
                  <Button onClick={handleSaveProfile} size="sm" className="flex-1">
                    <Save size={14} className="mr-1" />
                    保存
                  </Button>
                  <Button onClick={handleCancelEdit} variant="outline" size="sm" className="flex-1">
                    <X size={14} className="mr-1" />
                    取消
                  </Button>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-600">{profile.bio}</p>
            )}
          </CardContent>
        </Card>

        {/* Usage Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <BarChart3 className="mr-2" size={20} />
              使用统计
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-amber-600">{stats.totalMessages}</div>
                <div className="text-xs text-gray-500">聊天消息</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.totalMemories}</div>
                <div className="text-xs text-gray-500">封存记忆</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.daysUsed}</div>
                <div className="text-xs text-gray-500">使用天数</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-purple-600">{stats.favoriteScene}</div>
                <div className="text-xs text-gray-500">喜爱场景</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* App Preferences */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Settings className="mr-2" size={20} />
              应用设置
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">每日提醒</div>
                <div className="text-sm text-gray-500">接收温柔的每日关怀提醒</div>
              </div>
              <Switch
                checked={profile.preferences.dailyReminder}
                onCheckedChange={(checked) => handlePreferenceChange('dailyReminder', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">动画效果</div>
                <div className="text-sm text-gray-500">启用鸭鸭动画和过渡效果</div>
              </div>
              <Switch
                checked={profile.preferences.animations}
                onCheckedChange={(checked) => handlePreferenceChange('animations', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">音效反馈</div>
                <div className="text-sm text-gray-500">启用交互音效</div>
              </div>
              <Switch
                checked={profile.preferences.soundEffects}
                onCheckedChange={(checked) => handlePreferenceChange('soundEffects', checked)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">数据管理</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={handleExportData}
              variant="outline"
              className="w-full justify-start"
            >
              <Download className="mr-2" size={16} />
              导出我的数据
            </Button>
            
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50"
                >
                  <Trash2 className="mr-2" size={16} />
                  清除所有数据
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>确认清除数据</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    此操作将永久删除您的所有数据，包括：
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1 ml-4">
                    <li>• 所有聊天历史</li>
                    <li>• 封存的记忆</li>
                    <li>• 个人设置</li>
                    <li>• 使用记录</li>
                  </ul>
                  <p className="text-sm font-medium text-red-600">
                    此操作不可撤销，请谨慎操作。
                  </p>
                  <Button
                    onClick={handleClearAllData}
                    className="w-full bg-red-600 hover:bg-red-700"
                  >
                    确认清除所有数据
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>

        {/* Help & About */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <HelpCircle className="mr-2" size={20} />
              帮助与关于
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-center py-4">
              <div className="text-4xl mb-2">🦆</div>
              <div className="font-medium text-gray-800 mb-1">心理鸭 v1.0</div>
              <div className="text-sm text-gray-500 mb-4">
                你的贴心陪伴小伙伴
              </div>
              <Badge variant="secondary" className="text-xs">
                轻度心理陪伴与记忆疗愈空间
              </Badge>
            </div>
            
            <div className="text-center text-xs text-gray-500">
              <p>感谢你选择心理鸭作为你的陪伴伙伴</p>
              <p>愿每一天都充满温暖与希望 ✨</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;