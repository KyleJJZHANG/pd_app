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
        """Load emotion detection patterns and keywords from configuration."""
        # 从 YAML 配置加载情绪分析规则，不再硬编码
        emotion_config = self.config.get("emotion_analysis", {})
        
        self.emotion_keywords = emotion_config.get("emotion_keywords", {})
        
        # 加载情绪极性指示词
        sentiment_indicators = emotion_config.get("sentiment_indicators", {})
        self.positive_indicators = sentiment_indicators.get("positive", [])
        self.negative_indicators = sentiment_indicators.get("negative", [])
        
        # 加载其他配置
        self.intensity_rules = emotion_config.get("intensity_rules", {})
        self.urgency_assessment = emotion_config.get("urgency_assessment", {})
        self.needs_mapping = emotion_config.get("psychological_needs_mapping", {})
        self.support_mapping = emotion_config.get("support_type_mapping", {})
        self.fallback_config = emotion_config.get("fallback_analysis", {})
    
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
        
        # Calculate intensity using config-driven rules
        intensity = self.intensity_rules.get("default_intensity", 0.5)
        
        # Apply punctuation boost from config
        punctuation_boost = self.intensity_rules.get("punctuation_boost", {})
        for char, boost in punctuation_boost.items():
            if char in text:
                intensity += boost
                
        # Apply multiple emotions boost from config
        if len(detected_emotions) > 2:
            intensity += self.intensity_rules.get("multiple_emotions_boost", 0.2)
        
        # Apply max intensity limit from config
        max_intensity = self.intensity_rules.get("max_intensity", 1.0)
        intensity = min(intensity, max_intensity)
        
        # Determine urgency level using config-driven rules
        urgency_levels = self.urgency_assessment.get("urgency_levels", {})
        urgency_level = urgency_levels.get("normal", 1)
        
        # Check for crisis keywords from config
        crisis_keywords = self.urgency_assessment.get("crisis_keywords", [])
        if any(keyword in text_lower for keyword in crisis_keywords):
            urgency_level = urgency_levels.get("crisis", 4)
        elif any(word in text_lower for word in self.urgency_assessment.get("high_urgency_keywords", [])):
            urgency_level = urgency_levels.get("high", 3)
        elif sentiment == "negative" and intensity > 0.7:
            urgency_level = urgency_levels.get("medium", 2)
        
        # Extract simple keywords
        keywords = []
        for emotion in detected_emotions:
            keywords.extend([kw for kw in self.emotion_keywords[emotion] if kw in text_lower])
        
        return EmotionAnalysis(
            sentiment=sentiment,
            intensity=intensity,
            confidence=self.fallback_config.get("confidence_level", 0.6),
            primary_emotions=detected_emotions[:2] if detected_emotions else self.fallback_config.get("default_emotions", ["平静"]),
            secondary_emotions=detected_emotions[2:] if len(detected_emotions) > 2 else [],
            keywords=list(set(keywords)),
            topics=self.fallback_config.get("default_topics", ["日常对话"]),
            psychological_needs=self._assess_needs(detected_emotions, sentiment),
            urgency_level=urgency_level,
            support_type=self._determine_support_type(sentiment, detected_emotions),
            processing_notes=self.fallback_config.get("processing_note", "Rule-based analysis (fallback)"),
            analyzed_at=datetime.now()
        )
    
    def _assess_needs(self, emotions: List[str], sentiment: str) -> List[str]:
        """Assess psychological needs based on emotions using config-driven mapping."""
        needs = []
        
        # Use config-driven emotion-to-needs mapping
        for emotion in emotions:
            if emotion in self.needs_mapping:
                needs.extend(self.needs_mapping[emotion])
        
        # Apply sentiment-based general needs from config
        if sentiment == "positive" and "positive_general" in self.needs_mapping:
            needs.extend(self.needs_mapping["positive_general"])
        elif sentiment == "negative" and not needs and "negative_general" in self.needs_mapping:
            needs.extend(self.needs_mapping["negative_general"])
        
        return list(set(needs))
    
    def _determine_support_type(self, sentiment: str, emotions: List[str]) -> str:
        """Determine appropriate support type using config-driven mapping."""
        # Check specific emotions first using config mapping
        for emotion in emotions:
            if emotion in self.support_mapping:
                return self.support_mapping[emotion]
        
        # Fall back to sentiment-based mapping from config
        if sentiment in self.support_mapping:
            return self.support_mapping[sentiment]
            
        # Use default from config
        return self.support_mapping.get("default", "general_support")
    
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