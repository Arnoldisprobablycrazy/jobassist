# python-service/resume_parser.py
import PyPDF2
from docx import Document
import re
import json
from typing import Dict, List, Any
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from collections import Counter
import spacy

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

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
        text_lower = text.lower()
        
        # Method 1: Pattern matching for technical skills
        for pattern in self.technical_skills_patterns:
            matches = re.findall(pattern, text_lower)
            skills.update([match.title() for match in matches])
        
        # Method 2: Pattern matching for soft skills
        for pattern in self.soft_skills_patterns:
            matches = re.findall(pattern, text_lower)
            skills.update([match.replace('_', ' ').title() for match in matches])
        
        # Method 3: Look for skills sections (common headings)
        skills_section_keywords = [
            'skills', 'technical skills', 'technologies', 'competencies',
            'expertise', 'qualifications', 'proficiencies'
        ]
        
        lines = text.split('\n')
        in_skills_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering a skills section
            if any(keyword in line_lower for keyword in skills_section_keywords):
                in_skills_section = True
                continue
            
            if in_skills_section:
                # Skip empty lines or section endings
                if not line.strip() or any(end_word in line_lower for end_word in ['experience', 'education', 'projects']):
                    in_skills_section = False
                    continue
                
                # Extract skills from the skills section
                # Split by common separators: commas, slashes, bullets
                skill_items = re.split(r'[,•·\-–—>|/]', line)
                for item in skill_items:
                    item = item.strip()
                    if len(item) > 2 and len(item) < 50:  # Reasonable skill length
                        # Clean up the skill
                        skill = self.clean_skill(item)
                        if skill:
                            skills.add(skill)
        
        # Method 4: Noun phrase extraction (simple version)
        try:
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)
            
            # Look for noun phrases that might be skills
            nouns = [word for word, pos in tagged if pos.startswith('NN') and len(word) > 2]
            # Filter nouns that look like technical terms
            tech_nouns = [noun for noun in nouns if self.looks_like_skill(noun)]
            skills.update([noun.title() for noun in tech_nouns])
        except Exception as e:
            print(f"Noun extraction failed: {e}")
        
        # Method 5: Look for capitalized technical terms (common in resumes)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for term in capitalized_terms:
            if self.looks_like_skill(term) and len(term) < 30:
                skills.add(term)
        
        return sorted(list(skills), key=lambda x: x.lower())

    def clean_skill(self, skill: str) -> str:
        """Clean and normalize a skill string"""
        # Remove common prefixes and suffixes
        skill = re.sub(r'^(strong|expert|basic|intermediate|advanced)\s+', '', skill.lower())
        skill = re.sub(r'\s+(skills?|knowledge|experience|proficiency)$', '', skill)
        
        # Remove extra whitespace and capitalize properly
        skill = ' '.join(skill.split())
        skill = skill.title()
        
        # Common skill normalizations
        skill_replacements = {
            'Javascript': 'JavaScript',
            'Typescript': 'TypeScript',
            'C++': 'C++',
            'C#': 'C#',
            'Node.Js': 'Node.js',
            'React.Js': 'React',
            'Vue.Js': 'Vue.js',
            'Html': 'HTML',
            'Css': 'CSS',
            'Sql': 'SQL',
            'Nosql': 'NoSQL',
            'Api': 'API',
            'Rest Api': 'REST API',
            'Graphql': 'GraphQL',
            'Ai': 'AI',
            'Ml': 'Machine Learning'
        }
        
        return skill_replacements.get(skill, skill)

    def looks_like_skill(self, word: str) -> bool:
        """Check if a word looks like a technical skill"""
        word_lower = word.lower()
        
        # Common non-skill words to exclude
        excluded_words = {
            'company', 'university', 'college', 'school', 'project', 'team',
            'year', 'years', 'month', 'months', 'client', 'customer', 'user',
            'system', 'service', 'application', 'software', 'technology',
            'solution', 'product', 'management', 'development', 'engineering'
        }
        
        if word_lower in excluded_words:
            return False
        
        # Check if it matches any of our skill patterns
        for pattern in self.technical_skills_patterns + self.soft_skills_patterns:
            if re.search(pattern, word_lower):
                return True
        
        # Check for common skill indicators
        skill_indicators = [
            r'\b\w+\.js$', r'\b\w+\.net$', r'\b\w+script$', r'\b\w+sql$',
            r'^[A-Z][a-z]+[A-Z]',  # CamelCase
            r'^[A-Z]+$'  # All caps (like API, CSS, HTML)
        ]
        
        return any(re.search(indicator, word) for indicator in skill_indicators)

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