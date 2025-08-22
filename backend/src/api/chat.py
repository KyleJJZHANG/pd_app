"""
Chat API for Duck Therapy System

Handles therapeutic chat interactions using multi-agent workflows.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
from uuid import uuid4

from ..services.crew_manager import crew_manager, WorkflowStatus
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
    Stream a message response (for real-time chat experience).
    
    This endpoint provides server-sent events for streaming responses.
    """
    async def generate_stream():
        try:
            # Send initial acknowledgment
            yield f"data: {json.dumps({'type': 'start', 'message': 'Processing message...'})}\n\n"
            
            # Prepare input data
            input_data = {
                "user_message": message.text,
                "context": message.context or [],
                "user_preferences": message.user_preferences or {},
                "response_style": message.response_style,
                "analysis_depth": message.analysis_depth
            }
            
            # Execute workflow
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Analyzing emotions...'})}\n\n"
            
            workflow_result = await crew_manager.execute_workflow(
                workflow_name=message.workflow_type,
                input_data=input_data,
                session_id=message.session_id
            )
            
            if workflow_result.status == WorkflowStatus.FAILED:
                yield f"data: {json.dumps({'type': 'error', 'message': workflow_result.error})}\n\n"
                return
            
            # Send progress updates
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Generating response...'})}\n\n"
            
            # Send final response
            final_output = workflow_result.final_output or {}
            response_data = {
                "type": "response",
                "text": final_output.get("response_text", "鸭鸭暂时无法回复，请稍后再试哦～"),
                "emotion_analysis": final_output.get("emotion_analysis"),
                "execution_time_ms": workflow_result.total_execution_time_ms,
                "success_rate": workflow_result.success_rate
            }
            
            yield f"data: {json.dumps(response_data)}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )


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