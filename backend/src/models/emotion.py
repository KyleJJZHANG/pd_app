"""
Emotion Analysis Models for Duck Therapy System

Data models for emotion analysis and psychological assessment.
"""
from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class EmotionAnalysis(BaseModel):
    """Emotion analysis result model."""
    
    # Basic sentiment analysis
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        ..., description="Overall sentiment classification"
    )
    intensity: float = Field(
        ..., ge=0.0, le=1.0, description="Emotion intensity score"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Analysis confidence score"
    )
    
    # Detailed emotion breakdown
    primary_emotions: List[str] = Field(
        default_factory=list, description="Primary emotion tags"
    )
    secondary_emotions: List[str] = Field(
        default_factory=list, description="Secondary emotion tags"
    )
    
    # Content analysis
    keywords: List[str] = Field(
        default_factory=list, description="Extracted keywords"
    )
    topics: List[str] = Field(
        default_factory=list, description="Identified topics"
    )
    language_style: Optional[str] = Field(
        None, description="Language style characteristics"
    )
    
    # Psychological assessment
    psychological_needs: List[str] = Field(
        default_factory=list, description="Identified psychological needs"
    )
    urgency_level: int = Field(
        default=1, ge=1, le=5, description="Support urgency level (1-5)"
    )
    support_type: Optional[str] = Field(
        None, description="Recommended support type"
    )
    
    # Metadata
    processing_notes: Optional[str] = Field(
        None, description="Additional processing information"
    )
    analyzed_at: datetime = Field(default_factory=datetime.now)


class EmotionTrend(BaseModel):
    """Emotion trend analysis model."""
    
    date: datetime = Field(..., description="Analysis date")
    average_sentiment: float = Field(
        ..., ge=-1.0, le=1.0, description="Average sentiment score"
    )
    dominant_emotion: str = Field(..., description="Most frequent emotion")
    message_count: int = Field(..., ge=0, description="Number of messages analyzed")
    
    # Emotion distribution
    emotion_distribution: Dict[str, float] = Field(
        default_factory=dict, description="Emotion frequency distribution"
    )
    
    # Trend indicators
    mood_stability: float = Field(
        ..., ge=0.0, le=1.0, description="Mood stability score"
    )
    positive_ratio: float = Field(
        ..., ge=0.0, le=1.0, description="Ratio of positive emotions"
    )


class EmotionSummary(BaseModel):
    """Emotion analysis summary model."""
    
    session_id: str = Field(..., description="Session identifier")
    period_start: datetime = Field(..., description="Analysis period start")
    period_end: datetime = Field(..., description="Analysis period end")
    
    # Overall statistics
    total_messages: int = Field(..., ge=0, description="Total messages analyzed")
    average_intensity: float = Field(
        ..., ge=0.0, le=1.0, description="Average emotion intensity"
    )
    dominant_emotion: str = Field(..., description="Most frequent emotion")
    
    # Trend analysis
    daily_trends: List[EmotionTrend] = Field(
        default_factory=list, description="Daily emotion trends"
    )
    
    # Insights and recommendations
    insights: List[str] = Field(
        default_factory=list, description="Generated insights"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommended actions"
    )
    
    # Progress indicators
    improvement_areas: List[str] = Field(
        default_factory=list, description="Areas for improvement"
    )
    positive_highlights: List[str] = Field(
        default_factory=list, description="Positive developments"
    )


class EmotionAnalysisRequest(BaseModel):
    """Request model for emotion analysis."""
    
    text: str = Field(..., min_length=1, description="Text to analyze")
    context: Optional[List[str]] = Field(
        None, description="Additional context messages"
    )
    analysis_depth: Literal["basic", "standard", "detailed"] = Field(
        default="standard", description="Analysis depth level"
    )


class EmotionAnalysisResponse(BaseModel):
    """Response model for emotion analysis."""
    
    success: bool = Field(..., description="Analysis success status")
    analysis: Optional[EmotionAnalysis] = Field(
        None, description="Emotion analysis results"
    )
    
    # Additional response data
    suggestions: Optional[Dict[str, str]] = Field(
        None, description="Immediate support suggestions"
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class EmotionTag(BaseModel):
    """Emotion tag definition model."""
    
    name: str = Field(..., description="Emotion tag name")
    category: Literal["positive", "neutral", "negative"] = Field(
        ..., description="Emotion category"
    )
    intensity_weight: float = Field(
        default=1.0, ge=0.0, le=2.0, description="Intensity multiplier"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Associated keywords"
    )
    description: Optional[str] = Field(
        None, description="Emotion description"
    )