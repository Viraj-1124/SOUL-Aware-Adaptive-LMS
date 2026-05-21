import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
import json
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Service for generating personalized content via LLM"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.openai_api_key)
        
        if self.use_openai:
            try:
                import openai
                openai.api_key = self.openai_api_key
            except ImportError:
                logger.warning("OpenAI library not installed")
                self.use_openai = False
    
    @staticmethod
    def _create_prompt_for_remedial_content(
        student_name: str,
        skill_gap: str,
        difficulty_level: str,
        student_context: Dict,
        fatigue_level: Optional[str] = None
    ) -> str:
        """Create a well-structured prompt for LLM"""
        
        fatigue_note = ""
        if fatigue_level:
            fatigue_note = f"""
The student is experiencing {fatigue_level} moral fatigue. Please ensure the content:
- Is concise and not overwhelming
- Includes breaks and mini-reflections
- Has motivational elements
"""
        
        prompt = f"""Create personalized educational content for a student.

Student Profile:
- Name: {student_name}
- Learning Style: {student_context.get('learning_style', 'Visual and practical')}
- Current Level: {difficulty_level}
- Recent Topics: {student_context.get('recent_topics', 'Not specified')}
- Motivation Level: {student_context.get('motivation_level', 'Medium')}

Skill Gap to Address:
- Gap: {skill_gap}
- Recommended Difficulty: {difficulty_level}

Content Requirements:
1. Create learning material that bridges this skill gap
2. Use clear, simple language appropriate for the student's level
3. Include 2-3 real-world examples
4. Add 1 simple interactive activity or self-check question
5. Make it engaging but not overwhelming (300-500 words){fatigue_note}

Format the response as:
TITLE: [Brief, engaging title]

OVERVIEW: [2-3 sentences explaining what they'll learn]

CONTENT: [Main learning material with examples]

KEY TAKEAWAYS:
- [Point 1]
- [Point 2]
- [Point 3]

SELF-CHECK: [One question to verify understanding]

NEXT STEPS: [Brief suggestion for follow-up learning]
"""
        return prompt
    
    @staticmethod
    def _create_reflection_prompt(
        student_name: str,
        context: str,
        recent_performance: Dict
    ) -> str:
        """Create a reflection prompt for journaling"""
        
        performance_context = ""
        if recent_performance:
            performance_context = f"""
Based on your recent learning:
- Topics covered: {recent_performance.get('topics', 'N/A')}
- Performance: {recent_performance.get('score', 'N/A')}%
- Engagement level: {recent_performance.get('engagement', 'N/A')}
"""
        
        prompt = f"""Create a personalized reflection prompt for a student.

Student: {student_name}
Context: {context}
{performance_context}

Create a single reflective question that:
1. Is open-ended and encourages deep thinking
2. Connects to their learning journey
3. Helps them identify growth areas
4. Is appropriate for {context} reflection

The prompt should be 1-2 sentences, thoughtful, and actionable.

Reflection Prompt:
"""
        return prompt
    
    def generate_remedial_content(
        self,
        student_name: str,
        skill_gap: str,
        difficulty_level: str,
        student_context: Dict,
        fatigue_level: Optional[str] = None,
        fallback_content: Optional[str] = None
    ) -> str:
        """Generate personalized remedial content"""
        
        if not self.use_openai:
            return fallback_content or self._generate_fallback_content(
                skill_gap, difficulty_level, student_context
            )
        
        try:
            import openai
            
            prompt = self._create_prompt_for_remedial_content(
                student_name, skill_gap, difficulty_level, student_context, fatigue_level
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator who designs personalized learning materials."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated remedial content for {student_name}: {skill_gap}")
            return content
        
        except Exception as e:
            logger.error(f"Error generating content via OpenAI: {e}")
            return fallback_content or self._generate_fallback_content(
                skill_gap, difficulty_level, student_context
            )
    
    def generate_reflection_prompt(
        self,
        student_name: str,
        context: str,
        recent_performance: Dict,
        fallback_prompt: Optional[str] = None
    ) -> str:
        """Generate personalized reflection prompt"""
        
        if not self.use_openai:
            return fallback_prompt or self._generate_fallback_reflection_prompt(context)
        
        try:
            import openai
            
            prompt = self._create_reflection_prompt(
                student_name, context, recent_performance
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in reflective learning and pedagogical prompting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            reflection_prompt = response.choices[0].message.content
            logger.info(f"Generated reflection prompt for {student_name}")
            return reflection_prompt
        
        except Exception as e:
            logger.error(f"Error generating reflection prompt: {e}")
            return fallback_prompt or self._generate_fallback_reflection_prompt(context)
    
    @staticmethod
    def _generate_fallback_content(
        skill_gap: str,
        difficulty_level: str,
        student_context: Dict
    ) -> str:
        """Generate basic fallback content if LLM fails"""
        
        templates = {
            "BEGINNER": f"""
TITLE: Introduction to {skill_gap}

OVERVIEW: 
Learn the basics of {skill_gap} through simple, practical examples.

CONTENT:
{skill_gap} is a fundamental skill in your current subject. Here are the key concepts:

1. **Core Concept**: {skill_gap} involves understanding how different elements work together.

2. **Real-World Example**: Think of {skill_gap} like building blocks - each piece is important.

3. **Practice**: Try applying this concept to something you're already familiar with.

KEY TAKEAWAYS:
- {skill_gap} builds on foundational knowledge
- Practice makes mastery
- Real-world applications help learning

SELF-CHECK: Can you explain {skill_gap} to a friend in your own words?

NEXT STEPS: Review these concepts and try some practice problems.
""",
            "INTERMEDIATE": f"""
TITLE: Mastering {skill_gap}

OVERVIEW:
Deepen your understanding of {skill_gap} with intermediate concepts and applications.

CONTENT:
At this level, you'll explore more complex applications of {skill_gap}.

1. **Advanced Concept**: {skill_gap} can be applied in multiple contexts.

2. **Real-World Example**: Consider how professionals use {skill_gap} to solve problems.

3. **Synthesis**: Combine {skill_gap} with other skills you've learned.

KEY TAKEAWAYS:
- Multiple approaches to {skill_gap} exist
- Context matters when applying {skill_gap}
- Continuous practice refines your skills

SELF-CHECK: How would you explain {skill_gap} to someone at your current level?

NEXT STEPS: Take on more complex problems to master {skill_gap}.
""",
            "ADVANCED": f"""
TITLE: Advanced Applications of {skill_gap}

OVERVIEW:
Explore advanced applications and critical thinking around {skill_gap}.

CONTENT:
At the advanced level, {skill_gap} involves sophisticated problem-solving.

1. **Complex Analysis**: {skill_gap} can be analyzed from multiple perspectives.

2. **Real-World Example**: Experts use {skill_gap} to drive innovation and problem-solving.

3. **Critical Thinking**: Consider edge cases and limitations of {skill_gap}.

KEY TAKEAWAYS:
- {skill_gap} has nuances and complexities
- Real-world application requires judgment
- Continuous learning is essential

SELF-CHECK: Can you identify when and why {skill_gap} is most effective?

NEXT STEPS: Explore research and expert perspectives on {skill_gap}.
"""
        }
        
        return templates.get(difficulty_level, templates["INTERMEDIATE"])
    
    @staticmethod
    def _generate_fallback_reflection_prompt(context: str) -> str:
        """Generate basic fallback reflection prompt"""
        
        prompts = {
            "SKILL_GAP": "How did you approach learning this new skill? What strategies worked best for you?",
            "FATIGUE": "How are you feeling about your learning journey right now? What would help you feel more energized?",
            "MOTIVATION": "What aspect of your learning is most meaningful to you? How can you reconnect with that?",
            "PERFORMANCE": "What helped you succeed in this task? How can you apply those strategies to future challenges?",
            "GENERAL": "Reflect on your learning today. What was the most interesting thing you learned?"
        }
        
        return prompts.get(context, prompts["GENERAL"])


# Global instance
_content_service = None


def get_content_generation_service() -> ContentGenerationService:
    """Get or create global content generation service"""
    global _content_service
    if _content_service is None:
        _content_service = ContentGenerationService()
    return _content_service


def generate_and_save_remedial_module(
    db: Session,
    student_id: int,
    course_id: int,
    skill_gap: str,
    difficulty_level: str,
    student_context: Dict,
    fatigue_level: Optional[str] = None
):
    """Generate and save a remedial module to database"""
    from app.models.alert import RemediationModule
    
    try:
        service = get_content_generation_service()
        
        # Get student name
        from app.models.user import User
        student = db.query(User).filter(User.id == student_id).first()
        student_name = student.email.split("@")[0] if student else "Student"
        
        # Generate content
        content = service.generate_remedial_content(
            student_name, skill_gap, difficulty_level, student_context, fatigue_level
        )
        
        # Extract title from generated content
        title = f"Learn {skill_gap}"
        if "TITLE:" in content:
            title = content.split("TITLE:")[1].split("\n")[0].strip()
        
        # Create module
        module = RemediationModule(
            student_id=student_id,
            course_id=course_id,
            title=title,
            description=f"Personalized remedial content for {skill_gap}",
            skill_gap=skill_gap,
            difficulty_level=difficulty_level,
            content=content,
            content_type="TEXT",
            generated_by="LLM_OPENAI" if service.use_openai else "RULE_BASED",
            assigned_at=datetime.utcnow()
        )
        
        db.add(module)
        db.commit()
        db.refresh(module)
        
        logger.info(f"Created remedial module {module.id} for student {student_id}")
        return module
    
    except Exception as e:
        logger.error(f"Error generating and saving remedial module: {e}")
        return None
