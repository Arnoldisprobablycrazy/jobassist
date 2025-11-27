"""
Enhanced Resume Analyzer using LlamaIndex and AI.
"""
import os
from typing import Dict, List, Any, Optional
from llama_index.core import Document
from ai_services.llama_service import get_ai_service
import logging

logger = logging.getLogger(__name__)

def _safe_get_response(response_obj) -> str:
    """Safely extract text from LlamaIndex response objects."""
    if response_obj is None:
        return ""
    
    # Try different attributes that might contain the response text
    for attr in ['text', 'response', 'message', 'content']:
        if hasattr(response_obj, attr):
            value = getattr(response_obj, attr)
            if isinstance(value, str):
                return value
    
    # Fallback: convert to string
    return str(response_obj)

class EnhancedResumeAnalyzer:
    """
    Advanced resume analyzer using AI for semantic understanding.
    """
    
    def __init__(self):
        self.ai_service = get_ai_service()
    
    def analyze_resume_advanced(self, resume_text: str, user_id: str) -> Dict[str, Any]:
        """
        Perform advanced AI-powered resume analysis.
        
        Args:
            resume_text: The resume content as text
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        try:
            # Create document for the resume
            resume_doc = Document(
                text=resume_text,
                metadata={
                    "user_id": user_id,
                    "document_type": "resume",
                    "analysis_version": "v1.0"
                }
            )
            
            # Create index for this resume
            index = self.ai_service.create_index_from_documents([resume_doc], "resumes")
            query_engine = index.as_query_engine()
            
            # Perform multiple analytical queries
            analysis_results = {}
            
            # 1. Skills Analysis
            skills_query = """
            Extract and categorize all technical and soft skills mentioned in this resume.
            Provide them in the following format:
            - Technical Skills: [list]
            - Soft Skills: [list]
            - Programming Languages: [list]
            - Frameworks/Tools: [list]
            """
            skills_response = query_engine.query(skills_query)
            analysis_results["skills_analysis"] = self._parse_skills_response(_safe_get_response(skills_response))
            
            # 2. Experience Level Assessment
            experience_query = """
            Analyze the experience level of this candidate based on:
            - Years of experience mentioned
            - Complexity of projects
            - Leadership roles
            - Career progression
            
            Classify as: Entry-Level, Mid-Level, Senior, or Executive
            Provide reasoning for the classification.
            """
            experience_response = query_engine.query(experience_query)
            experience_text = _safe_get_response(experience_response)
            analysis_results["experience_assessment"] = {
                "level": self._extract_experience_level(experience_text),
                "reasoning": experience_text
            }
            
            # 3. Career Trajectory Analysis
            trajectory_query = """
            Analyze the career trajectory and progression shown in this resume.
            Identify:
            - Career path consistency
            - Growth indicators
            - Role progression
            - Industry focus
            """
            trajectory_response = query_engine.query(trajectory_query)
            analysis_results["career_trajectory"] = _safe_get_response(trajectory_response)
            
            # 4. Improvement Suggestions
            improvement_query = """
            Based on this resume, provide specific suggestions for improvement:
            - Missing skills for career advancement
            - Resume formatting suggestions
            - Content gaps
            - Quantification opportunities
            """
            improvement_response = query_engine.query(improvement_query)
            analysis_results["improvement_suggestions"] = self._parse_suggestions(_safe_get_response(improvement_response))
            
            # 5. Industry Alignment
            industry_query = """
            Based on the skills, experience, and background, identify:
            - Primary industry alignment
            - Secondary industries this candidate could transition to
            - Emerging fields that match their skill set
            """
            industry_response = query_engine.query(industry_query)
            analysis_results["industry_alignment"] = _safe_get_response(industry_response)
            
            # Calculate overall quality score
            analysis_results["quality_score"] = self._calculate_quality_score(analysis_results)
            
            # Store metadata
            from datetime import datetime
            
            analysis_results["metadata"] = {
                "user_id": user_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "resume_length": len(resume_text),
                "confidence_scores": {
                    "skills": 0.85,
                    "experience": 0.90,
                    "trajectory": 0.80
                }
            }
            
            return {
                "success": True,
                "analysis": analysis_results
            }
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_skills_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the skills analysis response into structured data."""
        skills_dict = {
            "technical_skills": [],
            "soft_skills": [],
            "programming_languages": [],
            "frameworks_tools": []
        }
        
        # Simple parsing logic - in production, use more sophisticated NLP
        lines = response.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if "Technical Skills:" in line:
                current_category = "technical_skills"
                # Extract skills from the same line if present
                skills_part = line.split("Technical Skills:")[-1].strip()
                if skills_part:
                    skills_dict[current_category].extend([s.strip() for s in skills_part.split(',')])
            elif "Soft Skills:" in line:
                current_category = "soft_skills"
                skills_part = line.split("Soft Skills:")[-1].strip()
                if skills_part:
                    skills_dict[current_category].extend([s.strip() for s in skills_part.split(',')])
            elif "Programming Languages:" in line:
                current_category = "programming_languages"
                skills_part = line.split("Programming Languages:")[-1].strip()
                if skills_part:
                    skills_dict[current_category].extend([s.strip() for s in skills_part.split(',')])
            elif "Frameworks/Tools:" in line:
                current_category = "frameworks_tools"
                skills_part = line.split("Frameworks/Tools:")[-1].strip()
                if skills_part:
                    skills_dict[current_category].extend([s.strip() for s in skills_part.split(',')])
            elif current_category and line and not line.startswith('-'):
                # Continue parsing skills from subsequent lines
                skills_dict[current_category].extend([s.strip() for s in line.split(',') if s.strip()])
        
        return skills_dict
    
    def _extract_experience_level(self, response: str) -> str:
        """Extract experience level from the analysis response."""
        response_lower = response.lower()
        
        if "entry-level" in response_lower or "entry level" in response_lower:
            return "Entry-Level"
        elif "senior" in response_lower:
            return "Senior"
        elif "executive" in response_lower:
            return "Executive"
        elif "mid-level" in response_lower or "mid level" in response_lower:
            return "Mid-Level"
        else:
            # Default classification based on keywords
            if any(word in response_lower for word in ["0-2 years", "recent graduate", "junior"]):
                return "Entry-Level"
            elif any(word in response_lower for word in ["5+ years", "lead", "architect"]):
                return "Senior"
            else:
                return "Mid-Level"
    
    def _parse_suggestions(self, response: str) -> List[Dict[str, str]]:
        """Parse improvement suggestions into structured format."""
        suggestions = []
        lines = response.split('\n')
        
        current_category = None
        current_suggestions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # This is a suggestion item
                suggestion_text = line[1:].strip()
                if current_category:
                    suggestions.append({
                        "category": current_category,
                        "suggestion": suggestion_text
                    })
                else:
                    suggestions.append({
                        "category": "General",
                        "suggestion": suggestion_text
                    })
            elif line and ':' in line:
                # This might be a category header
                current_category = line.split(':')[0].strip()
        
        return suggestions
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate an overall resume quality score (0-100)."""
        score = 50  # Base score
        
        # Skills diversity bonus
        skills_analysis = analysis.get("skills_analysis", {})
        total_skills = sum(len(skills) for skills in skills_analysis.values())
        score += min(total_skills * 2, 30)  # Up to 30 points for skills
        
        # Experience level bonus
        experience_level = analysis.get("experience_assessment", {}).get("level", "Entry-Level")
        level_scores = {
            "Entry-Level": 5,
            "Mid-Level": 15,
            "Senior": 25,
            "Executive": 20  # Slightly lower as these resumes might be over-qualified for some roles
        }
        score += level_scores.get(experience_level, 0)
        
        # Improvement suggestions penalty (fewer suggestions = better resume)
        suggestions_count = len(analysis.get("improvement_suggestions", []))
        score -= min(suggestions_count * 3, 15)
        
        return max(0, min(100, score))  # Ensure score is between 0 and 100
    
    def get_skill_gap_analysis(self, resume_text: str, target_job_description: str) -> Dict[str, Any]:
        """
        Analyze skill gaps between resume and target job.
        """
        try:
            # Create documents
            resume_doc = Document(text=resume_text, metadata={"type": "resume"})
            job_doc = Document(text=target_job_description, metadata={"type": "job"})
            
            # Create index with both documents
            index = self.ai_service.create_index_from_documents([resume_doc, job_doc], "resumes")
            query_engine = index.as_query_engine()
            
            gap_query = """
            Compare the resume and job description to identify:
            1. Skills mentioned in the job but missing from the resume
            2. Skills in the resume that match the job requirements
            3. Experience gaps that need to be addressed
            4. Recommendations for skill development priority
            
            Provide a structured analysis with specific actionable recommendations.
            """
            
            gap_response = query_engine.query(gap_query)
            gap_text = _safe_get_response(gap_response)
            
            return {
                "success": True,
                "skill_gap_analysis": gap_text,
                "recommendations": self._extract_gap_recommendations(gap_text)
            }
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_gap_recommendations(self, response: str) -> List[str]:
        """Extract actionable recommendations from gap analysis."""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                recommendation = line[1:].strip()
                if recommendation and len(recommendation) > 10:  # Filter out very short items
                    recommendations.append(recommendation)
        
        return recommendations[:10]  # Limit to top 10 recommendations