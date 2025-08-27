"""
Duck Style Agent for Duck Therapy System

Specialized agent for maintaining duck personality consistency and therapeutic tone.
Ensures all responses align with the warm, healing duck character IP.
"""
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

from .base_agent import BaseAgent, BaseAgentInput, BaseAgentOutput
from ..utils.config_loader import config_loader
from loguru import logger


class DuckStyleInput(BaseAgentInput):
    """Input model for Duck Style Agent."""
    
    user_message: str
    emotion_analysis: Dict[str, Any]
    content_recommendations: Optional[Dict[str, Any]] = None
    therapy_suggestions: Optional[Dict[str, Any]] = None
    response_style: str = "standard"  # standard, detailed, brief


class DuckStyleAgent(BaseAgent):
    """Agent for maintaining duck personality and therapeutic tone."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize Duck Style Agent with YAML configuration.
        
        Args:
            config_override: Optional configuration overrides
        """
        super().__init__(
            agent_name="duck_style_agent",
            config_override=config_override
        )
        
        # Load personality guidelines from config
        self._load_personality_guidelines()
        
        # Load safety patterns
        self._load_safety_patterns()
    
    def _load_personality_guidelines(self):
        """Load duck personality guidelines from configuration."""
        # 从 YAML 配置加载个性化设置，不再硬编码
        personality_traits = self.config.get("personality_traits", {})
        
        self.tone_characteristics = personality_traits.get("语气特征", [])
        self.expression_style = personality_traits.get("表达方式", [])
        self.avoid_content = personality_traits.get("避免内容", [])
        self.special_elements = personality_traits.get("特色元素", [])
        
        # 从 YAML 配置加载鸭鸭专用表达词汇
        self.duck_expressions = self.config.get("duck_expressions", {})
    
    def _load_safety_patterns(self):
        """Load content safety patterns from configuration."""
        # 从 YAML 配置加载安全检查模式，不再硬编码
        safety_patterns = self.config.get("safety_patterns", {})
        
        self.inappropriate_patterns = safety_patterns.get("inappropriate_patterns", [])
        self.medical_patterns = safety_patterns.get("medical_patterns", [])
        self.safety_responses = safety_patterns.get("safety_responses", {})
    
    async def process(self, input_data: DuckStyleInput) -> BaseAgentOutput:
        """
        Process duck response generation task.
        
        Args:
            input_data: Input containing user message and analysis data
            
        Returns:
            Duck-style response with personality consistency
        """
        try:
            # Safety check first
            safety_check = self._check_content_safety(input_data.user_message)
            if safety_check["has_issues"]:
                return BaseAgentOutput(
                    success=True,
                    agent_name=self.name,
                    data={
                        "text": safety_check["response"],
                        "safety_triggered": True,
                        "safety_reason": safety_check["reason"]
                    }
                )
            
            logger.debug(f"DuckStyleAgent: Processing message for session {input_data.session_id}")
            
            # Get task template from YAML
            task_template = config_loader.get_task_template("duck_response_generation")
            if not task_template:
                raise ValueError("Duck response generation task template not found")
            
            logger.debug("DuckStyleAgent: Task template loaded successfully")
            
            # Prepare context for LLM
            context_data = self._prepare_context(input_data)
            logger.debug(f"DuckStyleAgent: Context prepared: {list(context_data.keys())}")
            
            # Format task description with actual data
            task_description = task_template["description"].format(**context_data)
            logger.debug("DuckStyleAgent: Task description formatted successfully")
            
            # Execute LLM generation
            logger.debug("DuckStyleAgent: Starting LLM execution")
            llm_result = await self._execute_task(
                task_description=task_description,
                expected_output=task_template["expected_output"],
                context=self._build_personality_context()
            )
            logger.debug(f"DuckStyleAgent: LLM result received: {llm_result[:100] if llm_result else 'None'}...")
            
            # Enhance and validate the response
            logger.debug("DuckStyleAgent: Starting response enhancement")
            duck_response = self._enhance_duck_response(
                llm_result, input_data.emotion_analysis, input_data.response_style
            )
            logger.debug(f"DuckStyleAgent: Enhanced response: {duck_response[:100] if duck_response else 'None'}...")
            
            return BaseAgentOutput(
                success=True,
                agent_name=self.name,
                data={
                    "text": duck_response,
                    "style_applied": True,
                    "personality_consistent": True
                }
            )
            
        except Exception as e:
            logger.error(f"Duck style agent processing failed at step: {e}", exc_info=True)
            
            # Fallback to template-based response
            try:
                fallback_response = self._generate_fallback_response(input_data)
                return BaseAgentOutput(
                    success=True,
                    agent_name=self.name,
                    data={
                        "text": fallback_response,
                        "fallback_used": True
                    }
                )
            except Exception as fallback_error:
                return BaseAgentOutput(
                    success=False,
                    agent_name=self.name,
                    error=f"Both LLM and fallback generation failed: {str(e)}, {str(fallback_error)}"
                )
    
    def _check_content_safety(self, text: str) -> Dict[str, Any]:
        """
        Check content for safety issues.
        
        Args:
            text: Text to check
            
        Returns:
            Safety check results
        """
        text_lower = text.lower()
        
        # Check for crisis/inappropriate content
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, text_lower):
                return {
                    "has_issues": True,
                    "reason": "crisis_content",
                    "response": self.safety_responses["crisis"]
                }
        
        # Check for medical content
        for pattern in self.medical_patterns:
            if re.search(pattern, text_lower):
                return {
                    "has_issues": True,
                    "reason": "medical_content", 
                    "response": self.safety_responses["medical"]
                }
        
        return {"has_issues": False}
    
    def _prepare_context(self, input_data: DuckStyleInput) -> Dict[str, str]:
        """Prepare context data for task template."""
        return {
            "user_message": input_data.user_message,
            "emotion_analysis": str(input_data.emotion_analysis),
            "content_recommendations": str(input_data.content_recommendations or "无"),
            "therapy_suggestions": str(input_data.therapy_suggestions or "无")
        }
    
    def _build_personality_context(self) -> str:
        """Build personality context for LLM."""
        context_parts = [
            "你是心理鸭鸭，需要保持以下特征：",
            f"语气特征：{', '.join(self.tone_characteristics)}",
            f"表达方式：{', '.join(self.expression_style)}",
            f"避免：{', '.join(self.avoid_content)}",
            f"特色元素：{', '.join(self.special_elements)}",
            "",
            "回复要求：",
            "1. 像朋友一样自然对话，绝对不要提及任何分析过程",
            "2. 使用温暖、治愈的语气",
            "3. 适当使用'鸭鸭'自称",
            "4. 回复要简洁但有温度",
            "5. 以鼓励和支持为主",
            "6. 结尾要温暖自然",
            "",
            "严格禁止使用的词语：",
            "- '根据你的情绪分析'",
            "- '从你的话中分析'",
            "- '情绪分析显示'",
            "- '分析结果'等任何分析性词汇",
            "",
            "记住：你是朋友，不是分析师！"
        ]
        
        return "\n".join(context_parts)
    
    def _enhance_duck_response(
        self, 
        llm_response: str, 
        emotion_analysis: Dict[str, Any],
        response_style: str
    ) -> str:
        """
        Enhance LLM response with duck personality elements.
        
        Args:
            llm_response: Raw LLM response
            emotion_analysis: User emotion analysis
            response_style: Desired response style
            
        Returns:
            Enhanced duck-style response
        """
        # Clean up the response
        response = llm_response.strip()
        
        # Add duck personality elements if missing
        response = self._add_duck_elements(response, emotion_analysis)
        
        # Adjust response length based on style
        if response_style == "brief":
            response = self._make_response_brief(response)
        elif response_style == "detailed":
            response = self._add_detailed_elements(response, emotion_analysis)
        
        # Ensure warm ending
        response = self._ensure_warm_ending(response)
        
        # Final validation and cleanup
        response = self._validate_and_cleanup(response)
        
        return response
    
    def _add_duck_elements(self, response: str, emotion_analysis: Dict[str, Any]) -> str:
        """Add duck personality elements to response."""
        sentiment = emotion_analysis.get("sentiment", "neutral")
        
        # Add empathy expressions
        if sentiment == "negative":
            if not any(phrase in response for phrase in self.duck_expressions["empathy"]):
                empathy = self.duck_expressions["empathy"][0]
                response = f"{empathy}。{response}"
        
        # Add comfort expressions
        if "悲伤" in str(emotion_analysis.get("primary_emotions", [])):
            if not any(phrase in response for phrase in self.duck_expressions["comfort"]):
                comfort = self.duck_expressions["comfort"][1]
                response = f"{response} {comfort}。"
        
        # Ensure duck self-reference
        if "鸭鸭" not in response:
            # Add duck reference naturally
            response = response.replace("我", "鸭鸭", 1)
        
        return response
    
    def _make_response_brief(self, response: str) -> str:
        """Make response more concise."""
        sentences = response.split("。")
        if len(sentences) > 2:
            # Keep first sentence and a warm ending
            brief_response = sentences[0] + "。" + sentences[-1] if sentences[-1] else ""
            return brief_response
        return response
    
    def _add_detailed_elements(self, response: str, emotion_analysis: Dict[str, Any]) -> str:
        """Add more detailed supportive elements."""
        # Add specific emotion acknowledgment
        emotions = emotion_analysis.get("primary_emotions", [])
        if emotions and len(emotions) > 0:
            emotion_ack = f"鸭鸭能感受到你的{emotions[0]}，"
            if not emotion_ack[:5] in response:
                response = emotion_ack + response
        
        return response
    
    def _ensure_warm_ending(self, response: str) -> str:
        """Ensure response has a warm, supportive ending."""
        warm_endings = self.duck_expressions["endings"]
        
        # Check if response already has a warm ending
        has_warm_ending = any(ending in response for ending in warm_endings)
        
        if not has_warm_ending:
            # Add appropriate ending based on response length
            if len(response) > 50:
                ending = warm_endings[0]  # "鸭鸭会一直陪着你哦～"
            else:
                ending = warm_endings[2]  # "鸭鸭在这里"
            
            response = f"{response} {ending}"
        
        return response
    
    def _validate_and_cleanup(self, response: str) -> str:
        """Final validation and cleanup of response using config-driven rules."""
        # Remove extra spaces
        response = re.sub(r'\s+', ' ', response).strip()
        
        # 从配置获取需要移除的分析性短语
        enhancement_config = self.config.get("response_enhancement", {})
        analytical_phrases = enhancement_config.get("analytical_phrases_to_remove", [])
        
        # Remove technical/analytical phrases using config
        for phrase in analytical_phrases:
            pattern = phrase + r"[，。]?"
            response = re.sub(pattern, "", response, flags=re.IGNORECASE)
        
        # Clean up any resulting double spaces or awkward punctuation
        response = re.sub(r'\s+', ' ', response).strip()
        response = re.sub(r'[，。]{2,}', '。', response)
        response = re.sub(r'^[，。]+', '', response)
        
        # Ensure proper punctuation using config
        required_endings = enhancement_config.get("required_ending_chars", ["。"])
        if not response.endswith(tuple(required_endings)):
            response += "。"
        
        # Limit length using config
        max_length = enhancement_config.get("max_response_length", 200)
        if len(response) > max_length:
            sentences = response.split("。")
            response = "。".join(sentences[:2]) + "。"
        
        return response
    
    def _generate_fallback_response(self, input_data: DuckStyleInput) -> str:
        """
        Generate fallback response using templates.
        
        Args:
            input_data: Input data for response generation
            
        Returns:
            Template-based duck response
        """
        emotion_analysis = input_data.emotion_analysis
        sentiment = emotion_analysis.get("sentiment", "neutral")
        emotions = emotion_analysis.get("primary_emotions", [])
        
        # Select response template based on emotion
        if sentiment == "positive":
            if "开心" in emotions:
                base_response = "鸭鸭看到你很开心，这真是太好了！"
            elif "感激" in emotions:
                base_response = "鸭鸭感受到了你的感谢，这让鸭鸭也很温暖。"
            else:
                base_response = "听起来你心情不错呢，鸭鸭也为你高兴。"
        
        elif sentiment == "negative":
            if "悲伤" in emotions:
                base_response = "鸭鸭能感受到你的难过，想给你一个温暖的拥抱。"
            elif "焦虑" in emotions:
                base_response = "感觉到你有些紧张，鸭鸭陪着你，慢慢来就好。"
            elif "愤怒" in emotions:
                base_response = "鸭鸭理解你的情绪，有时候确实会让人生气。"
            else:
                base_response = "鸭鸭感受到了你的情绪，想陪着你聊一聊。"
        
        else:  # neutral
            base_response = "谢谢你和鸭鸭分享，鸭鸭很认真在听。"
        
        # Add warm ending
        ending = self.duck_expressions["endings"][0]
        return f"{base_response} {ending}"
    
    def get_personality_info(self) -> Dict[str, Any]:
        """Get current personality configuration."""
        return {
            "tone_characteristics": self.tone_characteristics,
            "expression_style": self.expression_style,
            "avoid_content": self.avoid_content,
            "special_elements": self.special_elements,
            "duck_expressions": self.duck_expressions
        }