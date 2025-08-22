# 内容管理系统文档

## 1. 内容管理概述

心理鸭应用的内容管理系统负责管理和提供与用户情绪状态相匹配的漫画和视频内容。系统通过智能匹配算法，为用户推荐最贴合其当前情绪的治愈性内容，增强陪伴体验。

### 1.1 内容类型

#### 漫画面板（Comic Panels）
- **格式**: JPG, PNG
- **尺寸**: 建议 800x600 至 1200x900
- **风格**: 鸭鸭 IP 风格，温暖治愈系
- **内容**: 情绪表达、安慰场景、励志瞬间

#### 视频片段（Video Clips）
- **格式**: MP4, WebM
- **时长**: 10-30 秒
- **分辨率**: 720p 或 1080p
- **内容**: 呼吸练习、冥想引导、温暖动画

### 1.2 内容分类体系

```
内容分类
├── 情绪类别
│   ├── 积极情绪
│   │   ├── 开心 (happy)
│   │   ├── 兴奋 (excited)
│   │   ├── 满足 (satisfied)
│   │   └── 感激 (grateful)
│   ├── 中性情绪
│   │   ├── 平静 (calm)
│   │   ├── 专注 (focused)
│   │   └── 思考 (contemplative)
│   └── 需要支持的情绪
│       ├── 悲伤 (sad)
│       ├── 焦虑 (anxious)
│       ├── 孤独 (lonely)
│       ├── 压力 (stressed)
│       └── 疲惫 (tired)
├── 场景类别
│   ├── 日常生活 (daily_life)
│   ├── 工作学习 (work_study)
│   ├── 人际关系 (relationships)
│   ├── 自我成长 (personal_growth)
│   └── 休闲娱乐 (leisure)
└── 治疗目的
    ├── 安慰陪伴 (comfort)
    ├── 情绪调节 (emotion_regulation)
    ├── 放松减压 (relaxation)
    ├── 积极鼓励 (encouragement)
    └── 技能指导 (skill_guidance)
```

## 2. 内容索引系统

### 2.1 内容元数据结构

```json
{
  "content_metadata": {
    "id": "panel_comfort_001",
    "type": "panel",
    "title": "温暖的拥抱",
    "description": "鸭鸭给予用户温暖拥抱的治愈画面",
    "file_info": {
      "filename": "warm_hug.jpg",
      "url": "/panels/warm_hug.jpg",
      "size": 245760,
      "format": "JPEG",
      "dimensions": {
        "width": 1000,
        "height": 750
      }
    },
    "content_tags": {
      "emotions": ["悲伤", "孤独", "需要安慰"],
      "scenarios": ["情感支持", "日常陪伴"],
      "therapy_purpose": ["安慰陪伴", "情绪调节"],
      "keywords": ["拥抱", "温暖", "陪伴", "安慰", "支持"]
    },
    "matching_scores": {
      "悲伤": 0.95,
      "孤独": 0.90,
      "焦虑": 0.75,
      "疲惫": 0.70
    },
    "usage_stats": {
      "view_count": 0,
      "positive_feedback": 0,
      "total_feedback": 0,
      "effectiveness_score": 0.0
    },
    "metadata": {
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": "content_team",
      "last_updated": "2024-01-01T00:00:00Z",
      "version": "1.0",
      "status": "active"
    }
  }
}
```

### 2.2 内容索引数据库设计

```sql
-- 内容基础表
CREATE TABLE content_assets (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'panel' | 'video'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    filename VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    file_size INTEGER,
    format VARCHAR(20),
    width INTEGER,
    height INTEGER,
    duration INTEGER, -- 仅视频有效，单位秒
    status VARCHAR(20) DEFAULT 'active', -- 'active' | 'inactive' | 'pending'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 情绪标签表
CREATE TABLE emotion_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'positive' | 'neutral' | 'negative'
    description TEXT
);

-- 内容情绪关联表
CREATE TABLE content_emotion_mapping (
    content_id VARCHAR(50) REFERENCES content_assets(id),
    emotion_tag_id INTEGER REFERENCES emotion_tags(id),
    relevance_score DECIMAL(3,2), -- 0.00 - 1.00
    PRIMARY KEY (content_id, emotion_tag_id)
);

-- 关键词表
CREATE TABLE content_keywords (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(50) REFERENCES content_assets(id),
    keyword VARCHAR(100) NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.00
);

-- 使用统计表
CREATE TABLE content_usage_stats (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(50) REFERENCES content_assets(id),
    session_id VARCHAR(100),
    user_feedback INTEGER, -- 1-5 评分
    context_emotion VARCHAR(50),
    shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_content_type ON content_assets(type);
CREATE INDEX idx_content_status ON content_assets(status);
CREATE INDEX idx_emotion_mapping_emotion ON content_emotion_mapping(emotion_tag_id);
CREATE INDEX idx_keywords_content ON content_keywords(content_id);
CREATE INDEX idx_usage_content ON content_usage_stats(content_id);
```

