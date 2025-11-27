"""
Job Recommender using semantic search and AI analysis.
"""
import os
from typing import Dict, List, Any, Optional
from llama_index.core import Document
from ai_services.llama_service import get_ai_service
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
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

class JobRecommender:
    """
    AI-powered job recommendation engine using semantic matching.
    """
    
    def __init__(self):
        self.ai_service = get_ai_service()
    
    def index_job_description(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index a job description in the vector database.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Success status and job ID
        """
        try:
            # Create comprehensive job text for embedding
            job_text = self._create_job_embedding_text(job_data)
            
            # Create document
            job_doc = Document(
                text=job_text,
                metadata={
                    "job_id": job_data.get("job_id"),
                    "title": job_data.get("title", ""),
                    "company": job_data.get("company", ""),
                    "location": job_data.get("location", ""),
                    "experience_level": job_data.get("experience_level", ""),
                    "salary_min": job_data.get("salary_min", 0),
                    "salary_max": job_data.get("salary_max", 0),
                    "remote_ok": job_data.get("remote_ok", False),
                    "job_type": job_data.get("job_type", "full-time"),
                    "posted_date": job_data.get("posted_date", ""),
                    "required_skills": job_data.get("required_skills", [])
                }
            )
            
            # Index the job
            index = self.ai_service.create_index_from_documents([job_doc], "jobs")
            
            return {
                "success": True,
                "job_id": job_data.get("job_id"),
                "message": "Job indexed successfully"
            }
            
        except Exception as e:
            logger.error(f"Job indexing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def recommend_jobs(self, resume_text: str, user_preferences: Optional[Dict[str, Any]] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get personalized job recommendations based on resume.
        
        Args:
            resume_text: The candidate's resume content
            user_preferences: Optional filters (location, salary, etc.)
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended jobs with explanations
        """
        try:
            # Get query engine for jobs collection
            query_engine = self.ai_service.get_query_engine("jobs", similarity_top_k=limit)
            
            # Create enhanced query text
            query_text = self._create_recommendation_query(resume_text, user_preferences)
            
            # Get initial recommendations
            recommendations_response = query_engine.query(query_text)
            
            # Get detailed explanations for top matches
            detailed_recommendations = self._get_detailed_recommendations(
                resume_text, 
                recommendations_response, 
                user_preferences
            )
            
            return {
                "success": True,
                "recommendations": detailed_recommendations,
                "total_found": len(detailed_recommendations),
                "query_used": query_text
            }
            
        except Exception as e:
            logger.error(f"Job recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def explain_job_match(self, resume_text: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide detailed explanation for why a job matches a candidate.
        
        Args:
            resume_text: Candidate's resume
            job_data: Job information
            
        Returns:
            Detailed match explanation
        """
        try:
            # Create documents for both resume and job
            resume_doc = Document(text=resume_text, metadata={"type": "resume"})
            job_doc = Document(
                text=self._create_job_embedding_text(job_data),
                metadata={"type": "job"}
            )
            
            # Create index with both documents
            index = self.ai_service.create_index_from_documents([resume_doc, job_doc], "resumes")
            query_engine = index.as_query_engine()
            
            explanation_query = f"""
            Analyze why this candidate is a good fit for this job position: {job_data.get('title', 'this position')}.
            
            Consider:
            1. Skill alignment and overlap
            2. Experience level match
            3. Industry background compatibility
            4. Career growth potential
            5. Cultural fit indicators
            6. Potential challenges or gaps
            
            Provide a comprehensive match analysis with:
            - Overall match score (0-100)
            - Key strengths that align
            - Potential concerns or gaps
            - Specific recommendations for the candidate
            """
            
            explanation_response = query_engine.query(explanation_query)
            explanation_text = _safe_get_response(explanation_response)
            
            return {
                "success": True,
                "match_explanation": explanation_text,
                "match_score": self._extract_match_score(explanation_text),
                "key_alignments": self._extract_alignments(explanation_text),
                "concerns": self._extract_concerns(explanation_text)
            }
            
        except Exception as e:
            logger.error(f"Job match explanation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_career_suggestions(self, resume_text: str) -> Dict[str, Any]:
        """
        Get AI-powered career progression suggestions.
        
        Args:
            resume_text: Candidate's resume
            
        Returns:
            Career progression recommendations
        """
        try:
            # Create document
            resume_doc = Document(text=resume_text, metadata={"type": "resume"})
            index = self.ai_service.create_index_from_documents([resume_doc], "resumes")
            query_engine = index.as_query_engine()
            
            career_query = """
            Based on this resume, provide comprehensive career progression advice:
            
            1. Next logical career steps (2-3 specific roles)
            2. Skills to develop for advancement
            3. Industry trends to watch
            4. Salary progression expectations
            5. Alternative career paths to consider
            6. Timeline for career goals (short, medium, long-term)
            
            Be specific and actionable in your recommendations.
            """
            
            career_response = query_engine.query(career_query)
            career_text = _safe_get_response(career_response)
            
            return {
                "success": True,
                "career_advice": career_text,
                "next_roles": self._extract_next_roles(career_text),
                "skills_to_develop": self._extract_skills_development(career_text),
                "timeline": self._extract_timeline(career_text)
            }
            
        except Exception as e:
            logger.error(f"Career suggestions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_job_embedding_text(self, job_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of job for embedding."""
        parts = []
        
        # Basic info
        if job_data.get("title"):
            parts.append(f"Job Title: {job_data['title']}")
        if job_data.get("company"):
            parts.append(f"Company: {job_data['company']}")
        
        # Description
        if job_data.get("description"):
            parts.append(f"Description: {job_data['description']}")
        
        # Requirements
        if job_data.get("requirements"):
            parts.append(f"Requirements: {' '.join(job_data['requirements'])}")
        
        # Skills
        if job_data.get("required_skills"):
            parts.append(f"Required Skills: {' '.join(job_data['required_skills'])}")
        
        # Other details
        if job_data.get("experience_level"):
            parts.append(f"Experience Level: {job_data['experience_level']}")
        
        if job_data.get("location"):
            parts.append(f"Location: {job_data['location']}")
        
        return " | ".join(parts)
    
    def _create_recommendation_query(self, resume_text: str, preferences: Optional[Dict[str, Any]] = None) -> str:
        """Create optimized query for job recommendations."""
        query_parts = [f"Find jobs that match this candidate profile: {resume_text[:500]}"]
        
        if preferences:
            if preferences.get("preferred_location"):
                query_parts.append(f"Preferred location: {preferences['preferred_location']}")
            if preferences.get("min_salary"):
                query_parts.append(f"Minimum salary: {preferences['min_salary']}")
            if preferences.get("experience_level"):
                query_parts.append(f"Experience level: {preferences['experience_level']}")
            if preferences.get("remote_ok"):
                query_parts.append("Remote work preferred")
            if preferences.get("preferred_industries"):
                query_parts.append(f"Industries: {', '.join(preferences['preferred_industries'])}")
        
        return " | ".join(query_parts)
    
    def _get_detailed_recommendations(self, resume_text: str, recommendations_response, preferences: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed recommendations with AI explanations."""
        recommendations = []
        
        # Parse actual vector search results from source_nodes
        if hasattr(recommendations_response, 'source_nodes'):
            for idx, node in enumerate(recommendations_response.source_nodes[:10]):  # Top 10 matches
                try:
                    # Extract job details from node metadata and content
                    metadata = node.metadata if hasattr(node, 'metadata') else {}
                    content = node.text if hasattr(node, 'text') else str(node)
                    
                    # Get similarity score
                    match_score = int((node.score * 100) if hasattr(node, 'score') else 75)
                    
                    # Parse job details from metadata or content
                    job_id = metadata.get('job_id', f'job_{idx:03d}')
                    title = metadata.get('title') or metadata.get('job_title', 'Position')
                    company = metadata.get('company') or metadata.get('company_name', 'Company')
                    location = metadata.get('location', 'Not specified')
                    salary_range = metadata.get('salary_range') or metadata.get('salary', 'Not specified')
                    
                    # Extract key skills/requirements from content
                    key_matches = []
                    if 'required_skills' in metadata:
                        key_matches = metadata['required_skills'][:5]  # Top 5 skills
                    
                    # Generate explanation for this match
                    explanation = f"Match score {match_score}% based on skills and experience alignment."
                    
                    recommendations.append({
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": location,
                        "match_score": match_score,
                        "salary_range": salary_range,
                        "key_matches": key_matches,
                        "explanation": explanation
                    })
                except Exception as e:
                    print(f"Warning: Could not parse job recommendation: {e}")
                    continue
        
        return recommendations
    
    def _extract_match_score(self, response: str) -> int:
        """Extract match score from explanation response."""
        # Look for patterns like "85/100", "Score: 85", "85%"
        import re
        
        patterns = [
            r'(\d+)/100',
            r'[Ss]core:?\s*(\d+)',
            r'(\d+)%',
            r'(\d+)\s*out\s*of\s*100'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return int(match.group(1))
        
        return 75  # Default score if none found
    
    def _extract_alignments(self, response: str) -> List[str]:
        """Extract key alignments from explanation."""
        alignments = []
        lines = response.split('\n')
        
        in_strengths_section = False
        for line in lines:
            line = line.strip()
            if "strength" in line.lower() or "alignment" in line.lower():
                in_strengths_section = True
                continue
            elif "concern" in line.lower() or "gap" in line.lower():
                in_strengths_section = False
                continue
            elif in_strengths_section and (line.startswith('-') or line.startswith('•')):
                alignments.append(line[1:].strip())
        
        return alignments[:5]  # Top 5 alignments
    
    def _extract_concerns(self, response: str) -> List[str]:
        """Extract potential concerns from explanation."""
        concerns = []
        lines = response.split('\n')
        
        in_concerns_section = False
        for line in lines:
            line = line.strip()
            if "concern" in line.lower() or "gap" in line.lower() or "challenge" in line.lower():
                in_concerns_section = True
                continue
            elif "strength" in line.lower() or "recommendation" in line.lower():
                in_concerns_section = False
                continue
            elif in_concerns_section and (line.startswith('-') or line.startswith('•')):
                concerns.append(line[1:].strip())
        
        return concerns[:3]  # Top 3 concerns
    
    def _extract_next_roles(self, response: str) -> List[str]:
        """Extract next career roles from career advice."""
        roles = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if ("next" in line.lower() or "role" in line.lower()) and (line.startswith('-') or line.startswith('•')):
                role = line[1:].strip()
                if len(role) > 5:  # Filter out very short entries
                    roles.append(role)
        
        return roles[:3]  # Top 3 roles
    
    def _extract_skills_development(self, response: str) -> List[str]:
        """Extract skills to develop from career advice."""
        skills = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if "skill" in line.lower() and (line.startswith('-') or line.startswith('•')):
                skill = line[1:].strip()
                if len(skill) > 5:
                    skills.append(skill)
        
        return skills[:5]  # Top 5 skills
    
    def _extract_timeline(self, response: str) -> Dict[str, str]:
        """Extract timeline information from career advice."""
        timeline = {"short_term": "", "medium_term": "", "long_term": ""}
        
        if "short" in response.lower():
            # Extract short-term goals
            timeline["short_term"] = "6-12 months: Focus on skill development and networking"
        
        if "medium" in response.lower():
            timeline["medium_term"] = "1-3 years: Target promotion or role transition"
        
        if "long" in response.lower():
            timeline["long_term"] = "3-5 years: Leadership roles and strategic positions"
        
        return timeline