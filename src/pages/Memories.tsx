import React, { useState, useEffect } from 'react';
import { Plus, Search, Tag, Calendar, Trash2, Edit } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Badge } from '../components/ui/badge';
import { MemoryItem } from '../data';
import StorageService from '../services/storage';

const Memories: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState<string>('');
  const [isAddingMemory, setIsAddingMemory] = useState(false);
  const [newMemory, setNewMemory] = useState({
    title: '',
    content: '',
    tags: '' // 以逗号分隔的字符串
  });

  const storageService = StorageService.getInstance();

  useEffect(() => {
    loadMemories();
  }, []);

  const loadMemories = () => {
    const savedMemories = storageService.getMemories();
    setMemories(savedMemories);
  };

  const handleAddMemory = () => {
    if (!newMemory.title.trim() || !newMemory.content.trim()) return;

    const memory: MemoryItem = {
      id: `memory_${Date.now()}`,
      title: newMemory.title.trim(),
      content: newMemory.content.trim(),
      tags: newMemory.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0),
      createdAt: new Date(),
      type: 'text'
    };

    storageService.saveMemory(memory);
    setMemories([memory, ...memories]);
    setNewMemory({ title: '', content: '', tags: '' });
    setIsAddingMemory(false);
  };

  const handleDeleteMemory = (id: string) => {
    storageService.deleteMemory(id);
    setMemories(memories.filter(memory => memory.id !== id));
  };

  // 获取所有标签
  const allTags = Array.from(new Set(memories.flatMap(memory => memory.tags)));

  // 过滤记忆
  const filteredMemories = memories.filter(memory => {
    const matchesSearch = memory.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         memory.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTag = !selectedTag || memory.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-amber-50 p-4">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800 mb-1">记忆封存</h1>
            <p className="text-sm text-gray-600">珍藏美好时光片段</p>
          </div>
          <span className="text-2xl">📚</span>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="max-w-md mx-auto mb-6 space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
          <Input
            placeholder="搜索记忆..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 border-amber-200 focus:border-amber-400"
          />
        </div>

        {/* Tags Filter */}
        {allTags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedTag === '' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTag('')}
              className="text-xs"
            >
              全部
            </Button>
            {allTags.map(tag => (
              <Button
                key={tag}
                variant={selectedTag === tag ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedTag(tag)}
                className="text-xs"
              >
                {tag}
              </Button>
            ))}
          </div>
        )}
      </div>

      {/* Add Memory Button */}
      <div className="max-w-md mx-auto mb-6">
        <Dialog open={isAddingMemory} onOpenChange={setIsAddingMemory}>
          <DialogTrigger asChild>
            <Button className="w-full bg-gradient-to-r from-amber-400 to-yellow-500 text-white hover:from-amber-500 hover:to-yellow-600">
              <Plus size={16} className="mr-2" />
              新增记忆
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md mx-auto">
            <DialogHeader>
              <DialogTitle>封存新记忆</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <Input
                placeholder="记忆标题"
                value={newMemory.title}
                onChange={(e) => setNewMemory({...newMemory, title: e.target.value})}
              />
              <Textarea
                placeholder="记录这个美好的时刻..."
                value={newMemory.content}
                onChange={(e) => setNewMemory({...newMemory, content: e.target.value})}
                rows={4}
              />
              <Input
                placeholder="标签 (用逗号分隔，如：开心,朋友,旅行)"
                value={newMemory.tags}
                onChange={(e) => setNewMemory({...newMemory, tags: e.target.value})}
              />
              <div className="flex space-x-2">
                <Button
                  onClick={handleAddMemory}
                  disabled={!newMemory.title.trim() || !newMemory.content.trim()}
                  className="flex-1"
                >
                  保存记忆
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsAddingMemory(false)}
                >
                  取消
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Memories Grid */}
      <div className="max-w-md mx-auto">
        {filteredMemories.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <div className="text-4xl mb-4">🦆</div>
              <p className="text-gray-500 mb-4">
                {memories.length === 0 
                  ? "还没有封存的记忆呢～\n开始记录你的美好时光吧！" 
                  : "没有找到相关记忆\n试试其他搜索词？"
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredMemories.map((memory) => (
              <Card key={memory.id} className="hover:shadow-md transition-shadow duration-200">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg text-gray-800">{memory.title}</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteMemory(memory.id)}
                      className="text-gray-400 hover:text-red-500 p-1"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-gray-600 text-sm leading-relaxed mb-3">
                    {memory.content}
                  </p>
                  
                  {/* Tags */}
                  {memory.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {memory.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          <Tag size={10} className="mr-1" />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                  
                  {/* Date */}
                  <div className="flex items-center text-xs text-gray-400">
                    <Calendar size={12} className="mr-1" />
                    {memory.createdAt.toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Stats */}
        {memories.length > 0 && (
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500">
              已封存 {memories.length} 个美好记忆 ✨
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Memories;