### 2.3 内容索引管理器

```python
# tools/content_indexer.py
from typing import List, Dict, Optional, Tuple
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ContentAsset:
    id: str
    type: str  # 'panel' | 'video'
    title: str
    description: str
    url: str
    emotion_tags: List[str]
    keywords: List[str]
    relevance_scores: Dict[str, float]
    
class ContentIndexer:
    """内容索引管理器"""
    
    def __init__(self, db_path: str = "content_index.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表结构（简化版）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_assets (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                emotion_tags TEXT, -- JSON 存储
                keywords TEXT,     -- JSON 存储
                relevance_scores TEXT, -- JSON 存储
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                session_id TEXT,
                emotion_context TEXT,
                feedback_score INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_assets (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_content(self, content: ContentAsset) -> bool:
        """添加内容到索引"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO content_assets 
                (id, type, title, description, url, emotion_tags, keywords, relevance_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content.id,
                content.type,
                content.title,
                content.description,
                content.url,
                json.dumps(content.emotion_tags),
                json.dumps(content.keywords),
                json.dumps(content.relevance_scores)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding content: {e}")
            return False
    
    def search_by_emotion(
        self, 
        emotions: List[str], 
        content_type: Optional[str] = None,
        limit: int = 5
    ) -> List[ContentAsset]:
        """根据情绪搜索内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, type, title, description, url, emotion_tags, keywords, relevance_scores
            FROM content_assets 
            WHERE status = 'active'
        """
        
        params = []
        
        if content_type:
            query += " AND type = ?"
            params.append(content_type)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # 计算相关度得分并排序
        scored_results = []
        for row in results:
            asset = self._row_to_content_asset(row)
            score = self._calculate_emotion_relevance(asset, emotions)
            scored_results.append((score, asset))
        
        # 按得分排序并返回前 N 个
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [asset for _, asset in scored_results[:limit]]
    
    def search_by_keywords(
        self, 
        keywords: List[str], 
        content_type: Optional[str] = None,
        limit: int = 5
    ) -> List[ContentAsset]:
        """根据关键词搜索内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, type, title, description, url, emotion_tags, keywords, relevance_scores
            FROM content_assets 
            WHERE status = 'active'
        """
        
        params = []
        
        if content_type:
            query += " AND type = ?"
            params.append(content_type)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # 计算关键词匹配得分
        scored_results = []
        for row in results:
            asset = self._row_to_content_asset(row)
            score = self._calculate_keyword_relevance(asset, keywords)
            scored_results.append((score, asset))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [asset for _, asset in scored_results[:limit]]
    
    def record_usage(
        self, 
        content_id: str, 
        session_id: str, 
        emotion_context: str,
        feedback_score: Optional[int] = None
    ):
        """记录内容使用情况"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO content_usage 
                (content_id, session_id, emotion_context, feedback_score)
                VALUES (?, ?, ?, ?)
            """, (content_id, session_id, emotion_context, feedback_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording usage: {e}")
    
    def get_content_stats(self, content_id: str) -> Dict:
        """获取内容统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as view_count,
                AVG(feedback_score) as avg_rating,
                COUNT(feedback_score) as rating_count
            FROM content_usage 
            WHERE content_id = ? AND feedback_score IS NOT NULL
        """, (content_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "view_count": result[0] or 0,
            "average_rating": result[1] or 0.0,
            "rating_count": result[2] or 0
        }
    
    def _row_to_content_asset(self, row) -> ContentAsset:
        """将数据库行转换为 ContentAsset 对象"""
        return ContentAsset(
            id=row[0],
            type=row[1],
            title=row[2],
            description=row[3],
            url=row[4],
            emotion_tags=json.loads(row[5] or '[]'),
            keywords=json.loads(row[6] or '[]'),
            relevance_scores=json.loads(row[7] or '{}')
        )
    
    def _calculate_emotion_relevance(
        self, 
        asset: ContentAsset, 
        emotions: List[str]
    ) -> float:
        """计算情绪相关度得分"""
        total_score = 0.0
        
        for emotion in emotions:
            # 直接匹配
            if emotion in asset.relevance_scores:
                total_score += asset.relevance_scores[emotion]
            # 标签匹配
            elif emotion in asset.emotion_tags:
                total_score += 0.7  # 默认得分
        
        return total_score / len(emotions) if emotions else 0.0
    
    def _calculate_keyword_relevance(
        self, 
        asset: ContentAsset, 
        keywords: List[str]
    ) -> float:
        """计算关键词相关度得分"""
        matches = 0
        
        for keyword in keywords:
            if any(keyword in asset_keyword for asset_keyword in asset.keywords):
                matches += 1
            elif keyword in asset.title or keyword in asset.description:
                matches += 0.5
        
        return matches / len(keywords) if keywords else 0.0
```

## 3. 内容匹配算法

### 3.1 智能匹配策略

