"""
ATS (Applicant Tracking System) Optimization Module

This module provides comprehensive ATS compatibility analysis and optimization
for resumes and cover letters to maximize chances of passing automated screening.
"""

from typing import Dict, List, Any, Tuple
import re


class ATSOptimizer:
    """
    Analyzes and optimizes documents for ATS compatibility.
    
    ATS systems scan for:
    1. Keywords matching job description
    2. Standard section headers
    3. Simple, parseable formatting
    4. Relevant skills and qualifications
    5. Proper file format (PDF, DOCX)
    """
    
    def __init__(self):
        # Standard ATS-friendly section headers
        self.standard_sections = [
            'experience', 'work experience', 'professional experience', 'employment history',
            'education', 'academic background', 'qualifications',
            'skills', 'technical skills', 'core competencies', 'key skills',
            'certifications', 'licenses', 'professional development',
            'summary', 'professional summary', 'profile', 'objective',
            'projects', 'achievements', 'accomplishments',
            'languages', 'publications', 'volunteer experience'
        ]
        
        # Keywords that ATS systems commonly flag as important
        self.action_verbs = [
            'achieved', 'improved', 'trained', 'managed', 'created', 'designed',
            'developed', 'implemented', 'increased', 'decreased', 'reduced',
            'led', 'coordinated', 'executed', 'launched', 'delivered',
            'optimized', 'streamlined', 'transformed', 'established', 'built',
            'spearheaded', 'pioneered', 'accelerated', 'enhanced', 'generated'
        ]
        
        # Common ATS formatting issues
        self.ats_red_flags = {
            'tables': r'<table|\\begin{tabular}',
            'columns': r'\\begin{multicols}',
            'text_boxes': r'<textbox|\\fbox',
            'headers_footers': r'\\fancyhead|\\fancyfoot',
            'images': r'<img|\\includegraphics',
            'special_chars': r'[★☆●○◆◇■□▪▫]',  # Decorative characters
        }
    
    def analyze_ats_compatibility(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any],
        resume_text: str = ""
    ) -> Dict[str, Any]:
        """
        Comprehensive ATS compatibility analysis.
        
        Args:
            resume_data: Parsed resume information
            job_data: Job description and requirements
            resume_text: Raw resume text (optional, for format analysis)
            
        Returns:
            Detailed ATS compatibility report with score and recommendations
        """
        
        # Calculate individual scores
        keyword_score = self._calculate_keyword_match(resume_data, job_data)
        format_score = self._check_format_compatibility(resume_text, resume_data)
        section_score = self._check_standard_sections(resume_data)
        content_score = self._check_content_quality(resume_data, job_data)
        
        # Calculate overall ATS score (weighted average)
        overall_score = (
            keyword_score['score'] * 0.35 +  # Keywords are most important
            format_score['score'] * 0.25 +    # Format matters for parsing
            section_score['score'] * 0.20 +   # Standard sections help ATS
            content_score['score'] * 0.20     # Quality content is important
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            keyword_score, format_score, section_score, content_score, overall_score
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'category': self._get_ats_category(overall_score),
            'keyword_analysis': keyword_score,
            'format_analysis': format_score,
            'section_analysis': section_score,
            'content_analysis': content_score,
            'recommendations': recommendations,
            'critical_issues': self._identify_critical_issues(keyword_score, format_score, section_score),
            'estimated_pass_rate': self._estimate_pass_rate(overall_score)
        }
    
    def _calculate_keyword_match(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate keyword matching score between resume and job description."""
        
        # Extract keywords from job description
        job_title = job_data.get('title', '').lower()
        job_description = job_data.get('description', '').lower()
        required_skills = [s.lower() for s in job_data.get('required_skills', [])]
        responsibilities = [r.lower() for r in job_data.get('responsibilities', [])]
        
        # Combine all job keywords
        job_keywords = set()
        
        # Add skills
        job_keywords.update(required_skills)
        
        # Extract keywords from title (split by common separators)
        title_words = re.findall(r'\b\w+\b', job_title)
        job_keywords.update(word for word in title_words if len(word) > 3)
        
        # Extract key terms from description
        desc_words = re.findall(r'\b\w{4,}\b', job_description)
        # Get most frequent words (likely important keywords)
        from collections import Counter
        word_freq = Counter(desc_words)
        top_keywords = [word for word, count in word_freq.most_common(30) if count >= 2]
        job_keywords.update(top_keywords)
        
        # Remove common stop words
        stop_words = {'with', 'have', 'this', 'that', 'from', 'will', 'your', 
                     'about', 'their', 'which', 'when', 'where', 'must', 'should',
                     'experience', 'work', 'working', 'ability', 'strong', 'knowledge'}
        job_keywords = {kw for kw in job_keywords if kw not in stop_words}
        
        # Get resume content
        resume_skills = [s.lower() for s in resume_data.get('skills', [])]
        resume_experience = resume_data.get('experience', [])
        resume_education = resume_data.get('education', [])
        
        # Build resume keyword set
        resume_keywords = set(resume_skills)
        
        for exp in resume_experience:
            title = exp.get('title', '').lower()
            desc = exp.get('description', '').lower()
            resume_keywords.update(re.findall(r'\b\w{4,}\b', title + ' ' + desc))
        
        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            details = edu.get('details', '').lower()
            resume_keywords.update(re.findall(r'\b\w{4,}\b', degree + ' ' + details))
        
        # Calculate matches
        matched_keywords = job_keywords.intersection(resume_keywords)
        missing_keywords = job_keywords - resume_keywords
        
        # Prioritize required skills
        matched_required_skills = set(required_skills).intersection(set(resume_skills))
        missing_required_skills = set(required_skills) - set(resume_skills)
        
        # Calculate score
        if len(job_keywords) > 0:
            keyword_match_percentage = (len(matched_keywords) / len(job_keywords)) * 100
        else:
            keyword_match_percentage = 0
        
        if len(required_skills) > 0:
            required_skills_percentage = (len(matched_required_skills) / len(required_skills)) * 100
        else:
            required_skills_percentage = 100  # No specific requirements
        
        # Weighted score (required skills are more important)
        score = (keyword_match_percentage * 0.4) + (required_skills_percentage * 0.6)
        
        return {
            'score': round(score, 1),
            'total_job_keywords': len(job_keywords),
            'matched_keywords': len(matched_keywords),
            'missing_keywords': len(missing_keywords),
            'matched_keywords_list': sorted(list(matched_keywords))[:20],  # Top 20
            'missing_keywords_list': sorted(list(missing_keywords))[:15],  # Top 15 to add
            'required_skills_matched': len(matched_required_skills),
            'required_skills_total': len(required_skills),
            'missing_required_skills': list(missing_required_skills),
            'keyword_density': self._calculate_keyword_density(resume_keywords, job_keywords)
        }
    
    def _calculate_keyword_density(self, resume_kw: set, job_kw: set) -> str:
        """Calculate keyword density rating."""
        if not job_kw:
            return "N/A"
        
        density = len(resume_kw.intersection(job_kw)) / len(job_kw)
        
        if density >= 0.7:
            return "Excellent"
        elif density >= 0.5:
            return "Good"
        elif density >= 0.3:
            return "Fair"
        else:
            return "Poor"
    
    def _check_format_compatibility(
        self, 
        resume_text: str, 
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if resume format is ATS-friendly."""
        
        issues = []
        warnings = []
        score = 100.0
        
        # Check for format red flags
        if resume_text:
            for issue_type, pattern in self.ats_red_flags.items():
                if re.search(pattern, resume_text, re.IGNORECASE):
                    if issue_type in ['tables', 'columns', 'text_boxes']:
                        issues.append(f"Contains {issue_type.replace('_', ' ')} which ATS may not parse correctly")
                        score -= 15
                    elif issue_type in ['headers_footers', 'images']:
                        warnings.append(f"Contains {issue_type.replace('_', ' ')} - information may be missed by ATS")
                        score -= 10
                    else:
                        warnings.append(f"Contains special characters that some ATS may not recognize")
                        score -= 5
        
        # Check for email and phone (critical contact info)
        personal_info = resume_data.get('personal_info', {})
        if not personal_info.get('email'):
            issues.append("Email address not found - critical for ATS")
            score -= 20
        if not personal_info.get('phone'):
            warnings.append("Phone number not found - recommended for ATS")
            score -= 10
        
        # Check skills section exists
        if not resume_data.get('skills'):
            issues.append("No skills section detected - ATS relies heavily on skills matching")
            score -= 25
        
        # Check experience section
        if not resume_data.get('experience'):
            warnings.append("No work experience section detected")
            score -= 15
        
        score = max(0, score)  # Ensure non-negative
        
        return {
            'score': score,
            'issues': issues,
            'warnings': warnings,
            'is_ats_friendly': score >= 70,
            'format_tips': self._get_format_tips(issues, warnings)
        }
    
    def _check_standard_sections(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if resume has standard ATS-recognizable sections."""
        
        found_sections = []
        missing_recommended = []
        
        # Check which sections exist
        if resume_data.get('personal_info'):
            found_sections.append('Contact Information')
        
        if resume_data.get('skills'):
            found_sections.append('Skills')
        else:
            missing_recommended.append('Skills')
        
        if resume_data.get('experience'):
            found_sections.append('Work Experience')
        else:
            missing_recommended.append('Work Experience')
        
        if resume_data.get('education'):
            found_sections.append('Education')
        else:
            missing_recommended.append('Education')
        
        # Optional but good sections
        if resume_data.get('certifications'):
            found_sections.append('Certifications')
        
        if resume_data.get('projects'):
            found_sections.append('Projects')
        
        # Calculate score
        required_sections = 4  # Contact, Skills, Experience, Education
        found_required = len([s for s in found_sections if s in ['Contact Information', 'Skills', 'Work Experience', 'Education']])
        
        score = (found_required / required_sections) * 100
        
        return {
            'score': score,
            'found_sections': found_sections,
            'missing_sections': missing_recommended,
            'section_count': len(found_sections),
            'has_all_required': len(missing_recommended) == 0
        }
    
    def _check_content_quality(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check quality of resume content for ATS."""
        
        score = 100.0
        issues = []
        strengths = []
        
        # Check for action verbs in experience
        experience = resume_data.get('experience', [])
        action_verb_count = 0
        
        for exp in experience:
            description = exp.get('description', '').lower()
            action_verb_count += sum(1 for verb in self.action_verbs if verb in description)
        
        if action_verb_count == 0 and experience:
            issues.append("No strong action verbs found in experience descriptions")
            score -= 20
        elif action_verb_count >= 5:
            strengths.append(f"Good use of action verbs ({action_verb_count} found)")
        
        # Check for quantifiable achievements
        quantifiable_count = 0
        for exp in experience:
            description = exp.get('description', '')
            # Look for numbers, percentages, metrics
            if re.search(r'\d+[%$]?|\d+\s*(percent|million|thousand|users|customers)', description):
                quantifiable_count += 1
        
        if quantifiable_count == 0 and experience:
            issues.append("No quantifiable achievements found - add metrics and numbers")
            score -= 15
        elif quantifiable_count >= 2:
            strengths.append(f"Contains quantifiable achievements ({quantifiable_count} found)")
        
        # Check skill count
        skills = resume_data.get('skills', [])
        if len(skills) < 5:
            issues.append(f"Too few skills listed ({len(skills)}) - aim for 10-15 relevant skills")
            score -= 15
        elif len(skills) > 30:
            issues.append(f"Too many skills listed ({len(skills)}) - focus on most relevant 15-20")
            score -= 10
        else:
            strengths.append(f"Good number of skills ({len(skills)})")
        
        # Check experience descriptions length
        short_descriptions = sum(1 for exp in experience if len(exp.get('description', '')) < 50)
        if short_descriptions > 0 and experience:
            issues.append(f"{short_descriptions} experience entries have brief descriptions - add more detail")
            score -= 10
        
        score = max(0, score)
        
        return {
            'score': score,
            'issues': issues,
            'strengths': strengths,
            'action_verb_count': action_verb_count,
            'quantifiable_achievements': quantifiable_count,
            'skill_count': len(skills)
        }
    
    def _generate_recommendations(
        self, 
        keyword_score: Dict,
        format_score: Dict,
        section_score: Dict,
        content_score: Dict,
        overall_score: float
    ) -> List[Dict[str, str]]:
        """Generate prioritized recommendations for ATS optimization."""
        
        recommendations = []
        
        # Critical: Missing keywords
        if keyword_score['score'] < 60:
            missing_req = keyword_score.get('missing_required_skills', [])
            if missing_req:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Keywords',
                    'issue': f"Missing {len(missing_req)} required skills",
                    'action': f"Add these required skills to your resume: {', '.join(missing_req[:5])}",
                    'impact': 'High - ATS will likely reject without these'
                })
            
            missing_kw = keyword_score.get('missing_keywords_list', [])[:5]
            if missing_kw:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Keywords',
                    'issue': 'Low keyword match with job description',
                    'action': f"Incorporate these keywords naturally: {', '.join(missing_kw)}",
                    'impact': 'High - Increases ATS ranking significantly'
                })
        
        # Critical: Format issues
        if format_score['score'] < 70:
            for issue in format_score.get('issues', []):
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Format',
                    'issue': issue,
                    'action': 'Use simple formatting: standard fonts, no tables, no text boxes',
                    'impact': 'Critical - ATS may not parse resume correctly'
                })
        
        # High: Missing sections
        if section_score['score'] < 100:
            missing = section_score.get('missing_sections', [])
            if missing:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Structure',
                    'issue': f"Missing standard sections: {', '.join(missing)}",
                    'action': f"Add {missing[0]} section with relevant information",
                    'impact': 'High - ATS expects these sections'
                })
        
        # Medium: Content quality
        if content_score['score'] < 80:
            for issue in content_score.get('issues', []):
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Content',
                    'issue': issue,
                    'action': 'Enhance descriptions with action verbs and measurable results',
                    'impact': 'Medium - Improves ATS scoring and readability'
                })
        
        # Low: Optimization tips
        if overall_score >= 70:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Optimization',
                'issue': 'Resume is ATS-compatible but can be improved',
                'action': 'Use exact job title phrases, add relevant certifications, include LinkedIn URL',
                'impact': 'Low - Fine-tuning for maximum ATS score'
            })
        
        return recommendations
    
    def _identify_critical_issues(
        self, 
        keyword_score: Dict, 
        format_score: Dict, 
        section_score: Dict
    ) -> List[str]:
        """Identify issues that will likely cause ATS rejection."""
        
        critical = []
        
        # Missing required skills = auto-reject
        missing_required = keyword_score.get('missing_required_skills', [])
        if len(missing_required) > 2:
            critical.append(f"Missing {len(missing_required)} required skills - likely auto-reject")
        
        # Format issues that prevent parsing
        if format_score['score'] < 50:
            critical.append("Severe formatting issues - ATS may not parse resume at all")
        
        # Missing critical sections
        if not section_score.get('has_all_required'):
            critical.append("Missing required sections - ATS cannot categorize information")
        
        # Very low keyword match
        if keyword_score['score'] < 40:
            critical.append("Extremely low keyword match - will rank at bottom of ATS")
        
        return critical
    
    def _estimate_pass_rate(self, score: float) -> Dict[str, Any]:
        """Estimate probability of passing ATS screening."""
        
        if score >= 85:
            return {
                'percentage': '90-95%',
                'label': 'Excellent',
                'description': 'Very likely to pass ATS and reach human reviewer'
            }
        elif score >= 70:
            return {
                'percentage': '70-85%',
                'label': 'Good',
                'description': 'Good chance of passing ATS screening'
            }
        elif score >= 55:
            return {
                'percentage': '40-60%',
                'label': 'Fair',
                'description': 'May pass ATS but improvements recommended'
            }
        elif score >= 40:
            return {
                'percentage': '20-35%',
                'label': 'Poor',
                'description': 'Low chance of passing - significant improvements needed'
            }
        else:
            return {
                'percentage': '5-15%',
                'label': 'Very Poor',
                'description': 'Unlikely to pass ATS - major revisions required'
            }
    
    def _get_ats_category(self, score: float) -> str:
        """Get ATS compatibility category."""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Very Poor"
    
    def _get_format_tips(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Get specific formatting tips based on detected issues."""
        
        tips = []
        
        if any('table' in issue.lower() for issue in issues + warnings):
            tips.append("Replace tables with simple bullet points or line breaks")
        
        if any('column' in issue.lower() for issue in issues + warnings):
            tips.append("Use single-column layout for maximum ATS compatibility")
        
        if any('text box' in issue.lower() for issue in issues + warnings):
            tips.append("Remove text boxes - place content in main document flow")
        
        if any('header' in issue.lower() or 'footer' in issue.lower() for issue in issues + warnings):
            tips.append("Move contact info from headers/footers to main document body")
        
        if any('special character' in issue.lower() for issue in issues + warnings):
            tips.append("Use standard characters: bullets (•), dashes (-), asterisks (*)")
        
        if not tips:
            tips.append("Use standard fonts (Arial, Calibri, Times New Roman)")
            tips.append("Stick to .PDF or .DOCX file formats")
            tips.append("Use standard section headers (Experience, Education, Skills)")
        
        return tips
    
    def optimize_cover_letter_for_ats(
        self, 
        cover_letter: str, 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize cover letter for ATS compatibility."""
        
        required_skills = [s.lower() for s in job_data.get('required_skills', [])]
        job_title = job_data.get('title', '').lower()
        
        # Check if cover letter includes key elements
        cl_lower = cover_letter.lower()
        
        issues = []
        score = 100.0
        
        # Check for job title mention
        if job_title and job_title not in cl_lower:
            issues.append(f"Cover letter doesn't mention job title: '{job_data.get('title')}'")
            score -= 20
        
        # Check for required skills
        skills_mentioned = sum(1 for skill in required_skills if skill in cl_lower)
        skills_missing = len(required_skills) - skills_mentioned
        
        if skills_missing > len(required_skills) * 0.5:
            issues.append(f"Only {skills_mentioned}/{len(required_skills)} required skills mentioned")
            score -= 25
        
        # Check length (ATS may truncate very long cover letters)
        word_count = len(cover_letter.split())
        if word_count > 600:
            issues.append(f"Cover letter too long ({word_count} words) - aim for 250-400 words")
            score -= 10
        elif word_count < 150:
            issues.append(f"Cover letter too short ({word_count} words) - add more detail")
            score -= 15
        
        score = max(0, score)
        
        return {
            'score': score,
            'issues': issues,
            'skills_mentioned': skills_mentioned,
            'skills_total': len(required_skills),
            'word_count': word_count,
            'recommended_additions': [skill for skill in required_skills if skill not in cl_lower][:5]
        }
