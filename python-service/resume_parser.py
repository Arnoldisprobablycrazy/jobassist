# python-service/resume_parser.py
import PyPDF2
from docx import Document
import re
import json
from typing import Dict, List, Any
from collections import Counter

# Optional NLTK support for enhanced extraction (graceful degradation if not available)
NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    
    # Try to load required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
        except:
            pass
    
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        try:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            pass
    
    # Verify NLTK is actually usable
    try:
        test_tokens = word_tokenize("test")
        NLTK_AVAILABLE = True
        print("✅ NLTK available for enhanced skill extraction")
    except:
        NLTK_AVAILABLE = False
        print("ℹ️  NLTK not available - using regex-only extraction (still works fine!)")
        
except ImportError:
    NLTK_AVAILABLE = False
    print("ℹ️  NLTK not installed - using regex-only extraction")

class ResumeParser:
    def __init__(self):
        # Common technical skills patterns
        self.technical_skills_patterns = [
            # Programming Languages
            r'\b(python|java|javascript|typescript|c\+\+|c#|go|rust|swift|kotlin|r|ruby|php|perl|scala)\b',
            # Frontend Technologies
            r'\b(react|angular|vue\.js|vuejs|next\.js|nextjs|nuxt\.js|nuxtjs|svelte|jquery|html5|css3|sass|less|bootstrap|tailwind)\b',
            # Backend Technologies
            r'\b(node\.js|nodejs|express\.js|expressjs|django|flask|spring|laravel|rails|asp\.net|fastapi|graphql|rest api)\b',
            # Databases
            r'\b(mysql|postgresql|mongodb|redis|sqlite|oracle|sql server|dynamodb|cassandra|elasticsearch)\b',
            # Cloud & DevOps
            r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible|jenkins|git|github|gitlab|ci/cd|devops)\b',
            # Data Science & AI
            r'\b(pandas|numpy|scikit-learn|tensorflow|pytorch|keras|opencv|nltk|spacy|tableau|power bi)\b',
            # Mobile Development
            r'\b(react native|flutter|android|ios|xcode|android studio)\b',
            # Testing
            r'\b(jest|mocha|chai|cypress|selenium|junit|pytest|unittest)\b',
            # Tools & Methodologies
            r'\b(agile|scrum|kanban|jira|confluence|figma|sketch|photoshop|illustrator)\b'
        ]
        
        # Soft skills patterns
        self.soft_skills_patterns = [
            r'\b(communication|leadership|teamwork|problem.solving|critical thinking|creativity|adaptability|time management|collaboration|presentation|negotiation)\b',
            r'\b(project management|strategic planning|analytical skills|attention to detail|multitasking|decision making)\b'
        ]

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def extract_skills_dynamically(self, text: str) -> List[str]:
        """Extract skills dynamically from resume text using multiple methods"""
        skills = set()

        # Preprocess: remove contact info and noisy tokens (emails, urls, phones)
        cleaned_text = re.sub(r'\S+@\S+', ' ', text)  # remove emails
        cleaned_text = re.sub(r'http[s]?://\S+|www\.\S+', ' ', cleaned_text)  # remove urls
        cleaned_text = re.sub(r'\+?\d[\d\s\-\(\)]{6,}\d', ' ', cleaned_text)  # remove phone-like sequences

        # Method 1: Pattern matching for technical skills (on cleaned text)
        for pattern in self.technical_skills_patterns:
            matches = re.findall(pattern, cleaned_text.lower())
            for match in matches:
                # match may be a tuple from grouped regex; handle accordingly
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                skill = self.clean_skill(match)
                if skill and self.looks_like_skill(skill):
                    skills.add(skill)

        # Method 2: Pattern matching for soft skills
        for pattern in self.soft_skills_patterns:
            matches = re.findall(pattern, cleaned_text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                skill = self.clean_skill(match.replace('_', ' '))
                if skill and self.looks_like_skill(skill):
                    skills.add(skill)

        # Method 3: Look for skills sections (common headings)
        skills_section_keywords = [
            'skills', 'technical skills', 'technologies', 'competencies',
            'expertise', 'qualifications', 'proficiencies'
        ]

        lines = cleaned_text.split('\n')
        in_skills_section = False

        for i, line in enumerate(lines):
            line_strip = line.strip()
            line_lower = line_strip.lower()

            # skip lines that obviously contain contact info or URLs
            if '@' in line_lower or 'http' in line_lower or 'linkedin' in line_lower or 'github' in line_lower:
                continue

            # Enter skills section
            if any(keyword in line_lower for keyword in skills_section_keywords):
                in_skills_section = True
                continue

            if in_skills_section:
                # End section heuristics
                if not line_strip or any(end_word in line_lower for end_word in ['experience', 'education', 'projects']):
                    in_skills_section = False
                    continue

                # Split by common separators
                skill_items = re.split(r'[,:;/•\-–—>|/\\]', line_strip)
                for item in skill_items:
                    item = item.strip()
                    if not item:
                        continue
                    # Remove section prefixes like "programming:" or "frontend:"
                    item = re.sub(r'^(programming|frontend|backend|cloud|tools|skills|technical|technologies)\s*[:\-]\s*', '', item, flags=re.I)
                    # Remove parentheticals and trailing qualifiers
                    item = re.sub(r'\([^\)]*\)', '', item)
                    item = item.strip()
                    if 2 <= len(item) <= 60:
                        skill = self.clean_skill(item)
                        if skill and self.looks_like_skill(skill):
                            skills.add(skill)

        # Method 4: Token-level heuristics (catch compound tech terms)
        # Split by common separators and spaces, then validate
        tokens = re.split(r'[\n,;:/\\|•\-–—]', cleaned_text)
        for tok in tokens:
            tok = tok.strip()
            if not tok or len(tok) < 2 or len(tok) > 60:
                continue
            # Ignore long sentence-like lines (likely descriptive text)
            # Even if they contain tech markers, prefer extracting via pattern matching above
            if len(tok.split()) > 4:
                continue
            # Skip obvious verb-driven fragments (e.g., 'built', 'developed', 'implemented')
            if re.search(r'\b(built|developed|implemented|designed|worked|experience|using|with|responsible)\b', tok, flags=re.I):
                continue
            # Remove contact-like lines
            if '@' in tok or 'http' in tok or 'www.' in tok:
                continue
            # Clean and validate
            tok_clean = re.sub(r'^(?:skills|experience|projects)[:\-\s]+', '', tok, flags=re.I).strip()
            tok_clean = re.sub(r'\([^\)]*\)', '', tok_clean).strip()
            if 2 <= len(tok_clean) <= 60:
                skill = self.clean_skill(tok_clean)
                if skill and self.looks_like_skill(skill):
                    skills.add(skill)

        # Final filtering: remove common non-skill tokens (countries, generic words)
        final_skills = []
        excluded_terms = {
            'united states', 'usa', 'uk', 'united kingdom', 'canada', 'germany', 'france', 'india',
            'china', 'nigeria', 'brazil', 'russia', 'australia'
        }
        for s in skills:
            s_low = s.lower()
            if any(ex in s_low for ex in excluded_terms):
                continue
            # Exclude tokens that look like contact info or addresses
            if re.search(r'\d{2,}', s_low):
                continue
            if any(tok in s_low for tok in ['email', 'phone', 'linkedin', 'github', 'www', 'http']):
                continue
            final_skills.append(s)

        return sorted(list(set(final_skills)), key=lambda x: x.lower())

    def clean_skill(self, skill: str) -> str:
        """Clean and normalize a skill string"""
        # Normalize case and remove qualifiers
        original = skill
        skill = skill.strip()
        # Remove leading role/section labels
        skill = re.sub(r'^(programming|frontend|backend|cloud|tools|skills|technical|technologies)\s*[:\-]\s*', '', skill, flags=re.I)
        # Remove strength qualifiers
        skill = re.sub(r'^(strong|expert|basic|intermediate|advanced)\s+', '', skill, flags=re.I)
        # Remove trailing words like 'skills' or 'experience'
        skill = re.sub(r'\s+(skills?|knowledge|experience|proficiency)$', '', skill, flags=re.I)
        # Remove parenthetical content and extra spaces
        skill = re.sub(r'\([^\)]*\)', '', skill).strip()
        skill = ' '.join(skill.split())

        # Titlecase but preserve common uppercase acronyms
        def normalize_token(tok: str) -> str:
            if tok.lower() in {'api', 'css', 'html', 'sql', 'nosql', 'aws', 'gcp', 'gpu', 'cpu', 'ci/cd'}:
                return tok.upper()
            if re.match(r'^[a-z]+\.[a-z]+$', tok.lower()):
                return tok.lower()
            return tok.title()

        parts = skill.split()
        parts = [normalize_token(p) for p in parts]
        skill = ' '.join(parts)

        # Specific replacements
        skill_replacements = {
            'Javascript': 'JavaScript',
            'Typescript': 'TypeScript',
            'Node.Js': 'Node.js',
            'React.Js': 'React',
            'Vue.Js': 'Vue.js',
            'Next.Js': 'Next.js',
            'Html': 'HTML',
            'Css': 'CSS',
            'Sql': 'SQL',
            'Nosql': 'NoSQL',
            'Api': 'API',
            'Rest Api': 'REST API',
            'Graphql': 'GraphQL',
            'Ai': 'AI',
            'Ml': 'Machine Learning',
            'Ci/Cd': 'CI/CD'
        }

        skill = skill_replacements.get(skill, skill)
        # Final guard: remove empty or too-short results
        if not skill or len(skill) < 2:
            return ''
        return skill

    def looks_like_skill(self, word: str) -> bool:
        """Check if a word looks like a technical skill"""
        word_lower = word.lower().strip()

        # Quick exclusions
        if not word_lower or len(word_lower) < 2 or len(word_lower) > 60:
            return False
        if any(tok in word_lower for tok in ['@', 'http', 'www', 'email', 'phone', 'linkedin', 'github']):
            return False

        # Exclude numeric-heavy tokens (likely years, phone numbers, addresses)
        if re.search(r'\d{2,}', word_lower) and not re.search(r'(c\+\+|c#|r\d)', word_lower):
            return False

        # Common non-skill words to exclude
        excluded_words = {
            'company', 'university', 'college', 'school', 'project', 'team',
            'year', 'years', 'month', 'months', 'client', 'customer', 'user',
            'system', 'service', 'application', 'software', 'technology',
            'solution', 'product', 'management', 'development', 'engineering',
            'address', 'street', 'road', 'city', 'state', 'country', 'manager', 'inc', 'ltd'
        }
        if word_lower in excluded_words or any(word_lower.endswith(' ' + w) for w in excluded_words):
            return False

        # Check patterns: technical markers or compound tokens
        for pattern in self.technical_skills_patterns + self.soft_skills_patterns:
            if re.search(pattern, word_lower):
                return True

        # Check for indicators like .js, net, api, or all-caps acronyms
        if re.search(r'\.[a-z]{2,5}$', word_lower) or re.search(r'^[A-Z]{2,6}$', word) or re.search(r'\b(api|aws|gcp|sql|html|css)\b', word_lower):
            return True

        # Reject otherwise (avoid generic nouns)
        return False

    def extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        # Extract name (simple heuristic - first line that's not too long)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        name = ""
        for line in lines[:5]:  # Check first 5 lines
            if (len(line) < 50 and 
                not any(word in line.lower() for word in ['resume', 'cv', 'curriculum', 'vitae']) and
                re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line)):
                name = line
                break
        
        return {
            'name': name,
            'email': emails[0] if emails else '',
            'phone': phones[0] if phones else ''
        }

    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience with improved parsing"""
        experience = []
        lines = text.split('\n')
        
        experience_keywords = ['experience', 'work history', 'employment', 'professional experience']
        current_experience = {}
        in_experience_section = False
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Check if we're entering experience section
            if any(keyword in line_lower for keyword in experience_keywords):
                in_experience_section = True
                continue
            
            if in_experience_section:
                # Skip empty lines
                if not line_clean:
                    continue
                
                # Look for job title patterns
                job_title_patterns = [
                    r'^(senior|junior|lead|principal)?\s*(software|frontend|backend|full.stack|web|mobile)\s+(developer|engineer)',
                    r'^(data scientist|data analyst|devops engineer|product manager|project manager|ui/ux designer)',
                    r'^[A-Z][a-z]+\s+[A-Z][a-z]+$'  # Simple title pattern
                ]
                
                for pattern in job_title_patterns:
                    if re.search(pattern, line_lower):
                        if current_experience:
                            experience.append(current_experience)
                        current_experience = {'title': line_clean, 'description': ''}
                        break
                
                # Add to current experience description
                if current_experience and line_clean != current_experience.get('title', ''):
                    current_experience['description'] += line_clean + " "
        
        # Add the last experience
        if current_experience:
            experience.append(current_experience)
        
        return experience if experience else [{'title': 'Professional Experience', 'description': 'Experience details extracted from resume'}]

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        education_keywords = ['education', 'university', 'college', 'bachelor', 'master', 'phd', 'degree', 'diploma']
        current_education = {}
        in_education_section = False
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            if any(keyword in line_lower for keyword in education_keywords):
                in_education_section = True
                if current_education:
                    education.append(current_education)
                current_education = {'institution': line_clean}
                continue
            
            if in_education_section and line_clean:
                # Look for degree patterns
                degree_patterns = [
                    r'\b(bachelor|b\.?s\.?|b\.?a\.?|master|m\.?s\.?|m\.?a\.?|phd|doctorate|associate|diploma|certificate)\b',
                    r'\b(of science|of arts|of engineering|in computer science|in business administration)\b'
                ]
                
                if any(re.search(pattern, line_lower) for pattern in degree_patterns):
                    current_education['degree'] = line_clean
                elif 'institution' in current_education and current_education['institution'] != line_clean:
                    # Assume this is additional info (dates, location, etc.)
                    current_education['details'] = line_clean
        
        if current_education:
            education.append(current_education)
        
        return education if education else [{'institution': 'Education details extracted from resume'}]

    def detect_recent_graduate(self, text: str) -> Dict[str, Any]:
        """
        Detect if the applicant is a recent graduate or has limited experience.
        Returns dictionary with graduate status and relevant details.
        """
        text_lower = text.lower()
        current_year = 2025
        
        # Indicators of recent graduate status
        graduate_indicators = {
            'is_recent_graduate': False,
            'graduation_year': None,
            'has_internship': False,
            'has_academic_projects': False,
            'has_limited_experience': False,
            'years_of_experience': 0,
            'relevant_coursework': [],
            'academic_achievements': []
        }
        
        # Check for graduation year patterns
        graduation_patterns = [
            r'graduated?[:\s]+(?:in\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\.?\s*(\d{4})',
            r'graduation\s+(?:date|year)?[:\s]+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\.?\s*(\d{4})',
            r'(?:bachelor|master|b\.?s\.?|m\.?s\.?|degree).*?(\d{4})',
            r'(?:expected|anticipated)\s+graduation[:\s]+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)?\.?\s*(\d{4})',
            r'(?:class\s+of|graduating)\s+(\d{4})',
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+(\d{4})\s*(?:\n|$|•|-)',
            r'university.*?(\d{4})\s*(?:\n|gpa|dean)',
            r'college.*?(\d{4})\s*(?:\n|gpa|dean)'
        ]
        
        graduation_years = []
        for pattern in graduation_patterns:
            matches = re.findall(pattern, text_lower)
            graduation_years.extend([int(year) for year in matches if 2015 <= int(year) <= current_year + 1])
        
        if graduation_years:
            most_recent_graduation = max(graduation_years)
            graduate_indicators['graduation_year'] = most_recent_graduation
            
            # Recent graduate if graduated within last 2 years
            if current_year - most_recent_graduation <= 2:
                graduate_indicators['is_recent_graduate'] = True
        
        # Check for internship experience
        internship_keywords = ['intern', 'internship', 'trainee', 'co-op', 'cooperative education']
        graduate_indicators['has_internship'] = any(keyword in text_lower for keyword in internship_keywords)
        
        # Check for academic/university projects
        project_keywords = [
            'academic project', 'university project', 'course project', 'capstone',
            'final year project', 'thesis', 'dissertation', 'research project',
            'group project', 'team project', 'class project'
        ]
        graduate_indicators['has_academic_projects'] = any(keyword in text_lower for keyword in project_keywords)
        
        # Detect years of experience
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?(?:work\s+)?experience'
        ]
        
        years_found = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            years_found.extend([int(year) for year in matches])
        
        if years_found:
            graduate_indicators['years_of_experience'] = max(years_found)
        else:
            # If no explicit years mentioned, count work experience entries
            experience_section = re.search(r'(?:work\s+)?experience.*?(?=education|skills|projects|$)', text_lower, re.DOTALL)
            if experience_section:
                # Count date ranges (e.g., "2023 - Present", "Jan 2022 - Dec 2023")
                date_ranges = re.findall(r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4}).*?(?:present|current|\d{4})', experience_section.group())
                graduate_indicators['years_of_experience'] = len(date_ranges)
        
        # Limited experience if less than 2 years
        if graduate_indicators['years_of_experience'] < 2:
            graduate_indicators['has_limited_experience'] = True
        
        # Extract relevant coursework
        coursework_keywords = ['relevant coursework', 'courses', 'curriculum', 'studied']
        for keyword in coursework_keywords:
            if keyword in text_lower:
                # Extract the next few lines after coursework mention
                coursework_section = re.search(f'{keyword}[:\s]+(.*?)(?=\n\n|education|experience|skills|$)', text_lower, re.DOTALL)
                if coursework_section:
                    courses = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', coursework_section.group(1))
                    graduate_indicators['relevant_coursework'] = courses[:5]  # Top 5 courses
        
        # Extract academic achievements
        achievement_keywords = [
            'dean\'s list', 'honor roll', 'gpa', 'scholarship', 'cum laude',
            'magna cum laude', 'summa cum laude', 'honor society', 'academic award'
        ]
        achievements = [keyword for keyword in achievement_keywords if keyword in text_lower]
        graduate_indicators['academic_achievements'] = achievements
        
        return graduate_indicators

    def validate_is_resume(self, text: str) -> tuple[bool, str]:
        """
        Validate if the document is actually a resume/CV.
        Returns (is_valid, error_message)
        """
        text_lower = text.lower()
        
        # Minimum text length check
        if len(text.strip()) < 100:
            return False, "Document is too short to be a resume (minimum 100 characters required)"
        
        # Resume indicator keywords (at least some should be present)
        resume_indicators = [
            'experience', 'education', 'skills', 'work history', 'employment',
            'professional experience', 'qualifications', 'career', 'university',
            'college', 'bachelor', 'master', 'degree', 'developer', 'engineer',
            'manager', 'analyst', 'designer', 'specialist', 'consultant',
            'projects', 'achievements', 'certifications', 'training', 'responsibilities',
            'duties', 'summary', 'objective', 'profile', 'about me', 'biography'
        ]
        
        # Count how many indicators are present
        indicator_count = sum(1 for indicator in resume_indicators if indicator in text_lower)
        
        # Reduced from 3 to 2 - be more lenient, some resumes are concise or use alternative section names
        if indicator_count < 2:
            return False, "Document doesn't appear to be a resume. Expected to find at least 2 resume-related sections (e.g., Experience, Education, Skills) but found only " + str(indicator_count)
        
        # Check for contact information (email or phone)
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
        
        if not (has_email or has_phone):
            return False, "Document doesn't contain typical resume contact information (email or phone number)"
        
        # Check for non-resume document types (be more lenient, only reject clear non-resumes)
        # Many resumes mention certificates, education transcripts in context - that's normal
        # Only reject if document is CLEARLY a different document type
        strict_non_resume_indicators = [
            'official invoice', 'receipt number', 'bank statement for', 'official transcript of',
            'purchase order number', 'medical record for', 'prescription for patient',
            'lab test results', 'payment confirmation', 'transaction receipt',
            'this is a transcript', 'grade report for', 'score report card'
        ]
        
        # Count strict non-resume indicators (must match exact phrases)
        non_resume_count = sum(1 for indicator in strict_non_resume_indicators if indicator in text_lower)
        
        # Only reject if we find 3+ strong indicators (very high confidence it's not a resume)
        if non_resume_count >= 3:
            return False, "Document appears to be a different type of document (transcript, certificate, statement, etc.), not a resume"
        
        # Check if it's mostly numbers/tables (like transcripts or statements)
        words = text.split()
        if len(words) < 50:
            return False, "Document is too short to be a comprehensive resume"
        
        # Calculate ratio of numeric content - be more lenient (resumes can have dates, phone numbers, GPA, etc.)
        numeric_words = sum(1 for word in words if any(char.isdigit() for char in word))
        numeric_ratio = numeric_words / len(words) if words else 0
        
        # Increased threshold from 40% to 60% - resumes naturally have lots of numbers (dates, years, GPA, phone, addresses)
        if numeric_ratio > 0.6:  # More than 60% numeric content
            return False, "Document contains too much numeric data. It may be a transcript, grade report, or financial statement rather than a resume"
        
        return True, ""

    def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Main resume parsing function"""
        try:
            # Extract text based on file type
            if file_type == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_type == 'docx':
                text = self.extract_text_from_docx(file_path)
            else:
                raise ValueError("Unsupported file type")
            
            # Validate that this is actually a resume
            is_valid, error_message = self.validate_is_resume(text)
            if not is_valid:
                raise ValueError(f"Invalid resume document: {error_message}")
            
            # Parse resume sections
            parsed_data = {
                'raw_text': text,
                'personal_info': self.extract_personal_info(text),
                'skills': self.extract_skills_dynamically(text),  # Use dynamic extraction
                'experience': self.extract_experience(text),
                'education': self.extract_education(text),
                'contact_info': self.extract_contact_info(text)
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Resume parsing failed: {str(e)}")

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        github_pattern = r'github\.com/[\w\-]+'
        portfolio_pattern = r'https?://[^\s]+\.(com|io|dev|net|org)[^\s]*'
        
        linkedin_matches = re.findall(linkedin_pattern, text.lower())
        github_matches = re.findall(github_pattern, text.lower())
        portfolio_matches = re.findall(portfolio_pattern, text.lower())
        
        return {
            'linkedin': linkedin_matches[0] if linkedin_matches else '',
            'github': github_matches[0] if github_matches else '',
            'portfolio': portfolio_matches[0] if portfolio_matches else ''
        }