```python
# tools/content_matcher.py
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentMatcher:
    """智能内容匹配器"""
    
    def __init__(self, content_indexer: ContentIndexer):
        self.indexer = content_indexer
        self.emotion_weights = {
            "primary": 1.0,      # 主要情绪
            "secondary": 0.7,    # 次要情绪
            "context": 0.5       # 上下文情绪
        }
        
    def find_best_matches(
        self,
        emotion_analysis: Dict,
        content_type: Optional[str] = None,
        max_results: int = 3
    ) -> List[Tuple[ContentAsset, float]]:
        """找到最佳匹配内容"""
        
        # 提取情绪信息
        primary_emotions = emotion_analysis.get("primary_emotions", [])
        secondary_emotions = emotion_analysis.get("secondary_emotions", [])
        keywords = emotion_analysis.get("keywords", [])
        
        # 多策略匹配
        emotion_matches = self._emotion_based_matching(
            primary_emotions, secondary_emotions
        )
        
        keyword_matches = self._keyword_based_matching(keywords)
        
        context_matches = self._context_based_matching(emotion_analysis)
        
        # 合并和排序结果
        all_matches = self._merge_and_rank_results(
            emotion_matches, keyword_matches, context_matches
        )
        
        # 过滤内容类型
        if content_type:
            all_matches = [
                (asset, score) for asset, score in all_matches 
                if asset.type == content_type
            ]
        
        # 应用使用历史优化
        optimized_matches = self._apply_usage_optimization(all_matches)
        
        return optimized_matches[:max_results]
    
    def _emotion_based_matching(
        self, 
        primary_emotions: List[str], 
        secondary_emotions: List[str]
    ) -> List[Tuple[ContentAsset, float]]:
        """基于情绪的匹配"""
        results = []
        
        # 主要情绪匹配
        for emotion in primary_emotions:
            matches = self.indexer.search_by_emotion([emotion], limit=10)
            for asset in matches:
                score = asset.relevance_scores.get(emotion, 0.0) * self.emotion_weights["primary"]
                results.append((asset, score))
        
        # 次要情绪匹配
        for emotion in secondary_emotions:
            matches = self.indexer.search_by_emotion([emotion], limit=5)
            for asset in matches:
                score = asset.relevance_scores.get(emotion, 0.0) * self.emotion_weights["secondary"]
                results.append((asset, score))
        
        return results
    
    def _keyword_based_matching(self, keywords: List[str]) -> List[Tuple[ContentAsset, float]]:
        """基于关键词的匹配"""
        if not keywords:
            return []
        
        matches = self.indexer.search_by_keywords(keywords, limit=10)
        results = []
        
        for asset in matches:
            # 计算 TF-IDF 相似度
            score = self._calculate_tfidf_similarity(keywords, asset.keywords)
            results.append((asset, score))
        
        return results
    
    def _context_based_matching(self, emotion_analysis: Dict) -> List[Tuple[ContentAsset, float]]:
        """基于上下文的匹配"""
        results = []
        
        # 情绪强度考虑
        intensity = emotion_analysis.get("intensity", 0.5)
        sentiment = emotion_analysis.get("sentiment", "neutral")
        
        # 根据情绪强度调整策略
        if intensity > 0.8 and sentiment == "negative":
            # 高强度负面情绪，推荐安慰类内容
            comfort_content = self.indexer.search_by_emotion(["安慰", "支持"], limit=5)
            for asset in comfort_content:
                results.append((asset, 0.9))
        
        elif intensity > 0.8 and sentiment == "positive":
            # 高强度正面情绪，推荐庆祝类内容
            celebration_content = self.indexer.search_by_emotion(["庆祝", "开心"], limit=5)
            for asset in celebration_content:
                results.append((asset, 0.8))
        
        return results
    
    def _merge_and_rank_results(
        self, 
        *result_lists: List[Tuple[ContentAsset, float]]
    ) -> List[Tuple[ContentAsset, float]]:
        """合并并排序结果"""
        # 合并所有结果
        all_results = {}
        
        for result_list in result_lists:
            for asset, score in result_list:
                if asset.id in all_results:
                    # 累加得分
                    all_results[asset.id] = (asset, all_results[asset.id][1] + score)
                else:
                    all_results[asset.id] = (asset, score)
        
        # 排序
        sorted_results = sorted(
            all_results.values(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_results
    
    def _apply_usage_optimization(
        self, 
        matches: List[Tuple[ContentAsset, float]]
    ) -> List[Tuple[ContentAsset, float]]:
        """应用使用历史优化"""
        optimized = []
        
        for asset, score in matches:
            stats = self.indexer.get_content_stats(asset.id)
            
            # 考虑用户反馈
            if stats["rating_count"] > 0:
                rating_boost = (stats["average_rating"] - 3.0) * 0.1  # -0.2 到 +0.2
                score += rating_boost
            
            # 避免过度重复（降低已经显示过很多次的内容的权重）
            if stats["view_count"] > 10:
                repetition_penalty = min(0.2, stats["view_count"] * 0.01)
                score -= repetition_penalty
            
            optimized.append((asset, max(0.0, score)))
        
        # 重新排序
        return sorted(optimized, key=lambda x: x[1], reverse=True)
    
    def _calculate_tfidf_similarity(self, query_keywords: List[str], asset_keywords: List[str]) -> float:
        """计算 TF-IDF 相似度"""
        if not query_keywords or not asset_keywords:
            return 0.0
        
        # 简化的相似度计算
        query_text = " ".join(query_keywords)
        asset_text = " ".join(asset_keywords)
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([query_text, asset_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
        except:
            # 回退到简单的词汇重叠
            overlap = len(set(query_keywords) & set(asset_keywords))
            return overlap / max(len(query_keywords), len(asset_keywords))
```

