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

    def validate_is_job_description(self, text: str) -> Dict[str, Any]:
        """
        Validate if the provided text is actually a job description/posting.
        Returns validation result with boolean and error message if invalid.
        """
        if not text or len(text.strip()) < 100:
            return {
                'is_valid': False,
                'error': 'Job description is too short. Please provide a complete job posting.'
            }
        
        text_lower = text.lower()
        
        # Job posting indicators - should have at least 1-2 of these (very lenient)
        job_indicators = [
            'responsibilities', 'requirements', 'qualifications', 'job description',
            'role', 'position', 'duties', 'hiring', 'seeking', 'looking for',
            'we are', 'join our team', 'apply', 'salary', 'compensation',
            'benefits', 'work environment', 'company culture', 'reports to',
            'years of experience', 'experience required', 'preferred qualifications',
            'nice to have', 'must have', 'job type', 'employment type',
            'full time', 'part time', 'contract', 'remote', 'on-site', 'hybrid',
            'application deadline', 'about the company', 'about us', 'our mission',
            'key responsibilities', 'what you will do', 'vacancy', 'job opening',
            'employment', 'career opportunity', 'teaching', 'instructor', 'professor',
            'internship', 'intern', 'applicants', 'candidates', 'opportunity',
            'department', 'organization', 'brief description', 'detailed description',
            'eligibility', 'criteria', 'why join', 'skills', 'gain experience'
        ]
        
        job_indicator_count = sum(1 for indicator in job_indicators if indicator in text_lower)
        
        # Very lenient - just need 1 clear indicator (was 2)
        if job_indicator_count < 1:
            return {
                'is_valid': False,
                'error': 'This does not appear to be a job description. Please upload a valid job posting.'
            }
        
        # Check for resume indicators - should NOT be a resume
        # Only check for VERY strong resume-specific indicators that would NEVER appear in job descriptions
        resume_indicators = [
            'curriculum vitae', 'my objective:', 'my career objective',
            'my professional summary:', 'my work history:', 'my employment history:',
            'personal information:', 'date of birth:', 'nationality:', 'marital status:',
            'references available upon request',
            'linkedin.com/in/', 'github.com/',
            'i have worked at', 'i am a', 'my experience includes', 'my skills include',
            'personal statement:', 'about me:'
        ]
        
        resume_indicator_count = sum(1 for indicator in resume_indicators if indicator in text_lower)
        
        # Very lenient - need at least 6 strong indicators to reject (was 5)
        # This prevents false positives on job descriptions that mention "skills" or "experience"
        if resume_indicator_count >= 6:
            return {
                'is_valid': False,
                'error': 'This appears to be a resume, not a job description. Please upload a job posting.'
            }
        
        # Check for other document types to exclude - VERY specific to avoid false positives
        # Job postings often ask applicants to submit transcripts, certificates, etc.
        # Only reject if document ITSELF is one of these types (not just mentions them in requirements)
        exclude_keywords = [
            'official grade report for', 'official mark sheet for', 'official academic record for',
            'official certificate of completion for',
            'invoice number:', 'receipt number:', 'bill number:', 'official bank statement',
            'official financial statement for', 'payment confirmation for',
            'official medical report for', 'official lab report for', 'prescription for patient:',
            'legal document number:', 'contract agreement between'
        ]
        
        exclude_count = sum(1 for keyword in exclude_keywords if keyword in text_lower)
        
        # Also check for transcript but only if it's CLEARLY the document itself
        # Job postings often ask for "submit your transcript" - that's fine
        transcript_phrases = [
            'this is my transcript', 'official transcript for student:', 'grade transcript for:',
            'academic transcript document for student:'
        ]
        has_transcript_doc = any(phrase in text_lower for phrase in transcript_phrases)
        if has_transcript_doc:
            exclude_count += 1
        
        # Need at least 3 strong indicators to reject (was 2) - very conservative
        if exclude_count >= 3:
            return {
                'is_valid': False,
                'error': 'This does not appear to be a job description. Please upload a valid job posting.'
            }
        
        # Check if text has too many numbers (likely a transcript or statement)
        numeric_chars = sum(c.isdigit() for c in text)
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        if total_chars > 0:
            numeric_ratio = numeric_chars / total_chars
            # Very lenient - job postings can have phone numbers, dates, salaries, years, etc.
            # Only reject if it's REALLY dominated by numbers (like a grade sheet)
            if numeric_ratio > 0.5:  # More than 50% numbers (was 40%)
                return {
                    'is_valid': False,
                    'error': 'Document contains too many numbers. Please upload a job description, not a transcript or statement.'
                }
        
        # All validation checks passed
        return {
            'is_valid': True,
            'error': None
        }

    def extract_required_skills(self, text: str) -> List[str]:
        """Extract skills dynamically from job description"""
        skills = set()
        
        # Preprocess: remove contact info and noisy tokens (emails, urls, phone numbers, company names)
        cleaned_text = re.sub(r'\S+@\S+', ' ', text)  # remove emails
        cleaned_text = re.sub(r'http[s]?://\S+|www\.\S+', ' ', cleaned_text)  # remove urls
        cleaned_text = re.sub(r'\+?\d[\d\s\-\(\)]{6,}\d', ' ', cleaned_text)  # remove phone-like sequences
        
        # Pattern matching on cleaned text
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, cleaned_text.lower())
            for match in matches:
                # Handle tuple results from grouped regex
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                # Clean and format the skill
                skill = self.clean_skill(match)
                if skill and self.looks_like_skill(skill):
                    skills.add(skill)
        
        # Look for skills in requirements sections
        requirements_sections = self.extract_requirements_sections(cleaned_text)
        for section in requirements_sections:
            # Skip lines with contact info or URLs
            if '@' in section or 'http' in section or 'www.' in section:
                continue
            
            # Split by common separators for more granular extraction
            skill_items = re.split(r'[,:;/•\-–—>|\\]', section)
            for item in skill_items:
                item = item.strip()
                if not item or len(item) < 2 or len(item) > 60:
                    continue
                # Remove prefixes like "required:", "skills:", etc.
                item = re.sub(r'^(required|skills|technical|experience|knowledge)[:\-\s]+', '', item, flags=re.I)
                item = re.sub(r'\([^\)]*\)', '', item).strip()
                
                # Check if it matches skill patterns
                for pattern in self.skill_patterns:
                    if re.search(pattern, item.lower()):
                        skill = self.clean_skill(item)
                        if skill and self.looks_like_skill(skill):
                            skills.add(skill)
                        break
        
        # Final filtering: remove common non-skill tokens
        final_skills = []
        excluded_terms = {
            'united states', 'usa', 'uk', 'united kingdom', 'canada', 'germany', 'france', 'india',
            'china', 'nigeria', 'brazil', 'russia', 'australia', 'new york', 'san francisco',
            'london', 'remote', 'hybrid', 'onsite'
        }
        for s in skills:
            s_low = s.lower()
            # Exclude countries, cities, work locations
            if any(ex in s_low for ex in excluded_terms):
                continue
            # Exclude tokens with numbers (likely years, addresses, salaries)
            if re.search(r'\d{2,}', s_low):
                continue
            # Exclude contact-related tokens
            if any(tok in s_low for tok in ['email', 'phone', 'linkedin', 'github', 'www', 'http', 'apply']):
                continue
            # Exclude company/role descriptors
            if any(tok in s_low for tok in ['company', 'position', 'role', 'salary', 'benefits']):
                continue
            final_skills.append(s)
        
        return sorted(list(set(final_skills)), key=lambda x: x.lower())

    def clean_skill(self, skill: str) -> str:
        """Clean and format skill names"""
        skill = skill.strip()
        
        # Remove common prefixes and qualifiers
        skill = re.sub(r'^(strong|expert|proficiency\s+in|experience\s+with|knowledge\s+of)\s+', '', skill, flags=re.I)
        skill = re.sub(r'^(required|preferred|must\s+have)[:\-\s]+', '', skill, flags=re.I)
        # Remove trailing words
        skill = re.sub(r'\s+(required|preferred|experience|years?)$', '', skill, flags=re.I)
        # Remove parenthetical content
        skill = re.sub(r'\([^\)]*\)', '', skill).strip()
        skill = ' '.join(skill.split())
        
        # Normalize acronyms and common tech names
        def normalize_token(tok: str) -> str:
            if tok.lower() in {'api', 'css', 'html', 'sql', 'nosql', 'aws', 'gcp', 'gpu', 'cpu', 'ci/cd', 'rest', 'graphql'}:
                return tok.upper()
            if re.match(r'^[a-z]+\.[a-z]+$', tok.lower()):  # e.g., node.js, vue.js
                return tok.lower()
            return tok.title()
        
        parts = skill.split()
        parts = [normalize_token(p) for p in parts]
        skill = ' '.join(parts)
        
        # Common normalizations
        replacements = {
            'Javascript': 'JavaScript',
            'Typescript': 'TypeScript',
            'C++': 'C++',
            'C#': 'C#',
            'Node.Js': 'Node.js',
            'React.Js': 'React',
            'Vue.Js': 'Vue.js',
            'Next.Js': 'Next.js',
            'Nuxt.Js': 'Nuxt.js',
            'Express.Js': 'Express.js',
            'Html': 'HTML',
            'Html5': 'HTML',
            'Css': 'CSS',
            'Css3': 'CSS',
            'Sql Server': 'SQL Server',
            'Rest Api': 'REST API',
            'Machine Learning': 'Machine Learning',
            'Deep Learning': 'Deep Learning',
            'React Native': 'React Native',
            'Android Studio': 'Android Studio',
            'Power Bi': 'Power BI',
            'Time Management': 'Time Management',
            'Problem Solving': 'Problem Solving',
            'Critical Thinking': 'Critical Thinking',
            'Project Management': 'Project Management',
            'Ci/Cd': 'CI/CD'
        }
        
        skill = replacements.get(skill, skill)
        
        # Final guard: remove empty or too-short results
        if not skill or len(skill) < 2:
            return ''
        return skill
    
    def looks_like_skill(self, word: str) -> bool:
        """Check if a word looks like a technical skill or valid requirement"""
        word_lower = word.lower().strip()
        
        # Quick exclusions
        if not word_lower or len(word_lower) < 2 or len(word_lower) > 60:
            return False
        if any(tok in word_lower for tok in ['@', 'http', 'www', 'email', 'phone', 'apply']):
            return False
        
        # Exclude numeric-heavy tokens (likely years, salaries, addresses)
        if re.search(r'\d{2,}', word_lower) and not re.search(r'(c\+\+|c#|html5|css3)', word_lower):
            return False
        
        # Common non-skill words to exclude
        excluded_words = {
            'company', 'position', 'role', 'location', 'remote', 'hybrid', 'onsite',
            'salary', 'benefits', 'compensation', 'employer', 'job', 'opportunity',
            'candidate', 'applicant', 'team', 'office', 'work', 'full-time', 'part-time',
            'contract', 'permanent', 'temporary', 'immediate', 'start', 'date',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december'
        }
        if word_lower in excluded_words:
            return False
        
        # Exclude long sentence-like fragments or verb-driven phrases
        if len(word_lower.split()) > 4:
            return False
        if re.search(r'\b(will|must|should|looking|seeking|hiring|join|offer|provide)\b', word_lower):
            return False
        
        # Check if it matches any of our skill patterns
        for pattern in self.skill_patterns:
            if re.search(pattern, word_lower):
                return True
        
        # Check for tech indicators (.js, .net, SQL, API, etc.)
        if re.search(r'\.[a-z]{2,5}$', word_lower) or re.search(r'\b(api|sql|aws|gcp|html|css)\b', word_lower):
            return True
        
        # Reject otherwise (avoid generic nouns and company jargon)
        return False

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
        """Extract job title from description - works for all career fields"""
        lines = text.split('\n')
        
        # Priority 1: Look for explicit job title indicators
        position_indicators = [
            r'^POSITION:\s*(.+)$',
            r'^JOB TITLE:\s*(.+)$',
            r'^ROLE:\s*(.+)$',
            r'^TITLE:\s*(.+)$',
            r'^POSITION\s+TITLE:\s*(.+)$',
            r'^JOB:\s*(.+)$',
            r'^OPENING:\s*(.+)$',
            r'^VACANCY:\s*(.+)$'
        ]
        
        for line in lines[:20]:
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Check for explicit position indicators
            for pattern in position_indicators:
                match = re.search(pattern, line_clean, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Clean up the title, preserve important characters
                    title = re.sub(r'[^\w\s/&()-]', '', title)
                    if len(title) > 2 and not self._is_header_or_company(title):
                        return title
        
        # Priority 2: Common job-related keywords (career-agnostic)
        # These words commonly appear in job titles across all industries
        job_keywords = [
            # Seniority levels
            r'\b(senior|junior|lead|principal|chief|head|assistant|associate|entry.level)\b',
            # Professional titles
            r'\b(manager|director|coordinator|supervisor|specialist|analyst|consultant|officer|administrator)\b',
            # Technical/Engineering
            r'\b(engineer|developer|architect|technician|programmer|analyst)\b',
            # Education
            r'\b(teacher|instructor|professor|educator|lecturer|tutor|counselor)\b',
            # Healthcare
            r'\b(nurse|physician|doctor|surgeon|therapist|pharmacist|clinician|practitioner)\b',
            # Creative/Design
            r'\b(designer|artist|creative|writer|editor|photographer|illustrator)\b',
            # Sales/Marketing
            r'\b(sales|marketing|account|business\s+development|representative)\b',
            # Finance/Accounting
            r'\b(accountant|auditor|financial|analyst|controller|treasurer)\b',
            # Legal
            r'\b(attorney|lawyer|counsel|paralegal|legal)\b',
            # Operations
            r'\b(operations|logistics|supply\s+chain|procurement)\b',
            # HR/Recruitment
            r'\b(human\s+resources|recruiter|talent|hr)\b',
            # Hospitality/Service
            r'\b(chef|cook|server|receptionist|concierge|host)\b',
            # Trades/Skilled
            r'\b(electrician|plumber|carpenter|mechanic|technician)\b'
        ]
        
        # Priority 3: Look for lines containing job-related keywords
        for line in lines[:20]:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 5 or len(line_clean) > 100:
                continue
            
            # Skip section headers and obvious non-title lines
            skip_keywords = ['about', 'location:', 'salary:', 'compensation:', 'deadline:', 
                           'start date:', 'employment type:', 'vacancy announcement', 
                           'job description', 'responsibilities:', 'qualifications:',
                           'requirements:', 'benefits:', 'how to apply', 'apply by']
            if any(keyword in line_clean.lower() for keyword in skip_keywords):
                continue
            
            # Skip all-caps lines that look like section headers
            if line_clean.isupper() and len(line_clean.split()) <= 4:
                if any(word in line_clean for word in ['ABOUT', 'DESCRIPTION', 'REQUIREMENTS', 'QUALIFICATIONS']):
                    continue
            
            # Check if line contains job-related keywords
            line_lower = line_clean.lower()
            for keyword_pattern in job_keywords:
                if re.search(keyword_pattern, line_lower):
                    # Found a potential job title
                    # Validate it's not a company name or generic text
                    if not self._is_header_or_company(line_clean):
                        return line_clean
        
        # Priority 4: Look for title-case lines (2-8 words, reasonable length)
        # This catches titles that don't match standard patterns
        for line in lines[:15]:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 5 or len(line_clean) > 100:
                continue
            
            # Skip all-caps lines (likely headers or company names)
            if line_clean.isupper():
                continue
            
            # Check if it's title case with 2-8 words
            words = line_clean.split()
            if 2 <= len(words) <= 8:
                # Count capitalized words
                capitalized = sum(1 for w in words if w and len(w) > 1 and w[0].isupper())
                # If most words are capitalized, it's likely a title
                if capitalized >= len(words) * 0.6:
                    # Final validation
                    if not self._is_header_or_company(line_clean):
                        return line_clean
        
        return "Position Not Specified"
    
    def _is_header_or_company(self, text: str) -> bool:
        """Helper to check if text is a header or company name, not a job title"""
        text_lower = text.lower()
        
        # Common non-title indicators
        non_title_keywords = [
            'company', 'since', 'founded', 'established', 'excellence',
            'welcome', 'thank you', 'sincerely', 'regards',
            'application', 'resume', 'cover letter',
            'equal opportunity', 'eeo', 'affirmative action'
        ]
        
        if any(keyword in text_lower for keyword in non_title_keywords):
            return True
        
        # If it's very short (1-2 chars), likely not a title
        if len(text.strip()) < 3:
            return True
        
        return False

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
        
        # First, try to find company name in first 3 lines (often in header)
        # Look for lines that are all caps or title case and not too long
        for line in lines[:3]:
            line_clean = line.strip()
            # Skip empty lines and very short lines
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Skip lines that look like headers (ABOUT, POSITION, etc.)
            if re.match(r'^(ABOUT|POSITION|LOCATION|JOB|VACANCY|ANNOUNCEMENT|DESCRIPTION)[\s:]', line_clean, re.IGNORECASE):
                continue
            
            # Check if line is all caps or title case (likely company name)
            words = line_clean.split()
            if words:
                # All caps company name (e.g., "MONORI SCHOOL")
                if line_clean.isupper() and len(line_clean) < 50:
                    # Clean special characters but keep spaces and ampersands
                    company = re.sub(r'[^\w\s&]', ' ', line_clean).strip()
                    if len(company) > 2:
                        return company
                
                # Title case company name (e.g., "Monori School")
                if all(word[0].isupper() for word in words if word and len(word) > 2) and len(line_clean) < 50:
                    company = re.sub(r'[^\w\s&]', ' ', line_clean).strip()
                    if len(company) > 2:
                        return company
        
        # Second, try common company indicators with word boundaries
        company_indicators = [
            (r'\bcompany:\s*', 'Company:'),
            (r'\borganization:\s*', 'Organization:'),
            (r'\bfirm:\s*', 'Firm:'),
            (r'\b(?:working\s+)?at\s+(\w+(?:\s+\w+){0,3})\b', 'at'),  # "at Company" or "working at Company"
            (r'\bjoin\s+(\w+(?:\s+\w+){0,3})\b', 'join')  # "join Company"
        ]
        
        for line in lines[:10]:  # Check first 10 lines
            line_clean = line.strip()
            if not line_clean:
                continue
                
            for pattern, indicator_type in company_indicators:
                match = re.search(pattern, line_clean, re.IGNORECASE)
                if match:
                    if indicator_type in ['Company:', 'Organization:', 'Firm:']:
                        # Extract everything after the indicator
                        company = line_clean.split(':', 1)[1].strip()
                    elif match.groups():
                        # Extract from captured group
                        company = match.group(1).strip()
                    else:
                        continue
                    
                    # Clean and validate
                    company = re.sub(r'[^\w\s&]', ' ', company).strip()
                    # Ensure it's not a fragment or common word
                    if len(company) > 2 and len(company) < 50:
                        # Avoid fragments like "ion" or common words
                        if company.lower() not in ['the', 'our', 'this', 'that', 'with', 'from', 'ion', 'tion']:
                            return company
        
        # Fallback: Look for "ABOUT <COMPANY>" section
        for i, line in enumerate(lines[:20]):
            if re.match(r'^ABOUT\s+[A-Z]', line.strip()):
                # Company name is in this line after "ABOUT"
                company = re.sub(r'^ABOUT\s+', '', line.strip())
                company = re.sub(r'[^\w\s&]', ' ', company).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        return "Company Not Specified"

    def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """Main job description analysis function"""
        try:
            # Validate that this is actually a job description
            validation_result = self.validate_is_job_description(job_text)
            if not validation_result['is_valid']:
                raise ValueError(validation_result['error'])
            
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
    
    def _deduplicate_skills(self, skills: List[str]) -> List[str]:
        """
        Aggressively deduplicate skills using multiple matching strategies.
        Same logic as EnhancedSimilarityAnalyzer for consistency.
        """
        if not skills:
            return []
        
        # Clean and normalize skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1:  # Skip empty or single-char
                cleaned_skills.append(skill)
        
        if not cleaned_skills:
            return []
        
        # Deduplicate
        unique_skills = []
        seen_lower = set()
        
        for skill in cleaned_skills:
            skill_lower = skill.lower()
            
            # Skip exact duplicates (case-insensitive)
            if skill_lower in seen_lower:
                continue
            
            # Check if this skill is a substring of any existing skill
            is_substring = False
            for existing in list(unique_skills):
                existing_lower = existing.lower()
                
                # If current skill is substring of existing, skip it
                if skill_lower in existing_lower and skill_lower != existing_lower:
                    is_substring = True
                    break
                
                # If existing is substring of current, replace existing
                if existing_lower in skill_lower and skill_lower != existing_lower:
                    unique_skills.remove(existing)
                    seen_lower.discard(existing_lower)
                    break
            
            if is_substring:
                continue
            
            # Word-level overlap check (e.g., "Agile" vs "Agile Methodology")
            skip_due_to_overlap = False
            words_current = set(skill_lower.split())
            
            for existing in list(unique_skills):
                existing_lower = existing.lower()
                words_existing = set(existing_lower.split())
                
                # Special cases for common abbreviations
                ci_cd_variants = {'ci/cd', 'ci-cd', 'cicd', 'continuous integration', 
                                 'continuous deployment', 'continuous delivery'}
                if skill_lower in ci_cd_variants and existing_lower in ci_cd_variants:
                    skip_due_to_overlap = True
                    break
                
                # Special case: Agile variants (Agile, Agile Methodology, Agile Development, etc.)
                if 'agile' in skill_lower and 'agile' in existing_lower:
                    # Keep only one Agile-related skill (prefer just "Agile")
                    if skill_lower == 'agile':
                        # Replace existing with just "Agile"
                        unique_skills.remove(existing)
                        seen_lower.discard(existing_lower)
                        break
                    elif existing_lower == 'agile':
                        # Keep existing "Agile", skip current
                        skip_due_to_overlap = True
                        break
                    else:
                        # Both are compound (e.g., "Agile Methodology" vs "Agile Development")
                        # Keep the first one encountered
                        skip_due_to_overlap = True
                        break
                
                # Calculate word overlap
                if words_current and words_existing:
                    overlap = len(words_current & words_existing)
                    min_words = min(len(words_current), len(words_existing))
                    
                    # If >70% word overlap, consider duplicate
                    if overlap / min_words > 0.7:
                        # Keep the longer/more specific one
                        if len(skill_lower) <= len(existing_lower):
                            skip_due_to_overlap = True
                            break
                        else:
                            unique_skills.remove(existing)
                            seen_lower.discard(existing_lower)
            
            if skip_due_to_overlap:
                continue
            
            unique_skills.append(skill)
            seen_lower.add(skill_lower)
        
        return unique_skills
    
    def calculate_similarity(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Calculate similarity between resume and job description with detailed recommendations"""
        try:
            # Import resume parser for proper skill extraction
            from resume_parser import ResumeParser
            
            # Extract skills from both documents
            resume_parser = ResumeParser()
            resume_skills = self._deduplicate_skills(resume_parser.extract_skills_dynamically(resume_text))
            
            # Detect if applicant is a recent graduate
            graduate_info = resume_parser.detect_recent_graduate(resume_text)
            
            job_analyzer = JobAnalyzer()
            job_skills = self._deduplicate_skills(job_analyzer.extract_required_skills(job_text))
            
            # Normalize for comparison
            resume_skills_lower = set(skill.lower() for skill in resume_skills)
            job_skills_lower = set(skill.lower() for skill in job_skills)
            
            # Find matching and missing skills
            matching_skills = []
            missing_skills = []
            
            for job_skill in job_skills:
                job_skill_lower = job_skill.lower()
                if job_skill_lower in resume_skills_lower:
                    matching_skills.append(job_skill)
                else:
                    missing_skills.append(job_skill)
            
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
            
            # Generate recommendations (with graduate-aware adjustments)
            recommendations = self.generate_recommendations(
                resume_text, 
                job_text, 
                matching_skills, 
                missing_skills,
                overall_similarity,
                skill_similarity,
                graduate_info
            )
            
            return {
                'overall_score': round(overall_similarity, 2),
                'skill_match_score': round(skill_similarity, 2),
                'experience_match_score': round(overall_similarity * 0.8, 2),
                'keyword_match_score': round(keyword_similarity, 2),
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'recommendations': recommendations,
                'graduate_status': graduate_info,
                'skills_summary': {
                    'total_job_skills': len(job_skills),
                    'matched_skills': len(matching_skills),
                    'missing_skills': len(missing_skills),
                    'match_percentage': round((len(matching_skills) / len(job_skills) * 100) if job_skills else 0, 2)
                }
            }
            
        except Exception as e:
            raise Exception(f"Similarity calculation failed: {str(e)}")
    
    def calculate_skill_similarity(self, resume_text: str, job_text: str) -> float:
        """Calculate skill-based similarity using proper extractors for each document type"""
        try:
            # Import resume parser for proper skill extraction from resumes
            from resume_parser import ResumeParser
            
            # Use ResumeParser for resume skills
            resume_parser = ResumeParser()
            resume_skills = resume_parser.extract_skills_dynamically(resume_text)
            
            # Use JobAnalyzer for job skills
            job_analyzer = JobAnalyzer()
            job_skills = job_analyzer.extract_required_skills(job_text)
            
            if not job_skills:
                return 0.0
            
            # CRITICAL: Deduplicate skills before comparison to avoid inflating counts
            resume_skills = self._deduplicate_skills(resume_skills)
            job_skills = self._deduplicate_skills(job_skills)
            
            # Normalize skills for better matching (case-insensitive comparison)
            resume_skills_set = set(skill.lower() for skill in resume_skills)
            job_skills_set = set(skill.lower() for skill in job_skills)
            
            if not job_skills_set:
                return 0.0
            
            # Calculate Jaccard similarity for skills
            intersection = len(resume_skills_set.intersection(job_skills_set))
            union = len(resume_skills_set.union(job_skills_set))
            
            # Also calculate how many job skills are matched (more important metric)
            job_skills_matched = len(resume_skills_set.intersection(job_skills_set))
            job_match_percentage = (job_skills_matched / len(job_skills_set)) * 100 if len(job_skills_set) > 0 else 0.0
            
            # Use weighted average: 70% job match, 30% Jaccard
            jaccard_similarity = (intersection / union) * 100 if union > 0 else 0.0
            weighted_similarity = (job_match_percentage * 0.7) + (jaccard_similarity * 0.3)
            
            return min(weighted_similarity, 100.0)
            
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
    
    def generate_recommendations(
        self, 
        resume_text: str, 
        job_text: str, 
        matching_skills: List[str],
        missing_skills: List[str],
        overall_score: float,
        skill_score: float,
        graduate_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate detailed recommendations to improve resume match (graduate-aware)"""
        is_recent_graduate = graduate_info and graduate_info.get('is_recent_graduate', False)
        has_limited_experience = graduate_info and graduate_info.get('has_limited_experience', False)
        
        recommendations = {
            'priority': 'high' if overall_score < 60 else 'medium' if overall_score < 80 else 'low',
            'action_items': [],
            'skill_suggestions': [],
            'content_suggestions': [],
            'formatting_tips': [],
            'graduate_specific': [] if (is_recent_graduate or has_limited_experience) else None
        }
        
        # Graduate-specific introduction
        if is_recent_graduate:
            recommendations['action_items'].append({
                'type': 'graduate_status',
                'title': '🎓 Recent Graduate Advantage',
                'description': 'You\'re a recent graduate! Employers understand you may lack industry experience but have fresh academic knowledge.',
                'impact': 'info',
                'action': 'Emphasize your academic projects, coursework, internships, and willingness to learn.'
            })
        
        # Skill-based recommendations (adjusted for graduates)
        if missing_skills:
            critical_skills = missing_skills[:5]  # Top 5 missing skills
            
            if is_recent_graduate or has_limited_experience:
                # More encouraging message for graduates
                recommendations['skill_suggestions'].append({
                    'type': 'add_skills',
                    'title': 'Highlight Relevant Knowledge & Skills',
                    'description': f'The job requires {len(missing_skills)} skills you haven\'t explicitly listed. As a recent graduate, you likely have academic exposure to many of these.',
                    'skills': critical_skills,
                    'impact': 'high',
                    'action': f'Add these skills if you\'ve studied them in coursework, projects, or have basic knowledge: {", ".join(critical_skills)}. Include your proficiency level (e.g., "Python (Academic Projects)", "JavaScript (Coursework & Personal Projects)").'
                })
            else:
                # Standard message for experienced professionals
                recommendations['skill_suggestions'].append({
                    'type': 'add_skills',
                    'title': 'Add Missing Critical Skills',
                    'description': f'Your resume is missing {len(missing_skills)} skills mentioned in the job description.',
                    'skills': critical_skills,
                    'impact': 'high',
                    'action': f'Add these skills to your resume if you have experience with them: {", ".join(critical_skills)}'
                })
        
        # Extract job requirements for targeted recommendations
        job_analyzer = JobAnalyzer()
        job_data = job_analyzer.analyze_job_description(job_text)
        
        # Experience level recommendations (graduate-aware)
        experience_level = job_data.get('experience_level', '')
        if experience_level:
            if is_recent_graduate or has_limited_experience:
                # Check if it's an entry-level position
                is_entry_level = any(term in experience_level.lower() for term in ['entry', 'junior', '0-1', '0-2', 'fresh', 'graduate'])
                
                if is_entry_level:
                    recommendations['action_items'].append({
                        'type': 'highlight_experience',
                        'title': 'Perfect Match for Entry-Level',
                        'description': f'Great news! This is an entry-level position ({experience_level}) suitable for recent graduates.',
                        'impact': 'positive',
                        'action': 'Highlight your internships, academic projects, hackathons, and any relevant coursework. Show enthusiasm and willingness to learn.'
                    })
                else:
                    recommendations['action_items'].append({
                        'type': 'highlight_experience',
                        'title': 'Bridge the Experience Gap',
                        'description': f'This role prefers {experience_level} experience. As a recent graduate, you can still apply!',
                        'impact': 'medium',
                        'action': 'Emphasize transferable skills from internships, academic projects, part-time work, or volunteer experience. Quantify your project impact (e.g., "Developed web app used by 100+ students").'
                    })
                
                # Add graduate-specific content suggestions
                if graduate_info.get('has_academic_projects'):
                    recommendations['graduate_specific'].append({
                        'type': 'academic_projects',
                        'title': '✅ Strong Academic Project Portfolio',
                        'description': 'You have academic projects listed, which is excellent for recent graduates.',
                        'impact': 'positive',
                        'action': 'Make sure each project includes: technologies used, your specific role, and measurable outcomes.'
                    })
                else:
                    recommendations['graduate_specific'].append({
                        'type': 'add_projects',
                        'title': 'Add Academic Projects Section',
                        'description': 'Academic projects demonstrate practical skills to employers.',
                        'impact': 'high',
                        'action': 'Create a "Projects" section showcasing your capstone project, assignments, or personal coding projects. Include GitHub links if available.'
                    })
                
                if graduate_info.get('has_internship'):
                    recommendations['graduate_specific'].append({
                        'type': 'internship_experience',
                        'title': '✅ Internship Experience',
                        'description': 'Your internship experience is valuable and demonstrates real-world exposure.',
                        'impact': 'positive',
                        'action': 'Emphasize what you learned, tools you used, and any contributions you made during your internship.'
                    })
                else:
                    recommendations['graduate_specific'].append({
                        'type': 'lack_internship',
                        'title': 'Consider Adding Related Experience',
                        'description': 'No internship listed. Many employers value any practical experience.',
                        'impact': 'medium',
                        'action': 'Include part-time jobs, volunteer work, freelance projects, or open-source contributions that demonstrate relevant skills.'
                    })
            else:
                # Standard experience recommendation for non-graduates
                recommendations['action_items'].append({
                    'type': 'highlight_experience',
                    'title': 'Emphasize Relevant Experience',
                    'description': f'This role requires {experience_level} experience.',
                    'impact': 'high',
                    'action': f'Ensure your resume clearly shows {experience_level} level experience with specific examples and achievements.'
                })
        
        # Keyword optimization
        job_keywords = self.extract_important_keywords(job_text)
        resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))
        missing_keywords = [kw for kw in job_keywords if kw.lower() not in resume_keywords]
        
        if missing_keywords:
            recommendations['content_suggestions'].append({
                'type': 'add_keywords',
                'title': 'Incorporate Key Terms',
                'description': f'Your resume is missing {len(missing_keywords)} important keywords from the job description.',
                'keywords': missing_keywords[:10],
                'impact': 'medium',
                'action': f'Naturally incorporate these terms: {", ".join(missing_keywords[:5])}'
            })
        
        # Responsibility alignment
        job_responsibilities = job_data.get('key_responsibilities', [])
        if job_responsibilities:
            recommendations['content_suggestions'].append({
                'type': 'align_responsibilities',
                'title': 'Align Your Experience with Job Duties',
                'description': 'Tailor your work experience bullets to match the job responsibilities.',
                'responsibilities': job_responsibilities[:3],
                'impact': 'high',
                'action': 'Rewrite your experience bullets to mirror the language and focus of the job responsibilities.'
            })
        
        # Quantifiable achievements
        if not re.search(r'\d+%|\d+x|\$\d+|increased|improved|reduced|grew', resume_text.lower()):
            recommendations['content_suggestions'].append({
                'type': 'add_metrics',
                'title': 'Add Quantifiable Achievements',
                'description': 'Include numbers, percentages, or measurable results.',
                'impact': 'high',
                'action': 'Add metrics like "Increased efficiency by 30%" or "Managed team of 5 developers"'
            })
        
        # ATS optimization
        recommendations['formatting_tips'].extend([
            {
                'type': 'ats_keywords',
                'title': 'ATS Keyword Optimization',
                'description': 'Ensure your resume passes Applicant Tracking Systems',
                'impact': 'high',
                'tips': [
                    f'Use exact skill names from job description: {", ".join(missing_skills[:3])}' if missing_skills else 'Your skills match well!',
                    'Avoid tables, images, or complex formatting',
                    'Use standard section headers (Experience, Education, Skills)',
                    'Save as .docx or .pdf format'
                ]
            },
            {
                'type': 'content_structure',
                'title': 'Content Structure',
                'description': 'Organize your resume for maximum impact',
                'impact': 'medium',
                'tips': [
                    'Start bullets with strong action verbs',
                    'Put most relevant experience first',
                    'Keep resume to 1-2 pages',
                    'Use consistent formatting throughout'
                ]
            }
        ])
        
        # Score-based priority actions (graduate-aware thresholds)
        if is_recent_graduate or has_limited_experience:
            # More lenient thresholds for graduates
            if skill_score < 40:
                recommendations['action_items'].insert(0, {
                    'type': 'improve_skills',
                    'title': '🟡 Build Your Skill Profile',
                    'description': f'Your skill match is {skill_score:.0f}%. As a recent graduate, focus on adding academic and project-based skills.',
                    'impact': 'high',
                    'action': f'List skills from coursework, projects, and self-study: {", ".join(missing_skills[:3])}. Mention your proficiency level honestly.'
                })
            elif skill_score < 60:
                recommendations['action_items'].insert(0, {
                    'type': 'moderate_match',
                    'title': '🟡 Good Start, Room to Improve',
                    'description': f'Your skill match is {skill_score:.0f}%. This is reasonable for a recent graduate!',
                    'impact': 'medium',
                    'action': 'Add any additional relevant skills from your coursework and projects. Employers know graduates are still learning.'
                })
            else:
                recommendations['action_items'].insert(0, {
                    'type': 'strong_match',
                    'title': '🟢 Strong Match for Entry-Level!',
                    'description': f'Your skill match is {skill_score:.0f}%. Excellent for a recent graduate!',
                    'impact': 'positive',
                    'action': 'Your skills are well-aligned. Focus on showcasing projects and demonstrating your learning ability.'
                })
        else:
            # Standard thresholds for experienced professionals
            if skill_score < 50:
                recommendations['action_items'].insert(0, {
                    'type': 'urgent_skills',
                    'title': '🔴 CRITICAL: Low Skill Match',
                    'description': f'Your skill match is only {skill_score:.0f}%. This significantly reduces your chances.',
                    'impact': 'critical',
                    'action': f'Immediately add these skills if you have them: {", ".join(missing_skills[:3])}'
                })
            elif skill_score < 70:
                recommendations['action_items'].insert(0, {
                    'type': 'improve_skills',
                    'title': '🟡 Moderate Skill Match',
                    'description': f'Your skill match is {skill_score:.0f}%. There\'s room for improvement.',
                    'impact': 'high',
                    'action': 'Review the missing skills list and add any you have experience with.'
                })
            else:
                recommendations['action_items'].insert(0, {
                    'type': 'good_match',
                    'title': '🟢 Good Skill Match',
                    'description': f'Your skill match is {skill_score:.0f}%. You\'re on the right track!',
                    'impact': 'low',
                    'action': 'Fine-tune your resume with the suggestions below to make it even stronger.'
                })
        
        return recommendations
    
    def extract_important_keywords(self, text: str) -> List[str]:
        """Extract important keywords from job description"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stop words
        stop_words = {
            'this', 'that', 'with', 'from', 'will', 'have', 'your',
            'their', 'about', 'would', 'there', 'which', 'when', 'where',
            'what', 'should', 'could', 'must', 'been', 'were', 'very',
            'also', 'into', 'just', 'than', 'them', 'these', 'those',
            'through', 'during', 'before', 'after', 'above', 'below'
        }
        
        # Filter and count words
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:15] if freq > 1]