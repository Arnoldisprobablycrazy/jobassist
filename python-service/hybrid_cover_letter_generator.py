# python-service/hybrid_cover_letter_generator.py
import re
from typing import Dict, List

class HybridCoverLetterGenerator:
    def __init__(self):
        self.templates = {
            'professional': self._professional_template,
            'enthusiastic': self._enthusiastic_template,
            'formal': self._formal_template
        }
    
    def generate_cover_letter(self, resume_data: Dict, job_data: Dict, tone: str = 'professional') -> str:
        """Generate cover letter using template + smart filling"""
        template_func = self.templates.get(tone, self._professional_template)
        return template_func(resume_data, job_data)
    
    def _professional_template(self, resume_data: Dict, job_data: Dict) -> str:
        name = resume_data.get('personal_info', {}).get('name', 'Applicant')
        email = resume_data.get('personal_info', {}).get('email', '')
        phone = resume_data.get('personal_info', {}).get('phone', '')
        
        skills = self._match_skills(resume_data, job_data)
        experience = self._get_relevant_experience(resume_data, job_data)
        
        return f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_data.get('job_title', 'position')} role at {job_data.get('company', 'your company')}. With my background in {', '.join(skills[:3])}, I am confident that I possess the qualifications necessary to excel in this position.

{experience}

I was particularly impressed by {job_data.get('company', 'your company')}'s focus on {self._extract_company_focus(job_data)} and believe my skills in {skills[0] if skills else 'this field'} would allow me to contribute significantly to your team.

Thank you for considering my application. I have attached my resume for your review and welcome the opportunity to discuss how my experience and skills can benefit {job_data.get('company', 'your company')}.

Sincerely,
{name}

{email} | {phone}
"""
    
    def _match_skills(self, resume_data: Dict, job_data: Dict) -> List[str]:
        """Find skills that match between resume and job"""
        resume_skills = set(resume_data.get('skills', []))
        job_skills = set(job_data.get('required_skills', []))
        
        # Exact matches first
        matches = list(resume_skills.intersection(job_skills))
        
        # Then partial matches
        for r_skill in resume_skills:
            for j_skill in job_skills:
                if r_skill.lower() in j_skill.lower() or j_skill.lower() in r_skill.lower():
                    if r_skill not in matches:
                        matches.append(r_skill)
        
        return matches if matches else resume_data.get('skills', [])[:3]
    
    def _get_relevant_experience(self, resume_data: Dict, job_data: Dict) -> str:
        """Extract relevant experience summary"""
        experience = resume_data.get('experience', [])
        if not experience:
            return "My professional experience has provided me with strong skills relevant to this position."
        
        # Find experience that matches job keywords
        job_text = ' '.join(job_data.get('key_responsibilities', [])).lower()
        for exp in experience:
            exp_text = exp.get('description', '').lower()
            # Simple keyword matching
            common_words = set(exp_text.split()) & set(job_text.split())
            if len(common_words) > 2:  # If at least 3 common words
                return f"In my previous role as {exp.get('title', 'a professional')}, I {exp.get('description', 'gained relevant experience')}."
        
        return f"In my previous role as {experience[0].get('title', 'a professional')}, I developed skills that align well with this position."
    
    def _extract_company_focus(self, job_data: Dict) -> str:
        """Extract company focus from job description"""
        desc = job_data.get('description', '')
        # Look for company values or focus areas
        focus_keywords = ['innovation', 'technology', 'quality', 'customer', 'growth', 'excellence']
        for keyword in focus_keywords:
            if keyword in desc.lower():
                return keyword
        return "excellence and innovation"