### 3.2 个性化推荐

```python
# tools/personalized_recommender.py
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import json

class PersonalizedRecommender:
    """个性化推荐系统"""
    
    def __init__(self, content_matcher: ContentMatcher):
        self.matcher = content_matcher
        self.user_profiles = {}  # 用户画像缓存
    
    def get_personalized_recommendations(
        self,
        session_id: str,
        emotion_analysis: Dict,
        max_results: int = 3
    ) -> List[Tuple[ContentAsset, float]]:
        """获取个性化推荐"""
        
        # 获取用户画像
        user_profile = self.get_user_profile(session_id)
        
        # 基础匹配
        base_matches = self.matcher.find_best_matches(
            emotion_analysis, max_results=max_results * 2
        )
        
        # 应用个性化调整
        personalized_matches = []
        
        for asset, score in base_matches:
            # 用户偏好调整
            preference_boost = self._calculate_preference_boost(asset, user_profile)
            
            # 多样性调整
            diversity_score = self._calculate_diversity_score(asset, user_profile)
            
            # 时间相关性调整
            temporal_boost = self._calculate_temporal_boost(asset, user_profile)
            
            # 综合得分
            final_score = score + preference_boost + diversity_score + temporal_boost
            personalized_matches.append((asset, final_score))
        
        # 排序并返回
        personalized_matches.sort(key=lambda x: x[1], reverse=True)
        return personalized_matches[:max_results]
    
    def get_user_profile(self, session_id: str) -> Dict:
        """获取用户画像"""
        if session_id in self.user_profiles:
            return self.user_profiles[session_id]
        
        # 从数据库加载用户历史
        profile = self._build_user_profile_from_history(session_id)
        self.user_profiles[session_id] = profile
        return profile
    
    def update_user_profile(
        self, 
        session_id: str, 
        content_id: str, 
        feedback_score: int,
        emotion_context: str
    ):
        """更新用户画像"""
        if session_id not in self.user_profiles:
            self.user_profiles[session_id] = self._create_empty_profile()
        
        profile = self.user_profiles[session_id]
        
        # 更新内容偏好
        if content_id not in profile["content_preferences"]:
            profile["content_preferences"][content_id] = []
        
        profile["content_preferences"][content_id].append({
            "feedback": feedback_score,
            "emotion": emotion_context,
            "timestamp": time.time()
        })
        
        # 更新情绪偏好
        if emotion_context in profile["emotion_preferences"]:
            # 加权平均
            current_score = profile["emotion_preferences"][emotion_context]
            profile["emotion_preferences"][emotion_context] = (
                current_score * 0.8 + feedback_score * 0.2
            )
        else:
            profile["emotion_preferences"][emotion_context] = feedback_score
        
        # 更新活跃时间
        hour = time.localtime().tm_hour
        profile["active_hours"][hour] += 1
        
        # 持久化更新
        self._save_user_profile(session_id, profile)
    
    def _build_user_profile_from_history(self, session_id: str) -> Dict:
        """从历史记录构建用户画像"""
        # 查询用户历史使用记录
        conn = sqlite3.connect(self.matcher.indexer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content_id, emotion_context, feedback_score, timestamp
            FROM content_usage 
            WHERE session_id = ? AND feedback_score IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
        """, (session_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        profile = self._create_empty_profile()
        
        # 分析历史记录
        for content_id, emotion_context, feedback_score, timestamp in history:
            # 内容偏好
            if content_id not in profile["content_preferences"]:
                profile["content_preferences"][content_id] = []
            
            profile["content_preferences"][content_id].append({
                "feedback": feedback_score,
                "emotion": emotion_context,
                "timestamp": timestamp
            })
            
            # 情绪偏好
            if emotion_context in profile["emotion_preferences"]:
                profile["emotion_preferences"][emotion_context] = (
                    profile["emotion_preferences"][emotion_context] * 0.9 + feedback_score * 0.1
                )
            else:
                profile["emotion_preferences"][emotion_context] = feedback_score
        
        return profile
    
    def _create_empty_profile(self) -> Dict:
        """创建空的用户画像"""
        return {
            "content_preferences": {},      # 内容偏好历史
            "emotion_preferences": {},      # 情绪内容偏好
            "active_hours": defaultdict(int),  # 活跃时间分布
            "content_type_preference": {   # 内容类型偏好
                "panel": 0.5,
                "video": 0.5
            },
            "diversity_preference": 0.5,   # 多样性偏好
            "created_at": time.time(),
            "last_updated": time.time()
        }
    
    def _calculate_preference_boost(self, asset: ContentAsset, profile: Dict) -> float:
        """计算用户偏好加成"""
        boost = 0.0
        
        # 内容类型偏好
        type_pref = profile["content_type_preference"].get(asset.type, 0.5)
        boost += (type_pref - 0.5) * 0.2
        
        # 相似内容偏好
        for content_id, feedbacks in profile["content_preferences"].items():
            if len(feedbacks) > 0:
                avg_feedback = sum(f["feedback"] for f in feedbacks) / len(feedbacks)
                if avg_feedback > 3.0:
                    # 如果用户喜欢相似内容，给予加成
                    similarity = self._calculate_content_similarity(asset.id, content_id)
                    boost += similarity * 0.15
        
        return boost
    
    def _calculate_diversity_score(self, asset: ContentAsset, profile: Dict) -> float:
        """计算多样性得分"""
        # 检查用户最近看过的内容
        recent_content = []
        current_time = time.time()
        
        for content_id, feedbacks in profile["content_preferences"].items():
            recent_feedbacks = [
                f for f in feedbacks 
                if current_time - f["timestamp"] < 86400  # 24小时内
            ]
            if recent_feedbacks:
                recent_content.append(content_id)
        
        # 如果当前内容与最近内容相似度过高，降低分数
        for recent_id in recent_content:
            similarity = self._calculate_content_similarity(asset.id, recent_id)
            if similarity > 0.8:
                return -0.3  # 重复内容惩罚
        
        return 0.1  # 新颖内容奖励
    
    def _calculate_temporal_boost(self, asset: ContentAsset, profile: Dict) -> float:
        """计算时间相关性加成"""
        current_hour = time.localtime().tm_hour
        
        # 如果用户在当前时间段更活跃，稍微提升推荐权重
        if profile["active_hours"][current_hour] > 0:
            return 0.05
        
        return 0.0
    
    def _calculate_content_similarity(self, content_id1: str, content_id2: str) -> float:
        """计算内容相似度"""
        # 简化实现，实际应该基于内容特征
        if content_id1 == content_id2:
            return 1.0
        
        # 基于 ID 前缀判断相似度（简化）
        prefix1 = content_id1.split('_')[0]
        prefix2 = content_id2.split('_')[0]
        
        if prefix1 == prefix2:
            return 0.7
        
        return 0.1
    
    def _save_user_profile(self, session_id: str, profile: Dict):
        """保存用户画像到存储"""
        # 这里可以保存到数据库或文件
        # 简化实现：保存到本地缓存
        profile["last_updated"] = time.time()
        self.user_profiles[session_id] = profile
```

