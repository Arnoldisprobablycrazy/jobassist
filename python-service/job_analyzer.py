# python-service/job_analyzer.py
import re
import json
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class JobAnalyzer:
    def __init__(self):
        # Expanded skill patterns for job descriptions
        self.skill_patterns = [
            # Programming Languages
            r'\b(python|java(?:script)?|typescript|c\+\+|c#|go|rust|swift|kotlin|r|ruby|php|perl|scala|dart)\b',
            # Frameworks & Libraries
            r'\b(react(?:\.js)?|angular|vue(?:\.js)?|next\.js|nuxt\.js|svelte|jquery|django|flask|spring|laravel|rails|express(?:\.js)?)\b',
            # Technologies
            r'\b(html5?|css3?|sass|less|bootstrap|tailwind|node\.js|graphql|rest\s+api|websocket|webpack|babel)\b',
            # Databases
            r'\b(mysql|postgresql|mongodb|redis|sqlite|oracle|sql\s+server|dynamodb|cassandra|elasticsearch|firebase)\b',
            # Cloud & DevOps
            r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible|jenkins|git|github|gitlab|ci/cd|devops)\b',
            # Data & AI
            r'\b(pandas|numpy|scikit-learn|tensorflow|pytorch|keras|opencv|nltk|spacy|tableau|power\s+bi|machine\s+learning|deep\s+learning)\b',
            # Mobile
            r'\b(react\s+native|flutter|android|ios|xcode|android\s+studio)\b',
            # Testing
            r'\b(jest|mocha|chai|cypress|selenium|junit|pytest|unittest)\b',
            # Methodologies
            r'\b(agile|scrum|kanban|waterfall)\b',
            # Soft Skills
            r'\b(communication|leadership|teamwork|problem.solving|critical\s+thinking|creativity|adaptability)\b',
            r'\b(time\s+management|collaboration|presentation|negotiation|project\s+management|analytical\s+skills)\b'
        ]

    def extract_required_skills(self, text: str) -> List[str]:
        """Extract skills dynamically from job description"""
        skills = set()
        text_lower = text.lower()
        
        # Pattern matching
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean and format the skill
                skill = self.clean_skill(match)
                if skill:
                    skills.add(skill)
        
        # Look for skills in requirements sections
        requirements_sections = self.extract_requirements_sections(text)
        for section in requirements_sections:
            section_matches = re.findall(r'\b(\w+(?:\s+\w+){0,2})\b', section.lower())
            for term in section_matches:
                for pattern in self.skill_patterns:
                    if re.search(pattern, term):
                        skill = self.clean_skill(term)
                        if skill:
                            skills.add(skill)
        
        return sorted(list(skills), key=lambda x: x.lower())

    def clean_skill(self, skill: str) -> str:
        """Clean and format skill names"""
        skill = skill.strip()
        
        # Common normalizations
        replacements = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'c++': 'C++',
            'c#': 'C#',
            'node.js': 'Node.js',
            'react.js': 'React',
            'vue.js': 'Vue.js',
            'next.js': 'Next.js',
            'nuxt.js': 'Nuxt.js',
            'express.js': 'Express.js',
            'html5': 'HTML',
            'css3': 'CSS',
            'sql server': 'SQL Server',
            'rest api': 'REST API',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'react native': 'React Native',
            'android studio': 'Android Studio',
            'power bi': 'Power BI',
            'time management': 'Time Management',
            'problem solving': 'Problem Solving',
            'critical thinking': 'Critical Thinking',
            'project management': 'Project Management'
        }
        
        skill = replacements.get(skill.lower(), skill.title())
        return skill

    def extract_requirements_sections(self, text: str) -> List[str]:
        """Extract sections that likely contain requirements"""
        sections = []
        lines = text.split('\n')
        
        requirement_keywords = [
            'requirements', 'qualifications', 'skills required', 'must have',
            'required skills', 'we are looking for', 'you should have',
            'technical skills', 'what you bring'
        ]
        
        current_section = []
        in_requirements = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in requirement_keywords):
                if current_section:
                    sections.append(' '.join(current_section))
                current_section = [line]
                in_requirements = True
            elif in_requirements and line.strip():
                current_section.append(line)
            elif in_requirements and not line.strip():
                # Empty line might end the section
                if current_section:
                    sections.append(' '.join(current_section))
                current_section = []
                in_requirements = False
        
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections

    def extract_experience_level(self, text: str) -> str:
        """Extract required experience level from job description"""
        text_lower = text.lower()
        
        # Senior level indicators
        senior_indicators = [
            'senior', 'lead', 'principal', 'staff', '5+ years', '5 years', '5+', 
            '6+ years', '7+ years', '8+ years', '10+ years', 'experienced', 'expert'
        ]
        
        # Mid-level indicators
        mid_indicators = [
            'mid-level', 'mid level', '3+ years', '3 years', '4+ years', '4 years',
            '2-5 years', '3-5 years', 'intermediate'
        ]
        
        # Junior level indicators
        junior_indicators = [
            'junior', 'entry level', 'entry-level', '0-2 years', '1-2 years', 
            '0-1 years', 'recent graduate', 'new graduate', 'fresher', 'associate'
        ]
        
        # Check for senior level first (most specific)
        if any(indicator in text_lower for indicator in senior_indicators):
            return 'Senior'
        elif any(indicator in text_lower for indicator in mid_indicators):
            return 'Mid-Level'
        elif any(indicator in text_lower for indicator in junior_indicators):
            return 'Junior'
        else:
            return 'Not Specified'

    def extract_job_title(self, text: str) -> str:
        """Extract job title from description"""
        lines = text.split('\n')
        
        # Common job title patterns
        title_patterns = [
            r'^(senior|junior|lead|principal)?\s*(software|frontend|backend|full\s*stack|web|mobile)\s+(developer|engineer)',
            r'^(data scientist|data analyst|devops engineer|product manager|project manager|ui/ux designer|ux/ui designer)',
            r'^(machine learning engineer|ml engineer|ai engineer|cloud engineer|solutions architect)',
            r'^(business analyst|systems analyst|qa engineer|test engineer|quality assurance)',
            r'^(technical lead|team lead|engineering manager|cto|technical director)'
        ]
        
        # Check first few lines for job title
        for line in lines[:10]:  # Check first 10 lines
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Look for common title patterns
            for pattern in title_patterns:
                match = re.search(pattern, line_clean.lower())
                if match:
                    return line_clean
            
            # If line is short and looks like a title
            if (len(line_clean) < 50 and 
                not any(word in line_clean.lower() for word in ['company', 'location', 'salary', 'apply']) and
                re.match(r'^[A-Z][a-zA-Z\s&]+$', line_clean)):
                return line_clean
        
        # Fallback: extract from the beginning of the description
        first_line = lines[0].strip() if lines else ""
        if len(first_line) < 100 and first_line:
            return first_line
        
        return "Position Not Specified"

    def extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from job description"""
        responsibilities = []
        lines = text.split('\n')
        
        responsibility_keywords = [
            'responsibilities', 'duties', 'what you will do', 'key responsibilities',
            'role and responsibilities', 'you will', 'your role'
        ]
        
        current_section = []
        in_responsibilities = False
        
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            if any(keyword in line_lower for keyword in responsibility_keywords):
                if current_section:
                    responsibilities.extend(self.clean_responsibilities(current_section))
                current_section = []
                in_responsibilities = True
                continue
            
            if in_responsibilities and line_clean:
                # Check if we're moving to a new section
                if any(section in line_lower for section in ['requirements', 'qualifications', 'skills', 'education']):
                    break
                
                current_section.append(line_clean)
            elif in_responsibilities and not line_clean and current_section:
                # Empty line might end the section
                responsibilities.extend(self.clean_responsibilities(current_section))
                current_section = []
                in_responsibilities = False
        
        if current_section:
            responsibilities.extend(self.clean_responsibilities(current_section))
        
        # If no specific responsibilities section found, extract from bullet points
        if not responsibilities:
            responsibilities = self.extract_bullet_points(text)
        
        return responsibilities[:8]  # Return top 8 responsibilities

    def clean_responsibilities(self, lines: List[str]) -> List[str]:
        """Clean and format responsibility lines"""
        cleaned = []
        current_item = ""
        
        for line in lines:
            line_clean = line.strip()
            
            # Skip empty lines and section headers
            if not line_clean or any(keyword in line_clean.lower() for keyword in ['responsibilities', 'duties']):
                continue
            
            # Check if this is a new bullet point
            if re.match(r'^[•·\-–—*\d\.]', line_clean):
                if current_item:
                    cleaned.append(current_item.strip())
                current_item = re.sub(r'^[•·\-–—*\d\.\s]+', '', line_clean)
            else:
                # Continue the current item
                current_item += " " + line_clean
        
        if current_item:
            cleaned.append(current_item.strip())
        
        return cleaned

    def extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        bullet_points = []
        lines = text.split('\n')
        
        for line in lines:
            line_clean = line.strip()
            # Look for bullet points and numbered lists
            if re.match(r'^[•·\-–—*\d\.]', line_clean):
                cleaned = re.sub(r'^[•·\-–—*\d\.\s]+', '', line_clean)
                if len(cleaned) > 10 and len(cleaned) < 200:  # Reasonable length
                    bullet_points.append(cleaned)
        
        return bullet_points[:6]

    def extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications and requirements"""
        qualifications = []
        lines = text.split('\n')
        
        qualification_keywords = [
            'qualifications', 'requirements', 'must have', 'required',
            'we require', 'you must have', 'essential', 'minimum qualifications'
        ]
        
        education_keywords = [
            'bachelor', "bachelor's", 'master', "master's", 'phd', 'doctorate',
            'degree', 'diploma', 'certification', 'b\.s\.', 'b\.a\.', 'm\.s\.', 'm\.a\.'
        ]
        
        current_section = []
        in_qualifications = False
        
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            if any(keyword in line_lower for keyword in qualification_keywords):
                if current_section:
                    qualifications.extend(self.clean_qualifications(current_section))
                current_section = []
                in_qualifications = True
                continue
            
            if in_qualifications and line_clean:
                # Check if we're moving to a different section
                if any(section in line_lower for section in ['responsibilities', 'duties', 'benefits', 'compensation']):
                    break
                
                current_section.append(line_clean)
            elif in_qualifications and not line_clean and current_section:
                qualifications.extend(self.clean_qualifications(current_section))
                current_section = []
                in_qualifications = False
        
        if current_section:
            qualifications.extend(self.clean_qualifications(current_section))
        
        # Also look for education requirements specifically
        education_requirements = self.extract_education_requirements(text)
        qualifications.extend(education_requirements)
        
        return list(set(qualifications))[:5]  # Remove duplicates and return top 5

    def clean_qualifications(self, lines: List[str]) -> List[str]:
        """Clean and format qualification lines"""
        cleaned = []
        
        for line in lines:
            line_clean = line.strip()
            # Skip section headers and very short lines
            if (len(line_clean) < 5 or 
                any(keyword in line_clean.lower() for keyword in ['qualifications', 'requirements'])):
                continue
            
            # Clean bullet points and numbering
            cleaned_line = re.sub(r'^[•·\-–—*\d\.\s]+', '', line_clean)
            if len(cleaned_line) > 8:  # Minimum reasonable length
                cleaned.append(cleaned_line)
        
        return cleaned

    def extract_education_requirements(self, text: str) -> List[str]:
        """Extract education-specific requirements"""
        education_requirements = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            # Look for education requirements
            if any(keyword in line_lower for keyword in ['bachelor', 'master', 'phd', 'degree', 'diploma']):
                # Check if this is actually an education requirement
                if any(edu_indicator in line_lower for edu_indicator in 
                       ['in computer science', 'in engineering', 'or equivalent', 'required', 'preferred']):
                    education_requirements.append(line.strip())
        
        return education_requirements

    def extract_company_name(self, text: str) -> str:
        """Extract company name from job description"""
        lines = text.split('\n')
        
        # Common company indicators
        company_indicators = ['at', 'company:', 'organization:', 'firm:']
        
        for line in lines[:5]:  # Check first 5 lines
            line_clean = line.strip()
            for indicator in company_indicators:
                if indicator in line_clean.lower():
                    # Extract company name after the indicator
                    parts = line_clean.split(indicator, 1)
                    if len(parts) > 1:
                        company = parts[1].strip()
                        # Clean up the company name
                        company = re.sub(r'[^\w\s&]', '', company)
                        if company and len(company) < 50:
                            return company
        
        # Fallback: look for capitalized words that might be company names
        for line in lines[:3]:
            words = line.strip().split()
            if len(words) == 1 and words[0].istitle() and len(words[0]) > 2:
                return words[0]
        
        return "Company Not Specified"

    def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """Main job description analysis function"""
        try:
            analysis = {
                'required_skills': self.extract_required_skills(job_text),
                'experience_level': self.extract_experience_level(job_text),
                'job_title': self.extract_job_title(job_text),
                'company': self.extract_company_name(job_text),
                'key_responsibilities': self.extract_responsibilities(job_text),
                'qualifications': self.extract_qualifications(job_text),
                'description': job_text[:500] + "..." if len(job_text) > 500 else job_text  # Truncate long descriptions
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Job analysis failed: {str(e)}")

class SimilarityCalculator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_similarity(self, resume_text: str, job_text: str) -> Dict[str, float]:
        """Calculate similarity between resume and job description"""
        try:
            # Combine texts for vectorization
            documents = [resume_text, job_text]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            overall_similarity = float(similarity_matrix[0][0]) * 100
            
            # Calculate skill-based similarity
            skill_similarity = self.calculate_skill_similarity(resume_text, job_text)
            
            # Calculate keyword overlap
            keyword_similarity = self.calculate_keyword_similarity(resume_text, job_text)
            
            return {
                'overall_score': round(overall_similarity, 2),
                'skill_match_score': round(skill_similarity, 2),
                'experience_match_score': round(overall_similarity * 0.8, 2),
                'keyword_match_score': round(keyword_similarity, 2)
            }
            
        except Exception as e:
            raise Exception(f"Similarity calculation failed: {str(e)}")
    
    def calculate_skill_similarity(self, resume_text: str, job_text: str) -> float:
        """Calculate skill-based similarity using the job analyzer"""
        try:
            job_analyzer = JobAnalyzer()
            resume_skills = job_analyzer.extract_required_skills(resume_text)
            job_skills = job_analyzer.extract_required_skills(job_text)
            
            if not job_skills:
                return 0.0
            
            # Calculate Jaccard similarity for skills
            resume_skills_set = set(resume_skills)
            job_skills_set = set(job_skills)
            
            if not job_skills_set:
                return 0.0
            
            intersection = len(resume_skills_set.intersection(job_skills_set))
            union = len(resume_skills_set.union(job_skills_set))
            
            similarity = (intersection / union) * 100 if union > 0 else 0.0
            return min(similarity, 100.0)
            
        except Exception as e:
            print(f"Skill similarity calculation error: {e}")
            return 0.0
    
    def calculate_keyword_similarity(self, resume_text: str, job_text: str) -> float:
        """Calculate keyword overlap similarity"""
        try:
            # Extract words from both texts
            resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
            job_words = set(re.findall(r'\b\w+\b', job_text.lower()))
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            resume_words = resume_words - stop_words
            job_words = job_words - stop_words
            
            if not job_words:
                return 0.0
            
            # Calculate overlap
            common_words = resume_words.intersection(job_words)
            similarity = (len(common_words) / len(job_words)) * 100
            
            return min(similarity, 100.0)
            
        except Exception as e:
            print(f"Keyword similarity calculation error: {e}")
            return 0.0