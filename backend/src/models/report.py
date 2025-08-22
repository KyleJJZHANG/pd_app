"""
Report Models for Duck Therapy System

Data models for daily reports, analytics, and insights.
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field
import uuid


class DailyReport(BaseModel):
    """Daily emotion and activity report model."""
    
    # Report identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Session identifier")
    report_date: date = Field(..., description="Report date")
    
    # Emotion summary
    emotion_summary: Dict = Field(..., description="Daily emotion analysis")
    dominant_emotion: str = Field(..., description="Most frequent emotion")
    emotion_stability: float = Field(
        ..., ge=0.0, le=1.0, description="Emotion stability score"
    )
    positive_moments: int = Field(..., ge=0, description="Count of positive moments")
    
    # Activity metrics
    total_interactions: int = Field(..., ge=0, description="Total chat interactions")
    active_time_minutes: Optional[int] = Field(
        None, ge=0, description="Total active time in minutes"
    )
    
    # Content engagement
    content_viewed: int = Field(..., ge=0, description="Content items viewed")
    content_feedback_given: int = Field(..., ge=0, description="Feedback items given")
    
    # Progress indicators
    growth_indicators: List[str] = Field(
        default_factory=list, description="Identified growth areas"
    )
    achievements: List[str] = Field(
        default_factory=list, description="Daily achievements"
    )
    
    # Insights and recommendations
    key_insights: List[str] = Field(
        default_factory=list, description="Key emotional insights"
    )
    gentle_suggestions: List[str] = Field(
        default_factory=list, description="Gentle improvement suggestions"
    )
    
    # Duck's encouragement
    duck_encouragement: str = Field(..., description="Personalized encouragement message")
    
    # Comparison data
    comparison_data: Optional[Dict] = Field(
        None, description="Comparison with previous periods"
    )
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0", description="Report format version")


class WeeklyReport(BaseModel):
    """Weekly emotion and progress report model."""
    
    # Report identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Session identifier")
    week_start: date = Field(..., description="Week start date")
    week_end: date = Field(..., description="Week end date")
    
    # Week summary
    week_summary: Dict = Field(..., description="Weekly overview")
    most_active_day: str = Field(..., description="Most active day of week")
    mood_trend: str = Field(..., description="Overall mood trend")
    
    # Daily breakdown
    daily_reports: List[DailyReport] = Field(
        default_factory=list, description="Daily reports for the week"
    )
    
    # Progress analysis
    emotional_growth: List[str] = Field(
        default_factory=list, description="Emotional growth observations"
    )
    behavioral_patterns: List[str] = Field(
        default_factory=list, description="Identified behavioral patterns"
    )
    
    # Recommendations
    focus_areas: List[str] = Field(
        default_factory=list, description="Areas to focus on next week"
    )
    celebration_points: List[str] = Field(
        default_factory=list, description="Points to celebrate"
    )
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)


class ReportGenerationRequest(BaseModel):
    """Request model for report generation."""
    
    session_id: str = Field(..., description="Session identifier")
    report_type: str = Field(..., description="Type of report to generate")
    
    # Date range
    start_date: Optional[date] = Field(None, description="Report start date")
    end_date: Optional[date] = Field(None, description="Report end date")
    
    # Options
    include_trends: bool = Field(default=True, description="Include trend analysis")
    include_comparisons: bool = Field(default=True, description="Include comparisons")
    detail_level: str = Field(default="standard", description="Report detail level")


class ReportGenerationResponse(BaseModel):
    """Response model for report generation."""
    
    success: bool = Field(..., description="Generation success status")
    report: Optional[DailyReport] = Field(None, description="Generated report")
    
    # Generation metadata
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )
    data_points_analyzed: Optional[int] = Field(
        None, description="Number of data points analyzed"
    )
    
    # Error information
    error: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(
        default_factory=list, description="Generation warnings"
    )


class EmotionInsight(BaseModel):
    """Emotion insight model for reports."""
    
    insight_type: str = Field(..., description="Type of insight")
    description: str = Field(..., description="Insight description")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Insight confidence score"
    )
    
    # Supporting data
    evidence: List[str] = Field(
        default_factory=list, description="Evidence supporting the insight"
    )
    related_emotions: List[str] = Field(
        default_factory=list, description="Related emotions"
    )
    
    # Actionable recommendations
    recommendations: List[str] = Field(
        default_factory=list, description="Actionable recommendations"
    )


class ProgressMetric(BaseModel):
    """Progress tracking metric model."""
    
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    
    # Change analysis
    change_amount: Optional[float] = Field(None, description="Absolute change")
    change_percentage: Optional[float] = Field(None, description="Percentage change")
    trend_direction: Optional[str] = Field(None, description="Trend direction")
    
    # Context
    metric_description: Optional[str] = Field(None, description="Metric description")
    unit: Optional[str] = Field(None, description="Measurement unit")
    
    # Evaluation
    is_improvement: Optional[bool] = Field(None, description="Whether change is positive")
    target_value: Optional[float] = Field(None, description="Target value if any")


class ReportSummary(BaseModel):
    """Summary of available reports."""
    
    session_id: str = Field(..., description="Session identifier")
    
    # Report counts
    total_daily_reports: int = Field(..., ge=0, description="Total daily reports")
    total_weekly_reports: int = Field(..., ge=0, description="Total weekly reports")
    
    # Date range
    first_report_date: Optional[date] = Field(None, description="First report date")
    latest_report_date: Optional[date] = Field(None, description="Latest report date")
    
    # Recent reports
    recent_reports: List[Dict] = Field(
        default_factory=list, description="Recent report summaries"
    )
    
    # Overall progress
    overall_progress_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Overall progress score"
    )
    key_achievements: List[str] = Field(
        default_factory=list, description="Key achievements across all reports"
    )