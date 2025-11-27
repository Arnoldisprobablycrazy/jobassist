"""
Enhanced Similarity Analyzer using AI embeddings and semantic matching.
"""
import logging
from typing import Dict, List, Any, Tuple
import numpy as np
from ai_services.llama_service import get_ai_service
from llama_index.core import Document

logger = logging.getLogger(__name__)

class EnhancedSimilarityAnalyzer:
    """
    AI-powered similarity analysis using semantic embeddings.
    Provides more accurate matching than basic TF-IDF.
    """
    
    def __init__(self):
        try:
            self.ai_service = get_ai_service()
            logger.info("Enhanced Similarity Analyzer initialized with AI service")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.ai_service = None
    
    def calculate_enhanced_similarity(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive similarity using AI embeddings and semantic analysis.
        
        Args:
            resume_data: Parsed resume information
            job_data: Parsed job description information
            
        Returns:
            Detailed similarity scores and analysis
        """
        if not self.ai_service:
            return self._fallback_similarity(resume_data, job_data)
        
        try:
            # Extract text representations
            resume_text = self._create_resume_text(resume_data)
            job_text = self._create_job_text(job_data)
            
            # Calculate different similarity dimensions
            overall_similarity = self._calculate_semantic_similarity(resume_text, job_text)
            skill_match = self._calculate_skill_match(resume_data, job_data)
            experience_match = self._calculate_experience_match(resume_data, job_data)
            education_match = self._calculate_education_match(resume_data, job_data)
            
            # Get detailed analysis from AI
            detailed_analysis = self._get_ai_analysis(resume_data, job_data)
            
            # Calculate weighted overall score
            weighted_score = (
                overall_similarity * 0.3 +
                skill_match['score'] * 0.35 +
                experience_match['score'] * 0.25 +
                education_match['score'] * 0.10
            )
            
            # Generate improvement recommendations to reach 80%
            improvement_plan = self._generate_improvement_plan(
                resume_data, 
                job_data, 
                weighted_score,
                skill_match,
                experience_match
            )
            
            return {
                'success': True,
                'overall_score': round(weighted_score, 2),
                'semantic_similarity': round(overall_similarity, 2),
                'skill_match': skill_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'detailed_analysis': detailed_analysis,
                'recommendation': self._generate_recommendation(weighted_score),
                'strengths': self._identify_strengths(resume_data, job_data, skill_match),
                'gaps': self._identify_gaps(resume_data, job_data, skill_match),
                'improvement_plan': improvement_plan,
                'method': 'ai_semantic'
            }
            
        except Exception as e:
            logger.error(f"Enhanced similarity calculation failed: {e}")
            return self._fallback_similarity(resume_data, job_data)
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings."""
        try:
            # Get embeddings for both texts
            embedding1 = self.ai_service.embed_model.get_text_embedding(text1)
            embedding2 = self.ai_service.embed_model.get_text_embedding(text2)
            
            # Calculate cosine similarity
            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)
            
            cosine_sim = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            # Convert to percentage (0-100)
            similarity_score = (cosine_sim + 1) / 2 * 100  # Normalize from [-1,1] to [0,100]
            
            return min(max(similarity_score, 0), 100)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_skill_match(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate detailed skill matching with semantic understanding."""
        try:
            # AGGRESSIVE DEDUPLICATION: Same logic as cover letter generator
            # Deduplicate resume skills
            resume_skills_raw = resume_data.get('skills', [])
            resume_skills_dedup = []
            resume_normalized = []
            
            for skill in resume_skills_raw:
                if not skill or len(skill.strip()) < 2:
                    continue
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                
                is_duplicate = False
            for seen in resume_normalized:
                # Check substring matches (e.g., "Agile" vs "Agile Methodology")
                if skill_lower == seen or skill_lower in seen or seen in skill_lower:
                    is_duplicate = True
                    break
                
                # Special case: CI/CD variants
                cicd_terms = {'ci/cd', 'ci-cd', 'cicd', 'continuous integration', 'continuous deployment'}
                if skill_lower in cicd_terms and seen in cicd_terms:
                    is_duplicate = True
                    break
                
                # Check word overlap (>70% similarity)
                skill_words = set(skill_lower.split())
                seen_words = set(seen.split())
                if skill_words and seen_words:
                    overlap = len(skill_words & seen_words) / max(len(skill_words), len(seen_words))
                    if overlap > 0.7:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                resume_skills_dedup.append(skill_clean)
                resume_normalized.append(skill_lower)
            
            # Deduplicate required skills
            required_skills_raw = job_data.get('required_skills', [])
            required_skills_dedup = []
            required_normalized = []
            
            for skill in required_skills_raw:
                if not skill or len(skill.strip()) < 2:
                    continue
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                
                is_duplicate = False
                for seen in required_normalized:
                    if skill_lower == seen or skill_lower in seen or seen in skill_lower:
                        is_duplicate = True
                        break
                    
                    # Special case: CI/CD variants
                    cicd_terms = {'ci/cd', 'ci-cd', 'cicd', 'continuous integration', 'continuous deployment'}
                    if skill_lower in cicd_terms and seen in cicd_terms:
                        is_duplicate = True
                        break
                    
                    skill_words = set(skill_lower.split())
                    seen_words = set(seen.split())
                    if skill_words and seen_words:
                        overlap = len(skill_words & seen_words) / max(len(skill_words), len(seen_words))
                        if overlap > 0.7:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    required_skills_dedup.append(skill_clean)
                    required_normalized.append(skill_lower)
            
            # Now work with deduplicated sets
            resume_skills = set(resume_normalized)
            required_skills = set(required_normalized)
            
            if not required_skills:
                return {'score': 0.0, 'matched': [], 'missing': [], 'total_required': 0}
            
            # Direct matches (exact or substring)
            direct_matches = set()
            for req_skill in required_skills:
                for res_skill in resume_skills:
                    # Exact match or substring match
                    if req_skill == res_skill or req_skill in res_skill or res_skill in req_skill:
                        direct_matches.add(req_skill)
                        break
            
            # Semantic matches (skills that are similar but not exact/substring)
            remaining_resume = resume_skills - {s for s in resume_skills if any(s in m or m in s for m in direct_matches)}
            remaining_required = required_skills - direct_matches
            
            semantic_matches = self._find_semantic_skill_matches(
                list(remaining_resume),
                list(remaining_required)
            )
            
            all_matches = direct_matches.union(semantic_matches)
            missing_skills = required_skills - all_matches
            
            # Calculate score with bonus for semantic matches
            direct_match_score = len(direct_matches) / len(required_skills) * 100
            semantic_match_score = len(semantic_matches) / len(required_skills) * 50  # 50% credit
            total_score = min(direct_match_score + semantic_match_score, 100)
            
            return {
                'score': round(total_score, 2),
                'matched': sorted(list(all_matches)),
                'direct_matches': sorted(list(direct_matches)),
                'semantic_matches': sorted(list(semantic_matches)),
                'missing': sorted(list(missing_skills)),
                'total_required': len(required_skills),
                'match_count': len(all_matches),
                'match_percentage': round(len(all_matches) / len(required_skills) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Skill match calculation failed: {e}")
            return {'score': 0.0, 'matched': [], 'missing': [], 'total_required': 0}
    
    def _find_semantic_skill_matches(
        self, 
        candidate_skills: List[str], 
        required_skills: List[str],
        threshold: float = 0.88  # Increased threshold to avoid false positives
    ) -> set:
        """Find semantically similar skills using embeddings."""
        if not self.ai_service or not candidate_skills or not required_skills:
            return set()
        
        try:
            semantic_matches = set()
            
            for req_skill in required_skills:
                # Skip if already handled by substring matching
                if any(req_skill in cand or cand in req_skill for cand in candidate_skills):
                    continue
                
                try:
                    req_embedding = self.ai_service.embed_model.get_text_embedding(req_skill)
                    
                    best_match = None
                    best_similarity = 0.0
                    
                    for cand_skill in candidate_skills:
                        # Skip if substring match (already handled)
                        if req_skill in cand_skill or cand_skill in req_skill:
                            continue
                        
                        cand_embedding = self.ai_service.embed_model.get_text_embedding(cand_skill)
                        
                        # Calculate similarity
                        similarity = np.dot(req_embedding, cand_embedding) / (
                            np.linalg.norm(req_embedding) * np.linalg.norm(cand_embedding)
                        )
                        
                        if similarity >= threshold and similarity > best_similarity:
                            best_match = req_skill
                            best_similarity = similarity
                    
                    if best_match:
                        semantic_matches.add(best_match)
                        logger.info(f"Semantic match: {best_match} (similarity: {best_similarity:.2f})")
                
                except Exception as embed_error:
                    logger.warning(f"Failed to embed skill '{req_skill}': {embed_error}")
                    continue
            
            return semantic_matches
            
        except Exception as e:
            logger.error(f"Semantic skill matching failed: {e}")
            return set()
    
    def _calculate_experience_match(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate experience level match."""
        try:
            experience = resume_data.get('experience', [])
            total_years = self._calculate_total_experience(experience)
            
            job_experience_level = job_data.get('experience_level', 'Not Specified').lower()
            
            # Define experience ranges
            experience_ranges = {
                'junior': (0, 2),
                'entry': (0, 2),
                'mid-level': (2, 5),
                'intermediate': (2, 5),
                'senior': (5, 10),
                'lead': (7, 15),
                'principal': (10, 20),
                'staff': (10, 20)
            }
            
            score = 100.0  # Default perfect match if not specified
            match_status = 'perfect'
            
            for level, (min_years, max_years) in experience_ranges.items():
                if level in job_experience_level:
                    if min_years <= total_years <= max_years:
                        score = 100.0
                        match_status = 'perfect'
                    elif total_years > max_years:
                        # Overqualified
                        score = 90.0
                        match_status = 'overqualified'
                    elif total_years < min_years:
                        # Underqualified - penalize more
                        gap = min_years - total_years
                        score = max(50.0 - (gap * 10), 0)
                        match_status = 'underqualified'
                    break
            
            return {
                'score': round(score, 2),
                'candidate_years': total_years,
                'required_level': job_experience_level,
                'match_status': match_status,
                'relevant_experience': self._extract_relevant_experience(experience, job_data)
            }
            
        except Exception as e:
            logger.error(f"Experience match calculation failed: {e}")
            return {'score': 0.0, 'candidate_years': 0, 'match_status': 'unknown'}
    
    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate total years of experience."""
        import re
        from datetime import datetime
        
        total_years = 0.0
        
        for exp in experience:
            # Try to parse duration from various formats
            duration_str = exp.get('duration', '')
            dates = exp.get('dates', '')
            
            # Method 1: Look for explicit duration like "2 years", "3.5 years"
            if duration_str:
                years_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:year|yr)', duration_str.lower())
                if years_match:
                    total_years += float(years_match.group(1))
                    continue
                
                # Look for months
                months_match = re.search(r'(\d+)\s*(?:month|mo)', duration_str.lower())
                if months_match:
                    total_years += float(months_match.group(1)) / 12
                    continue
            
            # Method 2: Parse date ranges like "Jan 2020 - Dec 2022"
            if dates:
                try:
                    # Try to extract year ranges
                    years = re.findall(r'\b(20\d{2})\b', dates)
                    if len(years) >= 2:
                        start_year = int(years[0])
                        end_year = int(years[-1]) if years[-1] else datetime.now().year
                        total_years += max(end_year - start_year, 0.5)  # Min 0.5 years
                        continue
                except:
                    pass
            
            # Method 3: Default estimate - if we can't parse, assume 1.5 years per position
            total_years += 1.5
        
        return round(total_years, 1)
    
    def _extract_relevant_experience(
        self, 
        experience: List[Dict[str, Any]], 
        job_data: Dict[str, Any]
    ) -> List[str]:
        """Extract experience entries relevant to the job."""
        relevant = []
        job_title = job_data.get('title', '').lower()
        required_skills = set(s.lower() for s in job_data.get('required_skills', []))
        
        for exp in experience:
            title = exp.get('title', '').lower()
            description = exp.get('description', '').lower()
            
            # Check if experience is relevant
            if (any(skill in title or skill in description for skill in required_skills) or
                any(word in title for word in job_title.split()[:3])):
                relevant.append(f"{exp.get('title', '')} at {exp.get('company', '')}")
        
        return relevant[:3]
    
    def _calculate_education_match(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate education requirement match."""
        try:
            education = resume_data.get('education', [])
            
            # Check if job requires specific degree
            job_description = job_data.get('description', '').lower()
            
            degree_levels = {
                'phd': 5,
                'doctorate': 5,
                'master': 4,
                "master's": 4,
                'msc': 4,
                'mba': 4,
                'bachelor': 3,
                "bachelor's": 3,
                'bsc': 3,
                'associate': 2,
                'diploma': 1
            }
            
            # Find highest degree in resume
            candidate_level = 0
            for edu in education:
                degree = edu.get('degree', '').lower()
                for deg, level in degree_levels.items():
                    if deg in degree:
                        candidate_level = max(candidate_level, level)
            
            # Find required degree level
            required_level = 0
            for deg, level in degree_levels.items():
                if deg in job_description:
                    required_level = max(required_level, level)
            
            # Calculate score
            if required_level == 0:
                score = 100.0  # No specific requirement
                status = 'not_required'
            elif candidate_level >= required_level:
                score = 100.0
                status = 'meets_requirement'
            elif candidate_level == required_level - 1:
                score = 75.0  # One level below
                status = 'close'
            else:
                score = 50.0  # Below requirement
                status = 'below_requirement'
            
            return {
                'score': round(score, 2),
                'candidate_level': candidate_level,
                'required_level': required_level,
                'status': status,
                'highest_degree': education[0].get('degree', 'None') if education else 'None'
            }
            
        except Exception as e:
            logger.error(f"Education match calculation failed: {e}")
            return {'score': 100.0, 'status': 'not_specified'}
    
    def _get_ai_analysis(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> str:
        """Get detailed AI analysis of the match."""
        try:
            resume_summary = self._create_resume_text(resume_data)
            job_summary = self._create_job_text(job_data)
            
            prompt = f"""Analyze the match between this candidate and job posting:

CANDIDATE PROFILE:
{resume_summary[:1500]}

JOB POSTING:
{job_summary[:1500]}

Provide a concise analysis (3-4 sentences) covering:
1. Overall fit assessment
2. Key strengths for this role
3. Main areas of concern or gaps
4. Recommendation (Strong Match / Good Match / Moderate Match / Weak Match)

Analysis:"""
            
            response = self.ai_service.llm.complete(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return "Detailed analysis unavailable"
    
    def _create_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of resume."""
        parts = []
        
        # Personal info
        personal_info = resume_data.get('personal_info', {})
        if personal_info.get('name'):
            parts.append(f"Name: {personal_info['name']}")
        
        # Skills
        skills = resume_data.get('skills', [])
        if skills:
            parts.append(f"Skills: {', '.join(skills[:20])}")
        
        # Experience
        experience = resume_data.get('experience', [])
        for exp in experience[:3]:
            exp_text = f"{exp.get('title', '')} at {exp.get('company', '')}"
            if exp.get('description'):
                exp_text += f": {exp['description'][:200]}"
            parts.append(exp_text)
        
        # Education
        education = resume_data.get('education', [])
        for edu in education:
            parts.append(f"{edu.get('degree', '')} from {edu.get('institution', '')}")
        
        return "\n".join(parts)
    
    def _create_job_text(self, job_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of job."""
        parts = []
        
        if job_data.get('title'):
            parts.append(f"Title: {job_data['title']}")
        if job_data.get('company'):
            parts.append(f"Company: {job_data['company']}")
        if job_data.get('experience_level'):
            parts.append(f"Level: {job_data['experience_level']}")
        
        required_skills = job_data.get('required_skills', [])
        if required_skills:
            parts.append(f"Required Skills: {', '.join(required_skills[:15])}")
        
        responsibilities = job_data.get('responsibilities', [])
        if responsibilities:
            parts.append(f"Responsibilities: {'; '.join(responsibilities[:5])}")
        
        if job_data.get('description'):
            parts.append(f"Description: {job_data['description'][:500]}")
        
        return "\n".join(parts)
    
    def _generate_recommendation(self, score: float) -> str:
        """Generate hiring recommendation based on score."""
        if score >= 85:
            return "Strong Match - Highly recommend proceeding with interview"
        elif score >= 70:
            return "Good Match - Recommend reviewing in detail"
        elif score >= 55:
            return "Moderate Match - Consider for interview if other candidates are limited"
        else:
            return "Weak Match - May not meet core requirements"
    
    def _generate_improvement_plan(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        current_score: float,
        skill_match: Dict[str, Any],
        experience_match: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate actionable improvement plan to reach 80% match.
        Provides specific recommendations on how to adjust resume.
        """
        target_score = 80.0
        score_gap = target_score - current_score
        
        if current_score >= target_score:
            return {
                'needed': False,
                'current_score': round(current_score, 2),
                'target_score': target_score,
                'message': 'Your resume already meets or exceeds the 80% match threshold!',
                'recommendations': []
            }
        
        recommendations = []
        priority_actions = []
        
        # 1. Skill Gap Analysis (35% weight - highest impact)
        missing_skills = skill_match.get('missing', [])
        if missing_skills:
            skill_impact = len(missing_skills) * 3.5  # Each missing skill = ~3.5% impact
            
            recommendations.append({
                'category': 'Skills',
                'priority': 'HIGH',
                'impact': f'+{min(skill_impact, score_gap):.1f}%',
                'current_status': f"{skill_match.get('match_count', 0)}/{skill_match.get('total_required', 0)} skills matched",
                'action': 'Add Missing Skills to Resume',
                'details': self._generate_skill_recommendations(missing_skills, resume_data),
                'specific_skills': missing_skills[:5]  # Top 5 missing skills
            })
            
            priority_actions.append('Add missing required skills to your resume')
        
        # 2. Experience Optimization (25% weight)
        exp_status = experience_match.get('match_status', 'unknown')
        if exp_status == 'underqualified' or current_score < 70:
            exp_recommendations = self._generate_experience_recommendations(
                resume_data, 
                job_data,
                experience_match
            )
            if exp_recommendations:
                recommendations.append(exp_recommendations)
                priority_actions.append('Emphasize relevant experience')
        
        # 3. Keyword Optimization (30% weight for semantic similarity)
        keyword_recommendations = self._generate_keyword_recommendations(
            resume_data,
            job_data
        )
        if keyword_recommendations:
            recommendations.append(keyword_recommendations)
            priority_actions.append('Optimize resume keywords')
        
        # 4. AI-Generated Specific Recommendations
        ai_recommendations = self._get_ai_improvement_suggestions(
            resume_data,
            job_data,
            current_score,
            target_score
        )
        
        return {
            'needed': True,
            'current_score': round(current_score, 2),
            'target_score': target_score,
            'score_gap': round(score_gap, 2),
            'estimated_actions': len(recommendations),
            'priority_actions': priority_actions[:3],
            'recommendations': recommendations,
            'ai_suggestions': ai_recommendations,
            'summary': self._generate_improvement_summary(current_score, target_score, recommendations)
        }
    
    def _generate_skill_recommendations(
        self,
        missing_skills: List[str],
        resume_data: Dict[str, Any]
    ) -> str:
        """Generate specific skill addition recommendations."""
        current_skills = set(s.lower() for s in resume_data.get('skills', []))
        
        suggestions = []
        
        for skill in missing_skills[:5]:
            skill_lower = skill.lower()
            
            # Check if candidate has related skills
            related = []
            skill_families = {
                'python': ['programming', 'scripting', 'backend'],
                'javascript': ['frontend', 'web', 'react', 'node'],
                'aws': ['cloud', 'azure', 'gcp', 'devops'],
                'docker': ['containerization', 'kubernetes', 'devops'],
                'sql': ['database', 'mysql', 'postgresql'],
                'react': ['frontend', 'javascript', 'ui'],
                'machine learning': ['ai', 'data science', 'deep learning']
            }
            
            if skill_lower in skill_families:
                for related_skill in skill_families[skill_lower]:
                    if related_skill in ' '.join(current_skills):
                        related.append(related_skill)
            
            if related:
                suggestions.append(f"• {skill}: Add to skills section (you have related: {', '.join(related)})")
            else:
                suggestions.append(f"• {skill}: Add to skills section or gain this skill through training")
        
        return '\n'.join(suggestions) if suggestions else 'Add the missing skills listed above to your resume'
    
    def _generate_experience_recommendations(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        experience_match: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate experience-related recommendations."""
        experience = resume_data.get('experience', [])
        job_title = job_data.get('title', '')
        required_skills = job_data.get('required_skills', [])
        
        details = []
        
        # Check if experience descriptions mention required skills
        for exp in experience[:3]:
            description = exp.get('description', '').lower()
            title = exp.get('title', '')
            
            mentioned_skills = [skill for skill in required_skills if skill.lower() in description]
            missing_skills = [skill for skill in required_skills if skill.lower() not in description]
            
            if missing_skills and mentioned_skills:
                details.append(f"• Enhance '{title}' description to mention: {', '.join(missing_skills[:3])}")
        
        if not details:
            details.append(f"• Rewrite job descriptions to emphasize skills relevant to {job_title}")
            details.append("• Add quantifiable achievements (percentages, numbers, metrics)")
            details.append("• Use action verbs: Led, Developed, Implemented, Improved")
        
        return {
            'category': 'Experience',
            'priority': 'MEDIUM',
            'impact': '+5-10%',
            'current_status': f"Experience level: {experience_match.get('match_status', 'unknown')}",
            'action': 'Optimize Experience Descriptions',
            'details': '\n'.join(details)
        }
    
    def _generate_keyword_recommendations(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate keyword optimization recommendations."""
        job_title = job_data.get('title', '')
        job_description = job_data.get('description', '')
        responsibilities = job_data.get('responsibilities', [])
        
        # Extract key phrases from job posting
        key_phrases = []
        
        # Common important phrases in job descriptions
        important_patterns = [
            'collaborate', 'lead', 'develop', 'implement', 'manage',
            'design', 'optimize', 'build', 'create', 'deliver'
        ]
        
        for pattern in important_patterns:
            if pattern in job_description.lower():
                key_phrases.append(pattern)
        
        details = [
            f"• Include exact job title in resume: '{job_title}'",
            "• Mirror key phrases from job description in your resume",
            f"• Use action verbs: {', '.join(key_phrases[:5])}",
            "• Match terminology (e.g., if they say 'collaborate', use 'collaborate' not 'work with')",
            "• Add industry-specific keywords from the job posting"
        ]
        
        return {
            'category': 'Keywords & Formatting',
            'priority': 'MEDIUM',
            'impact': '+5-8%',
            'current_status': 'Keyword optimization needed',
            'action': 'Improve ATS Compatibility',
            'details': '\n'.join(details)
        }
    
    def _get_ai_improvement_suggestions(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        current_score: float,
        target_score: float
    ) -> str:
        """Get AI-powered improvement suggestions."""
        if not self.ai_service:
            return "AI suggestions unavailable"
        
        try:
            resume_summary = self._create_resume_text(resume_data)[:1000]
            job_summary = self._create_job_text(job_data)[:1000]
            
            prompt = f"""You are a resume optimization expert. Analyze this resume-job match and provide specific, actionable recommendations to improve the match score from {current_score:.1f}% to {target_score:.1f}%.

CURRENT RESUME:
{resume_summary}

TARGET JOB:
{job_summary}

Provide 3-5 SPECIFIC, ACTIONABLE recommendations to improve this resume. Focus on:
1. What exact skills/keywords to add
2. How to rewrite experience descriptions
3. What achievements to emphasize
4. ATS optimization tips

Format each recommendation as a bullet point starting with an action verb.
Be specific and practical."""

            response = self.ai_service.llm.complete(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI improvement suggestions failed: {e}")
            return "Focus on adding missing skills and using keywords from the job description"
    
    def _generate_improvement_summary(
        self,
        current_score: float,
        target_score: float,
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate summary of improvement plan."""
        score_gap = target_score - current_score
        
        high_priority = sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        
        return f"To increase your match from {current_score:.1f}% to {target_score:.1f}% (gap of {score_gap:.1f}%), focus on {high_priority} high-priority action{'s' if high_priority != 1 else ''} and {len(recommendations) - high_priority} supporting improvements. Start with the highest impact actions first."
    
    def _identify_strengths(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any],
        skill_match: Dict[str, Any]
    ) -> List[str]:
        """Identify candidate's key strengths for this role."""
        strengths = []
        
        # Skill strengths
        matched_skills = skill_match.get('matched', [])
        if len(matched_skills) >= 5:
            strengths.append(f"Strong skill match with {len(matched_skills)} relevant skills")
        
        # Experience strengths
        relevant_exp = skill_match.get('relevant_experience', [])
        if relevant_exp:
            strengths.append(f"Relevant experience in similar roles")
        
        return strengths[:3]
    
    def _identify_gaps(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any],
        skill_match: Dict[str, Any]
    ) -> List[str]:
        """Identify gaps between candidate and requirements."""
        gaps = []
        
        missing_skills = skill_match.get('missing', [])
        if len(missing_skills) > 0:
            gaps.append(f"Missing {len(missing_skills)} required skills: {', '.join(list(missing_skills)[:3])}")
        
        return gaps[:3]
    
    def _fallback_similarity(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback similarity calculation without AI."""
        try:
            from job_analyzer import SimilarityCalculator
            
            calculator = SimilarityCalculator()
            
            resume_text = self._create_resume_text(resume_data)
            job_text = self._create_job_text(job_data)
            
            basic_scores = calculator.calculate_similarity(resume_text, job_text)
            
            return {
                'success': True,
                'overall_score': basic_scores.get('overall_score', 0),
                'skill_match': {'score': basic_scores.get('skill_match_score', 0)},
                'experience_match': {'score': basic_scores.get('experience_match_score', 0)},
                'method': 'basic_tfidf',
                'note': 'AI services unavailable - using basic similarity'
            }
            
        except Exception as e:
            logger.error(f"Fallback similarity failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'overall_score': 0
            }