## 4. 内容管理工具

### 4.1 内容批量导入工具

```python
# scripts/content_importer.py
import os
import json
import hashlib
from PIL import Image
import cv2
from pathlib import Path
from typing import Dict, List

class ContentImporter:
    """内容批量导入工具"""
    
    def __init__(self, content_indexer: ContentIndexer):
        self.indexer = content_indexer
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.webp'}
        self.supported_video_formats = {'.mp4', '.webm', '.mov'}
    
    def import_from_directory(self, directory_path: str, metadata_file: str = None):
        """从目录批量导入内容"""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # 加载元数据文件
        metadata = {}
        if metadata_file and os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # 遍历文件
        imported_count = 0
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                
                if file_extension in self.supported_image_formats:
                    success = self._import_image(file_path, metadata.get(file_path.name, {}))
                    if success:
                        imported_count += 1
                        
                elif file_extension in self.supported_video_formats:
                    success = self._import_video(file_path, metadata.get(file_path.name, {}))
                    if success:
                        imported_count += 1
        
        print(f"Successfully imported {imported_count} content items")
        return imported_count
    
    def _import_image(self, file_path: Path, file_metadata: Dict) -> bool:
        """导入图片内容"""
        try:
            # 生成唯一 ID
            content_id = self._generate_content_id(file_path, 'panel')
            
            # 获取图片信息
            with Image.open(file_path) as img:
                width, height = img.size
                file_size = file_path.stat().st_size
            
            # 创建 ContentAsset
            asset = ContentAsset(
                id=content_id,
                type='panel',
                title=file_metadata.get('title', file_path.stem),
                description=file_metadata.get('description', ''),
                url=f"/panels/{file_path.name}",
                emotion_tags=file_metadata.get('emotion_tags', []),
                keywords=file_metadata.get('keywords', []),
                relevance_scores=file_metadata.get('relevance_scores', {})
            )
            
            return self.indexer.add_content(asset)
            
        except Exception as e:
            print(f"Error importing image {file_path}: {e}")
            return False
    
    def _import_video(self, file_path: Path, file_metadata: Dict) -> bool:
        """导入视频内容"""
        try:
            content_id = self._generate_content_id(file_path, 'video')
            
            # 获取视频信息
            cap = cv2.VideoCapture(str(file_path))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            file_size = file_path.stat().st_size
            cap.release()
            
            asset = ContentAsset(
                id=content_id,
                type='video',
                title=file_metadata.get('title', file_path.stem),
                description=file_metadata.get('description', ''),
                url=f"/videos/{file_path.name}",
                emotion_tags=file_metadata.get('emotion_tags', []),
                keywords=file_metadata.get('keywords', []),
                relevance_scores=file_metadata.get('relevance_scores', {})
            )
            
            return self.indexer.add_content(asset)
            
        except Exception as e:
            print(f"Error importing video {file_path}: {e}")
            return False
    
    def _generate_content_id(self, file_path: Path, content_type: str) -> str:
        """生成内容唯一 ID"""
        # 基于文件路径和内容生成哈希
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        return f"{content_type}_{file_path.stem}_{file_hash}"
    
    def create_metadata_template(self, directory_path: str, output_file: str):
        """创建元数据模板文件"""
        directory = Path(directory_path)
        template = {}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                
                if (file_extension in self.supported_image_formats or 
                    file_extension in self.supported_video_formats):
                    
                    template[file_path.name] = {
                        "title": file_path.stem,
                        "description": "",
                        "emotion_tags": [],
                        "keywords": [],
                        "relevance_scores": {}
                    }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata template created: {output_file}")
```

