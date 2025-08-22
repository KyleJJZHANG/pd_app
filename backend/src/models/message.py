"""
Message Models for Duck Therapy System

Data models for chat messages and related structures.
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """Chat message model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "duck"] = Field(..., description="Message sender role")
    text: str = Field(..., min_length=1, description="Message content")
    
    # Optional media content
    panel_url: Optional[str] = Field(None, description="Comic panel URL")
    video_url: Optional[str] = Field(None, description="Video URL")
    
    # Metadata
    session_id: str = Field(..., description="Chat session identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Emotion analysis results (for user messages)
    emotion_tags: Optional[List[str]] = Field(None, description="Detected emotion tags")
    emotion_intensity: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Emotion intensity score"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatRequest(BaseModel):
    """Request model for chat API."""
    
    text: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: str = Field(..., description="Chat session ID")
    context: Optional[List[str]] = Field(default=None, max_length=10, description="Recent message context")


class ChatResponse(BaseModel):
    """Response model for chat API."""
    
    success: bool = Field(..., description="Request success status")
    user_message: Message = Field(..., description="Processed user message")
    duck_response: Message = Field(..., description="Duck's response message")
    
    # Additional response data
    emotion_analysis: Optional[dict] = Field(None, description="Emotion analysis results")
    content_recommendations: Optional[dict] = Field(None, description="Content recommendations")
    therapy_tip: Optional[dict] = Field(None, description="Therapy suggestion")
    
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageHistory(BaseModel):
    """Message history response model."""
    
    messages: List[Message] = Field(..., description="List of messages")
    total_count: int = Field(..., description="Total message count")
    has_more: bool = Field(..., description="Whether more messages exist")
    
    pagination: Optional[dict] = Field(None, description="Pagination info")


class SessionInfo(BaseModel):
    """Chat session information."""
    
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0, description="Total messages in session")
    
    # Session metadata
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[dict] = Field(None, description="Additional session data")