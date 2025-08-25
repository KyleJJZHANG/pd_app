"""
Chat API for Duck Therapy System

Handles therapeutic chat interactions using multi-agent workflows.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import json
import asyncio
from uuid import uuid4

from ..services.crew_manager import crew_manager, WorkflowStatus, StreamChunk, StreamChunkType
from ..models.message import Message
from loguru import logger

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message input model."""
    text: str = Field(..., min_length=1, max_length=2000, description="User message text")
    session_id: str = Field(..., description="Chat session identifier")
    context: Optional[List[str]] = Field(default=None, description="Recent conversation context")
    user_preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences for personalization")
    workflow_type: str = Field(default="basic_chat_flow", description="Type of workflow to execute")
    response_style: str = Field(default="standard", description="Response style: brief, standard, detailed")
    analysis_depth: str = Field(default="standard", description="Emotion analysis depth: basic, standard, detailed")


class ChatResponse(BaseModel):
    """Chat response output model."""
    message_id: str
    response_text: str
    emotion_analysis: Optional[Dict[str, Any]] = None
    content_recommendations: Optional[List[Dict[str, Any]]] = None
    therapy_suggestions: Optional[List[Dict[str, Any]]] = None
    workflow_executed: str
    execution_time_ms: int
    success_rate: float
    llm_providers_used: List[str]
    timestamp: datetime


class ChatSessionInfo(BaseModel):
    """Chat session information."""
    session_id: str
    created_at: datetime
    message_count: int
    last_activity: datetime
    status: str