### 4.2 内容质量检查工具

```python
# scripts/content_validator.py
from typing import Dict, List, Tuple
import os
from PIL import Image
import cv2

class ContentValidator:
    """内容质量检查工具"""
    
    def __init__(self):
        self.min_image_width = 400
        self.min_image_height = 300
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.min_video_duration = 5  # 5秒
        self.max_video_duration = 60  # 60秒
        self.max_video_size = 20 * 1024 * 1024  # 20MB
    
    def validate_content_directory(self, directory_path: str) -> Dict[str, List[str]]:
        """验证内容目录"""
        results = {
            "valid_files": [],
            "invalid_files": [],
            "warnings": [],
            "errors": []
        }
        
        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                validation_result = self.validate_single_file(file_path)
                
                if validation_result["is_valid"]:
                    results["valid_files"].append(file_path)
                else:
                    results["invalid_files"].append(file_path)
                
                results["warnings"].extend(validation_result["warnings"])
                results["errors"].extend(validation_result["errors"])
        
        return results
    
    def validate_single_file(self, file_path: str) -> Dict:
        """验证单个文件"""
        result = {
            "is_valid": False,
            "warnings": [],
            "errors": []
        }
        
        if not os.path.exists(file_path):
            result["errors"].append(f"File not found: {file_path}")
            return result
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension in ['.jpg', '.jpeg', '.png', '.webp']:
                result = self._validate_image(file_path)
            elif file_extension in ['.mp4', '.webm', '.mov']:
                result = self._validate_video(file_path)
            else:
                result["errors"].append(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            result["errors"].append(f"Validation error for {file_path}: {str(e)}")
        
        return result
    
    def _validate_image(self, file_path: str) -> Dict:
        """验证图片文件"""
        result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.max_image_size:
                result["errors"].append(f"Image file too large: {file_size / (1024*1024):.1f}MB")
                result["is_valid"] = False
            
            # 检查图片尺寸和格式
            with Image.open(file_path) as img:
                width, height = img.size
                
                if width < self.min_image_width:
                    result["warnings"].append(f"Image width too small: {width}px (min: {self.min_image_width}px)")
                
                if height < self.min_image_height:
                    result["warnings"].append(f"Image height too small: {height}px (min: {self.min_image_height}px)")
                
                # 检查图片质量
                if img.mode not in ['RGB', 'RGBA']:
                    result["warnings"].append(f"Unusual color mode: {img.mode}")
                
                # 检查 DPI（如果有）
                if hasattr(img, 'info') and 'dpi' in img.info:
                    dpi = img.info['dpi']
                    if isinstance(dpi, tuple) and dpi[0] < 72:
                        result["warnings"].append(f"Low DPI: {dpi[0]}")
                        
        except Exception as e:
            result["errors"].append(f"Cannot process image: {str(e)}")
            result["is_valid"] = False
        
        return result
    
    def _validate_video(self, file_path: str) -> Dict:
        """验证视频文件"""
        result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.max_video_size:
                result["errors"].append(f"Video file too large: {file_size / (1024*1024):.1f}MB")
                result["is_valid"] = False
            
            # 检查视频属性
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                result["errors"].append("Cannot open video file")
                result["is_valid"] = False
                return result
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if fps > 0:
                duration = frame_count / fps
                
                if duration < self.min_video_duration:
                    result["warnings"].append(f"Video too short: {duration:.1f}s (min: {self.min_video_duration}s)")
                
                if duration > self.max_video_duration:
                    result["warnings"].append(f"Video too long: {duration:.1f}s (max: {self.max_video_duration}s)")
            
            if width < 480:
                result["warnings"].append(f"Video width too small: {width}px")
            
            if height < 360:
                result["warnings"].append(f"Video height too small: {height}px")
            
            cap.release()
            
        except Exception as e:
            result["errors"].append(f"Cannot process video: {str(e)}")
            result["is_valid"] = False
        
        return result
    
    def generate_quality_report(self, validation_results: Dict) -> str:
        """生成质量报告"""
        report = []
        report.append("=== Content Quality Report ===\n")
        
        total_files = len(validation_results["valid_files"]) + len(validation_results["invalid_files"])
        valid_count = len(validation_results["valid_files"])
        
        report.append(f"Total files: {total_files}")
        report.append(f"Valid files: {valid_count}")
        report.append(f"Invalid files: {len(validation_results['invalid_files'])}")
        report.append(f"Success rate: {valid_count/total_files*100:.1f}%\n" if total_files > 0 else "No files found\n")
        
        if validation_results["errors"]:
            report.append("=== Errors ===")
            for error in validation_results["errors"]:
                report.append(f"❌ {error}")
            report.append("")
        
        if validation_results["warnings"]:
            report.append("=== Warnings ===")
            for warning in validation_results["warnings"]:
                report.append(f"⚠️  {warning}")
            report.append("")
        
        if validation_results["valid_files"]:
            report.append("=== Valid Files ===")
            for file_path in validation_results["valid_files"]:
                report.append(f"✅ {file_path}")
        
        return "\n".join(report)
```

