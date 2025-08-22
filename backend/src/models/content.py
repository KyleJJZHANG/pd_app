"""
Content Models for Duck Therapy System

Data models for content assets, recommendations, and management.
"""
from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ContentAsset(BaseModel):
    """Content asset model for comics and videos."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["panel", "video"] = Field(..., description="Content type")
    
    # Basic information
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    
    # File information
    url: str = Field(..., description="Content URL or file path")
    filename: Optional[str] = Field(None, description="Original filename")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    
    # Media properties
    width: Optional[int] = Field(None, description="Image/video width")
    height: Optional[int] = Field(None, description="Image/video height")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    format: Optional[str] = Field(None, description="File format")
    
    # Content classification
    emotion_tags: List[str] = Field(
        default_factory=list, description="Associated emotion tags"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Content keywords"
    )
    categories: List[str] = Field(
        default_factory=list, description="Content categories"
    )
    
    # Relevance scoring
    emotion_relevance: Dict[str, float] = Field(
        default_factory=dict, description="Emotion relevance scores"
    )
    
    # Usage statistics
    view_count: int = Field(default=0, description="Number of times viewed")
    positive_feedback: int = Field(default=0, description="Positive feedback count")
    total_feedback: int = Field(default=0, description="Total feedback count")
    effectiveness_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Content effectiveness score"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="Content creator")
    status: Literal["active", "inactive", "pending"] = Field(
        default="active", description="Content status"
    )


class ContentRecommendation(BaseModel):
    """Content recommendation model."""
    
    content: ContentAsset = Field(..., description="Recommended content")
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Recommendation relevance score"
    )
    match_reasons: List[str] = Field(
        default_factory=list, description="Reasons for recommendation"
    )
    emotion_match: List[str] = Field(
        default_factory=list, description="Matched emotions"
    )


class ContentRecommendationRequest(BaseModel):
    """Request model for content recommendations."""
    
    emotion_analysis: Dict = Field(..., description="Emotion analysis data")
    session_id: str = Field(..., description="Session identifier")
    
    # Filtering options
    content_types: List[Literal["panel", "video"]] = Field(
        default=["panel", "video"], description="Requested content types"
    )
    max_items: int = Field(
        default=3, ge=1, le=10, description="Maximum recommendations"
    )
    
    # Personalization
    user_preferences: Optional[Dict] = Field(
        None, description="User preference data"
    )
    exclude_recent: bool = Field(
        default=True, description="Exclude recently shown content"
    )


class ContentRecommendationResponse(BaseModel):
    """Response model for content recommendations."""
    
    success: bool = Field(..., description="Request success status")
    recommendations: List[ContentRecommendation] = Field(
        default_factory=list, description="Content recommendations"
    )
    
    # Additional response data
    match_explanation: Optional[str] = Field(
        None, description="Explanation of matching logic"
    )
    total_matches: int = Field(default=0, description="Total matching content count")
    recommendation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Recommendation batch identifier"
    )
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )


class ContentFeedback(BaseModel):
    """Content feedback model."""
    
    content_id: str = Field(..., description="Content identifier")
    session_id: str = Field(..., description="Session identifier")
    recommendation_id: Optional[str] = Field(
        None, description="Recommendation batch identifier"
    )
    
    # Feedback data
    feedback_type: Literal["helpful", "not_helpful", "inappropriate"] = Field(
        ..., description="Feedback type"
    )
    rating: Optional[int] = Field(
        None, ge=1, le=5, description="Rating score (1-5)"
    )
    comment: Optional[str] = Field(
        None, max_length=500, description="Optional feedback comment"
    )
    
    # Context
    emotion_context: Optional[str] = Field(
        None, description="User's emotion when viewing content"
    )
    
    # Metadata
    submitted_at: datetime = Field(default_factory=datetime.now)


class ContentUsageStats(BaseModel):
    """Content usage statistics model."""
    
    content_id: str = Field(..., description="Content identifier")
    
    # Usage metrics
    view_count: int = Field(..., ge=0, description="Total view count")
    unique_viewers: int = Field(..., ge=0, description="Unique viewer count")
    average_rating: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Average user rating"
    )
    rating_count: int = Field(default=0, ge=0, description="Number of ratings")
    
    # Effectiveness metrics
    positive_feedback_ratio: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Positive feedback ratio"
    )
    recommendation_frequency: float = Field(
        default=0.0, ge=0.0, description="How often content is recommended"
    )
    
    # Temporal data
    last_viewed: Optional[datetime] = Field(None, description="Last view timestamp")
    popularity_trend: Optional[str] = Field(
        None, description="Popularity trend indicator"
    )


class ContentLibraryStats(BaseModel):
    """Overall content library statistics."""
    
    total_assets: int = Field(..., ge=0, description="Total content assets")
    active_assets: int = Field(..., ge=0, description="Active content assets")
    
    # Type distribution
    panel_count: int = Field(..., ge=0, description="Number of comic panels")
    video_count: int = Field(..., ge=0, description="Number of videos")
    
    # Quality metrics
    average_effectiveness: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Average content effectiveness"
    )
    total_views: int = Field(..., ge=0, description="Total content views")
    
    # Coverage analysis
    emotion_coverage: Dict[str, int] = Field(
        default_factory=dict, description="Content count per emotion"
    )
    content_gaps: List[str] = Field(
        default_factory=list, description="Identified content gaps"
    )
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now)