# In-memory session storage (in production, use Redis or database)
chat_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage, background_tasks: BackgroundTasks):
    """
    Send a message to the duck therapy system.
    
    This endpoint processes user messages through the multi-agent workflow
    to provide therapeutic responses with emotion analysis.
    """
    try:
        start_time = datetime.now()
        
        # Validate session
        if message.session_id not in chat_sessions:
            chat_sessions[message.session_id] = {
                "created_at": start_time,
                "messages": [],
                "last_activity": start_time,
                "emotion_history": []
            }
        
        # Update session activity
        chat_sessions[message.session_id]["last_activity"] = start_time
        
        # Prepare input data for workflow
        input_data = {
            "user_message": message.text,
            "context": message.context or [],
            "user_preferences": message.user_preferences or {},
            "response_style": message.response_style,
            "analysis_depth": message.analysis_depth,
            "recent_content": [],  # TODO: Implement content history
            "user_history": chat_sessions[message.session_id].get("emotion_history", [])
        }
        
        # Execute workflow
        logger.info(f"Processing message for session {message.session_id} with workflow {message.workflow_type}")
        
        workflow_result = await crew_manager.execute_workflow(
            workflow_name=message.workflow_type,
            input_data=input_data,
            session_id=message.session_id
        )
        
        # Handle workflow failure
        if workflow_result.status == WorkflowStatus.FAILED:
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {workflow_result.error}"
            )
        
        # Extract response data
        final_output = workflow_result.final_output or {}
        response_text = final_output.get("response_text", "鸭鸭暂时无法回复，请稍后再试哦～")
        emotion_analysis = final_output.get("emotion_analysis")
        content_recommendations = final_output.get("content_recommendations")
        therapy_suggestions = final_output.get("therapy_suggestions")
        
        # Generate message ID
        message_id = str(uuid4())
        
        # Store message in session
        user_message_obj = {
            "id": str(uuid4()),
            "text": message.text,
            "type": "user",
            "timestamp": start_time.isoformat()
        }
        
        assistant_message_obj = {
            "id": message_id,
            "text": response_text,
            "type": "assistant",
            "timestamp": datetime.now().isoformat(),
            "emotion_analysis": emotion_analysis,
            "workflow_used": message.workflow_type
        }
        
        chat_sessions[message.session_id]["messages"].extend([
            user_message_obj,
            assistant_message_obj
        ])
        
        # Store emotion analysis in session history
        if emotion_analysis:
            chat_sessions[message.session_id]["emotion_history"].append({
                "timestamp": start_time.isoformat(),
                "analysis": emotion_analysis
            })
        
        # Collect LLM providers used
        llm_providers_used = list(set([
            task_result.llm_provider_used 
            for task_result in workflow_result.task_results 
            if task_result.llm_provider_used
        ]))
        
        # Schedule background tasks
        background_tasks.add_task(
            _update_session_analytics,
            message.session_id,
            emotion_analysis
        )
        
        # Create response
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = ChatResponse(
            message_id=message_id,
            response_text=response_text,
            emotion_analysis=emotion_analysis,
            content_recommendations=content_recommendations,
            therapy_suggestions=therapy_suggestions,
            workflow_executed=message.workflow_type,
            execution_time_ms=execution_time,
            success_rate=workflow_result.success_rate,
            llm_providers_used=llm_providers_used,
            timestamp=datetime.now()
        )
        
        logger.info(f"Message processed successfully for session {message.session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=ChatSessionInfo)
async def get_session_info(session_id: str):
    """Get information about a chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = chat_sessions[session_id]
    
    return ChatSessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        message_count=len(session_data["messages"]),
        last_activity=session_data["last_activity"],
        status="active"
    )


@router.get("/session/{session_id}/messages")
async def get_session_messages(
    session_id: str, 
    limit: int = 50, 
    offset: int = 0
):
    """Get messages from a chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = chat_sessions[session_id]["messages"]
    
    # Apply pagination
    start_idx = offset
    end_idx = offset + limit
    paginated_messages = messages[start_idx:end_idx]
    
    return {
        "session_id": session_id,
        "messages": paginated_messages,
        "total_count": len(messages),
        "offset": offset,
        "limit": limit,
        "has_more": end_idx < len(messages)
    }


@router.get("/session/{session_id}/emotion-history")
async def get_emotion_history(session_id: str):
    """Get emotion analysis history for a session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    emotion_history = chat_sessions[session_id].get("emotion_history", [])
    
    return {
        "session_id": session_id,
        "emotion_history": emotion_history,
        "total_entries": len(emotion_history)
    }


@router.post("/session/{session_id}/clear")
async def clear_session(session_id: str):
    """Clear a chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Keep session metadata but clear messages and history
    session_data = chat_sessions[session_id]
    session_data["messages"] = []
    session_data["emotion_history"] = []
    session_data["last_activity"] = datetime.now()
    
    return {
        "message": "Session cleared successfully",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session completely."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del chat_sessions[session_id]
    
    return {
        "message": "Session deleted successfully",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/sessions")
async def list_sessions(limit: int = 20, offset: int = 0):
    """List all chat sessions."""
    session_list = []
    
    for session_id, session_data in chat_sessions.items():
        session_list.append({
            "session_id": session_id,
            "created_at": session_data["created_at"],
            "message_count": len(session_data["messages"]),
            "last_activity": session_data["last_activity"],
            "status": "active"
        })
    
    # Sort by last activity (most recent first)
    session_list.sort(key=lambda x: x["last_activity"], reverse=True)
    
    # Apply pagination
    start_idx = offset
    end_idx = offset + limit
    paginated_sessions = session_list[start_idx:end_idx]
    
    return {
        "sessions": paginated_sessions,
        "total_count": len(session_list),
        "offset": offset,
        "limit": limit,
        "has_more": end_idx < len(session_list)
    }


@router.post("/stream")
async def stream_message(message: ChatMessage):
    """
    Stream a message response with real-time progress updates.
    
    Uses optimized streaming workflow with caching and performance monitoring.
    """
    # Validate input immediately - return 422 for empty messages
    if not message.text or not message.text.strip():
        raise HTTPException(
            status_code=422,
            detail="Message text cannot be empty"
        )
    
    if not message.session_id or not message.session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Session ID is required"
        )
    
    async def generate_stream():
        try:
            # Ensure session exists
            if message.session_id not in chat_sessions:
                chat_sessions[message.session_id] = {
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "messages": [],
                    "emotion_history": []
                }
            
            # Prepare input data
            input_data = {
                "user_message": message.text,
                "context": message.context or [],
                "user_preferences": message.user_preferences or {},
                "response_style": message.response_style,
                "analysis_depth": message.analysis_depth,
                "recent_content": [],
                "user_history": chat_sessions[message.session_id].get("emotion_history", [])
            }
            
            # Use the optimized streaming workflow
            logger.info(f"Starting streaming chat for session {message.session_id}")
            
            async for chunk in crew_manager.execute_workflow_stream(
                workflow_name=message.workflow_type,
                input_data=input_data,
                session_id=message.session_id
            ):
                # Convert StreamChunk to SSE format
                chunk_data = {
                    "type": chunk.type.value,
                    "timestamp": chunk.timestamp.isoformat(),
                    **(chunk.data or {})
                }
                
                # Ensure all datetime objects are serialized
                chunk_data = json.loads(json.dumps(chunk_data, default=str))
                
                yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Store final response data when complete
                if chunk.type == StreamChunkType.RESPONSE_END:
                    await _store_stream_session_data(
                        message.session_id,
                        message.text,
                        chunk.data,
                        message.workflow_type
                    )
            
            logger.info(f"Streaming completed for session {message.session_id}")
            
        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


async def _store_stream_session_data(
    session_id: str,
    user_text: str, 
    response_data: Dict[str, Any],
    workflow_type: str
):
    """Store streaming session data after response completion."""
    try:
        if session_id not in chat_sessions:
            return
            
        # Generate message IDs
        user_message_id = str(uuid4())
        assistant_message_id = str(uuid4())
        timestamp_now = datetime.now()
        
        # Store user message
        user_message_obj = {
            "id": user_message_id,
            "text": user_text,
            "type": "user",
            "timestamp": timestamp_now.isoformat()
        }
        
        # Store assistant response
        assistant_message_obj = {
            "id": assistant_message_id,
            "text": response_data.get("response_text", ""),
            "type": "assistant",
            "timestamp": timestamp_now.isoformat(),
            "emotion_analysis": response_data.get("emotion_analysis"),
            "workflow_used": workflow_type,
            "execution_time_ms": response_data.get("execution_time_ms", 0)
        }
        
        # Add to session
        chat_sessions[session_id]["messages"].extend([
            user_message_obj,
            assistant_message_obj
        ])
        
        # Store emotion analysis in history
        if response_data.get("emotion_analysis"):
            chat_sessions[session_id]["emotion_history"].append({
                "timestamp": timestamp_now.isoformat(),
                "analysis": response_data["emotion_analysis"]
            })
            
        # Update session activity
        chat_sessions[session_id]["last_activity"] = timestamp_now
        
        logger.debug(f"Session data stored for streaming response: {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to store streaming session data: {e}")


async def _update_session_analytics(session_id: str, emotion_analysis: Optional[Dict[str, Any]]):
    """Background task to update session analytics."""
    try:
        if not emotion_analysis:
            return
        
        # TODO: Implement session analytics
        # This could include:
        # - Emotion trend analysis
        # - User engagement metrics  
        # - Personalization improvements
        # - Content recommendation training data
        
        logger.debug(f"Session analytics updated for {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to update session analytics: {e}")


@router.get("/performance/stats")
async def get_performance_stats():
    """
    Get current performance statistics and metrics.
    
    Returns detailed performance data including cache usage, response times, etc.
    """
    try:
        stats = crew_manager.get_performance_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance statistics")


@router.post("/performance/optimize")
async def optimize_performance():
    """
    Run performance optimization tasks.
    
    Cleans cache, warms up agents, and applies other optimizations.
    """
    try:
        optimization_results = await crew_manager.optimize_performance()
        return {
            "success": True,
            "optimizations": optimization_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Performance optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Performance optimization failed")