## 5. 内容服务 API

### 5.1 内容推荐 API

```python
# api/content.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from tools.content_matcher import ContentMatcher
from tools.personalized_recommender import PersonalizedRecommender

router = APIRouter(prefix="/api/v1/content", tags=["content"])

class ContentRecommendationRequest(BaseModel):
    emotion_analysis: Dict
    session_id: str
    content_type: Optional[str] = None  # 'panel' | 'video'
    max_results: int = 3
    personalized: bool = True

class ContentRecommendationResponse(BaseModel):
    recommendations: List[Dict]
    match_explanation: str
    total_matches: int
    recommendation_id: str

class ContentFeedbackRequest(BaseModel):
    content_id: str
    session_id: str
    feedback_type: str  # 'helpful' | 'not_helpful' | 'inappropriate'
    rating: Optional[int] = None  # 1-5
    comment: Optional[str] = None

# 依赖注入
def get_content_services():
    from tools.content_indexer import ContentIndexer
    
    indexer = ContentIndexer()
    matcher = ContentMatcher(indexer)
    recommender = PersonalizedRecommender(matcher)
    
    return indexer, matcher, recommender

@router.post("/recommend", response_model=ContentRecommendationResponse)
async def recommend_content(
    request: ContentRecommendationRequest,
    services = Depends(get_content_services)
):
    """获取内容推荐"""
    indexer, matcher, recommender = services
    
    try:
        if request.personalized:
            # 个性化推荐
            matches = recommender.get_personalized_recommendations(
                session_id=request.session_id,
                emotion_analysis=request.emotion_analysis,
                max_results=request.max_results
            )
        else:
            # 基础推荐
            matches = matcher.find_best_matches(
                emotion_analysis=request.emotion_analysis,
                content_type=request.content_type,
                max_results=request.max_results
            )
        
        # 格式化响应
        recommendations = []
        for asset, score in matches:
            recommendations.append({
                "id": asset.id,
                "type": asset.type,
                "title": asset.title,
                "url": asset.url,
                "relevance_score": score,
                "emotion_match": asset.emotion_tags,
                "description": asset.description
            })
        
        # 生成推荐解释
        dominant_emotion = request.emotion_analysis.get("primary_emotions", [""])[0]
        explanation = f"基于你当前的{dominant_emotion}状态，为你推荐这些温暖的内容"
        
        recommendation_id = f"rec_{int(time.time())}_{request.session_id[:8]}"
        
        return ContentRecommendationResponse(
            recommendations=recommendations,
            match_explanation=explanation,
            total_matches=len(matches),
            recommendation_id=recommendation_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Content recommendation failed: {str(e)}"
        )

@router.post("/feedback")
async def submit_content_feedback(
    request: ContentFeedbackRequest,
    services = Depends(get_content_services)
):
    """提交内容反馈"""
    indexer, matcher, recommender = services
    
    try:
        # 记录使用统计
        feedback_score = request.rating if request.rating else (
            4 if request.feedback_type == "helpful" else
            2 if request.feedback_type == "not_helpful" else 1
        )
        
        indexer.record_usage(
            content_id=request.content_id,
            session_id=request.session_id,
            emotion_context="feedback",
            feedback_score=feedback_score
        )
        
        # 更新个性化推荐模型
        if request.rating:
            recommender.update_user_profile(
                session_id=request.session_id,
                content_id=request.content_id,
                feedback_score=request.rating,
                emotion_context="user_feedback"
            )
        
        return {"success": True, "message": "Feedback recorded"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback: {str(e)}"
        )

@router.get("/stats/{content_id}")
async def get_content_stats(
    content_id: str,
    services = Depends(get_content_services)
):
    """获取内容统计信息"""
    indexer, _, _ = services
    
    try:
        stats = indexer.get_content_stats(content_id)
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content stats: {str(e)}"
        )

@router.get("/library")
async def get_content_library(
    content_type: Optional[str] = None,
    emotion_tag: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    services = Depends(get_content_services)
):
    """获取内容库列表"""
    indexer, _, _ = services
    
    try:
        # 这里需要实现内容库查询功能
        # 简化实现
        content_list = []
        
        return {
            "success": True,
            "data": {
                "contents": content_list,
                "total": len(content_list),
                "has_more": False
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content library: {str(e)}"
        )
```

