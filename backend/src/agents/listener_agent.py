"""
Listener Agent for Duck Therapy System

Specialized agent for emotion analysis and psychological needs assessment.
Configured via YAML for maximum modularity.
"""
from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

from .base_agent import BaseAgent, BaseAgentInput, BaseAgentOutput
from ..models.emotion import EmotionAnalysis
from ..utils.config_loader import config_loader
from loguru import logger


class ListenerInput(BaseAgentInput):
    """Input model for Listener Agent."""
    
    text: str
    context: Optional[List[str]] = None
    analysis_depth: str = "standard"  # basic, standard, detailed


class ListenerAgent(BaseAgent):
    """Emotion analysis and psychological assessment agent."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize Listener Agent with YAML configuration.
        
        Args:
            config_override: Optional configuration overrides
        """
        super().__init__(
            agent_name="listener_agent",
            config_override=config_override
        )
        
        # Load emotion keywords and patterns
        self._load_emotion_patterns()
    
    def _load_emotion_patterns(self):
        """Load emotion detection patterns and keywords."""
        # Basic Chinese emotion keywords
        self.emotion_keywords = {
            "开心": ["开心", "高兴", "快乐", "愉快", "兴奋", "满足", "喜悦"],
            "悲伤": ["悲伤", "难过", "伤心", "沮丧", "失落", "痛苦"],
            "愤怒": ["愤怒", "生气", "火大", "气愤", "恼火", "暴躁"],
            "焦虑": ["焦虑", "担心", "紧张", "不安", "恐惧", "害怕"],
            "压力": ["压力", "疲惫", "累", "辛苦", "忙碌", "烦躁"],
            "孤独": ["孤独", "寂寞", "无聊", "空虚", "寂寥"],
            "平静": ["平静", "安静", "放松", "淡定", "宁静"],
            "感激": ["感谢", "感激", "谢谢", "感恩", "感动"],
            "困惑": ["困惑", "迷茫", "不懂", "疑惑", "纠结"]
        }
        
        # Sentiment indicators
        self.positive_indicators = ["好", "棒", "赞", "不错", "满意", "成功", "顺利"]
        self.negative_indicators = ["不好", "糟糕", "失败", "问题", "麻烦", "困难"]
    
    async def process(self, input_data: ListenerInput) -> BaseAgentOutput:
        """
        Process emotion analysis task.
        
        Args:
            input_data: Input containing text to analyze
            
        Returns:
            Emotion analysis results
        """
        try:
            # Get task template from YAML
            task_template = config_loader.get_task_template("emotion_analysis")
            if not task_template:
                raise ValueError("Emotion analysis task template not found")
            
            # Prepare context for LLM
            context = ""
            if input_data.context:
                context = "最近对话上下文：\n" + "\n".join(input_data.context[-3:])
            
            # Format task description with actual data
            task_description = task_template["description"].format(
                user_message=input_data.text,
                context=context or "无"
            )
            
            # Execute LLM analysis
            llm_result = await self._execute_task(
                task_description=task_description,
                expected_output=task_template["expected_output"],
                context=context
            )
            
            # Parse LLM result and combine with rule-based analysis
            emotion_analysis = await self._parse_and_enhance_analysis(
                llm_result, input_data.text, input_data.analysis_depth
            )
            
            return BaseAgentOutput(
                success=True,
                agent_name=self.name,
                data=emotion_analysis.dict()
            )
            
        except Exception as e:
            logger.error(f"Listener agent processing failed: {e}")
            
            # Fallback to rule-based analysis
            try:
                fallback_analysis = self._rule_based_analysis(input_data.text)
                return BaseAgentOutput(
                    success=True,
                    agent_name=self.name,
                    data=fallback_analysis.dict()
                )
            except Exception as fallback_error:
                return BaseAgentOutput(
                    success=False,
                    agent_name=self.name,
                    error=f"Both LLM and fallback analysis failed: {str(e)}, {str(fallback_error)}"
                )
    
    async def _parse_and_enhance_analysis(
        self, 
        llm_result: str, 
        original_text: str,
        analysis_depth: str
    ) -> EmotionAnalysis:
        """
        Parse LLM result and enhance with rule-based analysis.
        
        Args:
            llm_result: Raw LLM response
            original_text: Original user text
            analysis_depth: Analysis depth level
            
        Returns:
            Enhanced emotion analysis
        """
        try:
            # Try to parse JSON from LLM result
            # Clean up the result to extract JSON
            json_match = re.search(r'\{.*\}', llm_result, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # Fallback parsing
                parsed_data = self._extract_from_text(llm_result)
        except (json.JSONDecodeError, AttributeError):
            # If JSON parsing fails, use rule-based analysis
            logger.warning("LLM result parsing failed, using rule-based analysis")
            return self._rule_based_analysis(original_text)
        
        # Enhance with rule-based analysis
        rule_analysis = self._rule_based_analysis(original_text)
        
        # Normalize sentiment value
        sentiment_raw = parsed_data.get("sentiment", rule_analysis.sentiment)
        sentiment = self._normalize_sentiment(sentiment_raw)
        
        # Combine results
        emotion_analysis = EmotionAnalysis(
            sentiment=sentiment,
            intensity=max(
                parsed_data.get("intensity", 0.5),
                rule_analysis.intensity
            ),
            confidence=parsed_data.get("confidence", 0.8),
            primary_emotions=list(set(
                parsed_data.get("primary_emotions", []) + 
                rule_analysis.primary_emotions
            )),
            secondary_emotions=parsed_data.get("secondary_emotions", []),
            keywords=list(set(
                parsed_data.get("keywords", []) + 
                rule_analysis.keywords
            )),
            topics=parsed_data.get("topics", []),
            psychological_needs=parsed_data.get("psychological_needs", []),
            urgency_level=max(
                parsed_data.get("urgency_level", 1),
                rule_analysis.urgency_level
            ),
            support_type=parsed_data.get("support_type"),
            processing_notes=f"Combined LLM and rule-based analysis (depth: {analysis_depth})",
            analyzed_at=datetime.now()
        )
        
        return emotion_analysis
    
    def _normalize_sentiment(self, sentiment_raw: str) -> str:
        """
        Normalize sentiment value to match Pydantic model requirements.
        
        Args:
            sentiment_raw: Raw sentiment value from LLM
            
        Returns:
            Normalized sentiment value
        """
        if not sentiment_raw:
            return "neutral"
        
        sentiment_str = str(sentiment_raw).lower().strip()
        
        # Handle various positive indicators
        if sentiment_str in ["+", "正面", "积极", "positive", "pos", "good"]:
            return "positive"
        
        # Handle various negative indicators  
        elif sentiment_str in ["-", "负面", "消极", "negative", "neg", "bad"]:
            return "negative"
            
        # Handle neutral indicators
        elif sentiment_str in ["0", "中性", "neutral", "neu", "平静"]:
            return "neutral"
            
        # Default to neutral for unknown formats
        else:
            logger.warning(f"Unknown sentiment format: {sentiment_raw}, defaulting to neutral")
            return "neutral"
    
    def _rule_based_analysis(self, text: str) -> EmotionAnalysis:
        """
        Fallback rule-based emotion analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Basic emotion analysis
        """
        text_lower = text.lower()
        
        # Detect emotions based on keywords
        detected_emotions = []
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                detected_emotions.append(emotion)
                emotion_scores[emotion] = score
        
        # Determine sentiment
        positive_score = sum(1 for indicator in self.positive_indicators if indicator in text_lower)
        negative_score = sum(1 for indicator in self.negative_indicators if indicator in text_lower)
        
        if positive_score > negative_score:
            sentiment = "positive"
        elif negative_score > positive_score:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Calculate intensity based on punctuation and emotional words
        intensity = 0.5
        if "!" in text or "！" in text:
            intensity += 0.2
        if "?" in text or "？" in text:
            intensity += 0.1
        if len(detected_emotions) > 2:
            intensity += 0.2
        
        intensity = min(intensity, 1.0)
        
        # Determine urgency level
        urgency_level = 1
        if "帮助" in text_lower or "救" in text_lower:
            urgency_level = 4
        elif any(word in text_lower for word in ["痛苦", "绝望", "崩溃"]):
            urgency_level = 3
        elif sentiment == "negative" and intensity > 0.7:
            urgency_level = 2
        
        # Extract simple keywords
        keywords = []
        for emotion in detected_emotions:
            keywords.extend([kw for kw in self.emotion_keywords[emotion] if kw in text_lower])
        
        return EmotionAnalysis(
            sentiment=sentiment,
            intensity=intensity,
            confidence=0.6,  # Lower confidence for rule-based
            primary_emotions=detected_emotions[:2] if detected_emotions else ["平静"],
            secondary_emotions=detected_emotions[2:] if len(detected_emotions) > 2 else [],
            keywords=list(set(keywords)),
            topics=["日常对话"],
            psychological_needs=self._assess_needs(detected_emotions, sentiment),
            urgency_level=urgency_level,
            support_type=self._determine_support_type(sentiment, detected_emotions),
            processing_notes="Rule-based analysis (fallback)",
            analyzed_at=datetime.now()
        )
    
    def _assess_needs(self, emotions: List[str], sentiment: str) -> List[str]:
        """Assess psychological needs based on emotions."""
        needs = []
        
        if "悲伤" in emotions:
            needs.extend(["安慰", "倾听"])
        if "焦虑" in emotions:
            needs.extend(["安抚", "指导"])
        if "愤怒" in emotions:
            needs.extend(["理解", "发泄"])
        if "孤独" in emotions:
            needs.extend(["陪伴", "连接"])
        if "压力" in emotions:
            needs.extend(["放松", "支持"])
        
        if sentiment == "positive":
            needs.extend(["分享", "庆祝"])
        elif sentiment == "negative" and not needs:
            needs.extend(["支持", "理解"])
        
        return list(set(needs))
    
    def _determine_support_type(self, sentiment: str, emotions: List[str]) -> str:
        """Determine appropriate support type."""
        if sentiment == "positive":
            return "celebration"
        elif "焦虑" in emotions:
            return "anxiety_relief"
        elif "悲伤" in emotions:
            return "comfort"
        elif "愤怒" in emotions:
            return "anger_management"
        elif "压力" in emotions:
            return "stress_relief"
        else:
            return "general_support"
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from unstructured LLM text response."""
        # Basic text parsing fallback
        result = {
            "sentiment": "neutral",
            "intensity": 0.5,
            "confidence": 0.5,
            "primary_emotions": [],
            "keywords": [],
            "topics": [],
            "psychological_needs": [],
            "urgency_level": 1
        }
        
        # Simple pattern matching
        if "正面" in text or "积极" in text or "positive" in text.lower() or "+" in text:
            result["sentiment"] = "positive"
        elif "负面" in text or "消极" in text or "negative" in text.lower() or "-" in text:
            result["sentiment"] = "negative"
        
        # Extract emotions mentioned in text
        for emotion in self.emotion_keywords.keys():
            if emotion in text:
                result["primary_emotions"].append(emotion)
        
        return result