## 6. 部署和维护

### 6.1 内容 CDN 配置

```yaml
# docker-compose.yml 中的 CDN 配置
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./content:/usr/share/nginx/html/content
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - duck-therapy-backend

  duck-therapy-backend:
    # ... 其他配置
    volumes:
      - ./content:/app/content:ro  # 只读挂载内容目录
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # 启用 gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;
    
    # 静态内容缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|pdf|mp4|webm)$ {
        root /usr/share/nginx/html;
        expires 7d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://duck-therapy-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 6.2 内容监控和分析

```python
# scripts/content_analytics.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns

class ContentAnalytics:
    """内容分析工具"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def generate_usage_report(self, days: int = 30) -> Dict:
        """生成使用报告"""
        conn = sqlite3.connect(self.db_path)
        
        # 最近N天的使用数据
        since_date = datetime.now() - timedelta(days=days)
        
        usage_data = pd.read_sql_query("""
            SELECT 
                c.id,
                c.type,
                c.title,
                COUNT(u.id) as view_count,
                AVG(u.feedback_score) as avg_rating,
                COUNT(u.feedback_score) as rating_count
            FROM content_assets c
            LEFT JOIN content_usage u ON c.id = u.content_id
            WHERE u.timestamp > ? OR u.timestamp IS NULL
            GROUP BY c.id, c.type, c.title
            ORDER BY view_count DESC
        """, conn, params=[since_date.isoformat()])
        
        conn.close()
        
        # 生成统计
        report = {
            "period": f"Last {days} days",
            "total_content": len(usage_data),
            "total_views": usage_data["view_count"].sum(),
            "avg_rating": usage_data["avg_rating"].mean(),
            "top_content": usage_data.head(10).to_dict('records'),
            "content_by_type": usage_data.groupby('type')['view_count'].sum().to_dict(),
            "rating_distribution": usage_data["avg_rating"].value_counts().to_dict()
        }
        
        return report
    
    def identify_content_gaps(self) -> List[str]:
        """识别内容缺口"""
        conn = sqlite3.connect(self.db_path)
        
        # 查找没有对应内容的情绪
        emotion_usage = pd.read_sql_query("""
            SELECT emotion_context, COUNT(*) as request_count
            FROM content_usage
            WHERE feedback_score IS NULL  -- 没有找到合适内容
            GROUP BY emotion_context
            ORDER BY request_count DESC
        """, conn)
        
        conn.close()
        
        gaps = []
        for _, row in emotion_usage.iterrows():
            if row['request_count'] > 5:  # 超过5次请求但没有内容
                gaps.append(f"缺少 '{row['emotion_context']}' 相关内容 ({row['request_count']} 次请求)")
        
        return gaps
    
    def generate_content_performance_chart(self, output_path: str):
        """生成内容性能图表"""
        conn = sqlite3.connect(self.db_path)
        
        data = pd.read_sql_query("""
            SELECT 
                c.title,
                c.type,
                COUNT(u.id) as views,
                AVG(u.feedback_score) as rating
            FROM content_assets c
            LEFT JOIN content_usage u ON c.id = u.content_id
            WHERE u.feedback_score IS NOT NULL
            GROUP BY c.id, c.title, c.type
            HAVING COUNT(u.id) > 0
        """, conn)
        
        conn.close()
        
        if len(data) == 0:
            print("No data available for chart generation")
            return
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 观看次数 vs 评分散点图
        scatter = ax1.scatter(data['views'], data['rating'], 
                             c=data['type'].astype('category').cat.codes, 
                             alpha=0.6, s=50)
        ax1.set_xlabel('观看次数')
        ax1.set_ylabel('平均评分')
        ax1.set_title('内容性能分析')
        
        # 添加类型图例
        types = data['type'].unique()
        for i, content_type in enumerate(types):
            ax1.scatter([], [], c=f'C{i}', label=content_type)
        ax1.legend()
        
        # 内容类型分布饼图
        type_counts = data['type'].value_counts()
        ax2.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        ax2.set_title('内容类型分布')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to {output_path}")
```

这个内容管理系统文档提供了完整的内容管理解决方案，从内容索引、智能匹配到个性化推荐，确保系统能够为用户提供最贴合其情绪状态的治愈性内容。