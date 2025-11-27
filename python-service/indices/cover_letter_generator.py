"""
Enhanced Cover Letter Generator using RAG and AI.
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

class EnhancedCoverLetterGenerator:
    """
    AI-powered cover letter generator using RAG (Retrieval Augmented Generation).
    """
    
    def __init__(self):
        self.ai_service = get_ai_service()
        self._initialize_cover_letter_examples()
    
    def _initialize_cover_letter_examples(self):
        """Initialize the knowledge base with successful cover letter examples."""
        # In a real implementation, you'd load these from a database
        example_cover_letters = [
            {
                "content": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Senior Software Engineer position at TechCorp. With over 5 years of experience in Python and React development, I am confident in my ability to contribute to your team's success.\n\nIn my current role at StartupABC, I led the development of a microservices architecture that improved system performance by 40%. My expertise in AWS cloud services and DevOps practices aligns perfectly with your requirements for scalable solution development.\n\nI am particularly drawn to TechCorp's commitment to innovation and would welcome the opportunity to discuss how my technical leadership and problem-solving skills can benefit your engineering team.\n\nSincerely,\nJohn Developer",
                "job_title": "Senior Software Engineer",
                "industry": "Technology",
                "experience_level": "Senior",
                "tone": "Professional",
                "key_skills": ["Python", "React", "AWS", "Microservices", "DevOps"],
                "success_metrics": {"response_rate": 0.85, "interview_rate": 0.65}
            },
            {
                "content": "Dear [Hiring Manager Name],\n\nI am excited to apply for the Product Manager position at InnovateCorp. Your recent product launch in the AI space caught my attention, and I believe my background in both technology and product strategy makes me an ideal candidate.\n\nDuring my tenure at TechSolutions, I successfully managed a cross-functional team of 12 people and delivered 3 major product releases that increased user engagement by 60%. My analytical approach to product decisions, combined with strong stakeholder management skills, has consistently driven results.\n\nI am passionate about building products that solve real user problems, and I would love to bring this passion to InnovateCorp's innovative team.\n\nBest regards,\nSarah Product",
                "job_title": "Product Manager",
                "industry": "Technology",
                "experience_level": "Mid-Level",
                "tone": "Enthusiastic",
                "key_skills": ["Product Management", "Analytics", "Leadership", "Stakeholder Management"],
                "success_metrics": {"response_rate": 0.78, "interview_rate": 0.55}
            }
        ]
        
        try:
            # Convert examples to documents and index them
            cover_letter_docs = []
            for i, example in enumerate(example_cover_letters):
                doc = Document(
                    text=example["content"],
                    metadata={
                        "example_id": f"cl_example_{i}",
                        "job_title": example["job_title"],
                        "industry": example["industry"],
                        "experience_level": example["experience_level"],
                        "tone": example["tone"],
                        "key_skills": example["key_skills"],
                        "response_rate": example["success_metrics"]["response_rate"],
                        "interview_rate": example["success_metrics"]["interview_rate"]
                    }
                )
                cover_letter_docs.append(doc)
            
            # Index the examples
            self.ai_service.create_index_from_documents(cover_letter_docs, "cover_letters")
            logger.info("Cover letter examples indexed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cover letter examples: {e}")
    
    def generate_cover_letter(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a personalized cover letter using RAG.
        
        Args:
            resume_data: Parsed resume information
            job_data: Job description and requirements
            preferences: User preferences (tone, focus areas, etc.)
            
        Returns:
            Generated cover letter with metadata
        """
        try:
            # Set default preferences
            preferences = preferences or {}
            tone = preferences.get("tone", "professional")
            focus = preferences.get("focus", "technical")  # technical, leadership, results
            length = preferences.get("length", "medium")  # short, medium, long
            
            # Add variation seed to ensure different outputs each time
            import random
            import time
            import os
            # Combine timestamp, process id, and random for better uniqueness
            if "seed" not in preferences:
                variation_seed = int(time.time() * 1000000) % 100000 + os.getpid() + random.randint(0, 10000)
            else:
                seed_val = preferences.get("seed")
                variation_seed = int(seed_val) if seed_val is not None else int(time.time() * 1000000) % 100000
            random.seed(variation_seed)
            
            # Retrieve relevant cover letter examples
            relevant_examples = self._retrieve_relevant_examples(job_data, resume_data)
            
            # Generate personalized cover letter with variation
            cover_letter = self._generate_personalized_letter(
                resume_data, 
                job_data, 
                relevant_examples, 
                tone, 
                focus, 
                length,
                variation_seed
            )
            
            # Analyze and score the generated letter
            quality_analysis = self._analyze_cover_letter_quality(cover_letter, job_data)
            
            # Determine which variation strategy was used
            import random
            random.seed(variation_seed)
            variation_strategies = [
                "achievement-focused", "passion-driven", "problem-solver", 
                "story-telling", "direct-value"
            ]
            strategy_used = variation_strategies[variation_seed % len(variation_strategies)]
            
            return {
                "success": True,
                "cover_letter": cover_letter,
                "quality_analysis": quality_analysis,
                "examples_used": len(relevant_examples),
                "preferences_applied": {
                    "tone": tone,
                    "focus": focus,
                    "length": length
                },
                "variation_info": {
                    "strategy": strategy_used,
                    "seed": variation_seed,
                    "note": "Each generation uses a different approach for variety"
                },
                "metadata": {
                    "generated_at": "2025-11-10",  # In production, use actual timestamp
                    "resume_id": resume_data.get("resume_id"),
                    "job_id": job_data.get("job_id"),
                    "word_count": len(cover_letter.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_multiple_variations(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple cover letter variations with different approaches.
        
        Args:
            resume_data: Parsed resume information  
            job_data: Job description and requirements
            
        Returns:
            Multiple cover letter variations
        """
        try:
            variations = []
            
            # Generate different variations
            variation_configs = [
                {"tone": "professional", "focus": "technical", "length": "medium", "name": "Technical Focus"},
                {"tone": "enthusiastic", "focus": "results", "length": "medium", "name": "Results-Driven"},
                {"tone": "formal", "focus": "leadership", "length": "long", "name": "Leadership Emphasis"},
                {"tone": "conversational", "focus": "cultural", "length": "short", "name": "Cultural Fit"}
            ]
            
            for config in variation_configs:
                result = self.generate_cover_letter(resume_data, job_data, config)
                if result["success"]:
                    variations.append({
                        "name": config["name"],
                        "cover_letter": result["cover_letter"],
                        "quality_score": result["quality_analysis"]["overall_score"],
                        "tone": config["tone"],
                        "focus": config["focus"],
                        "length": config["length"],
                        "word_count": len(result["cover_letter"].split())
                    })
            
            # Rank variations by quality
            variations.sort(key=lambda x: x["quality_score"], reverse=True)
            
            return {
                "success": True,
                "variations": variations,
                "total_variations": len(variations),
                "recommended_variation": variations[0] if variations else None
            }
            
        except Exception as e:
            logger.error(f"Multiple variations generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_cover_letter(self, cover_letter_text: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize an existing cover letter for better alignment with job requirements.
        
        Args:
            cover_letter_text: Current cover letter content
            job_data: Job description and requirements
            
        Returns:
            Optimized cover letter with suggestions
        """
        try:
            # Create documents for analysis
            letter_doc = Document(text=cover_letter_text, metadata={"type": "cover_letter"})
            job_doc = Document(
                text=f"Job Title: {job_data.get('title', '')} | Description: {job_data.get('description', '')} | Requirements: {' '.join(job_data.get('requirements', []))}",
                metadata={"type": "job"}
            )
            
            # Create index for optimization analysis
            index = self.ai_service.create_index_from_documents([letter_doc, job_doc], "cover_letters")
            query_engine = index.as_query_engine()
            
            optimization_query = f"""
            Analyze this cover letter for the {job_data.get('title', 'position')} and provide specific optimization recommendations:
            
            1. Keyword alignment with job requirements
            2. Structure and flow improvements
            3. Quantification opportunities
            4. Tone and style adjustments
            5. Content gaps to address
            6. Sections to strengthen or remove
            
            Provide an optimized version and explain the changes made.
            """
            
            optimization_response = query_engine.query(optimization_query)
            optimization_text = _safe_get_response(optimization_response)
            
            return {
                "success": True,
                "optimization_analysis": optimization_text,
                "original_letter": cover_letter_text,
                "suggestions": self._extract_optimization_suggestions(optimization_text),
                "optimized_version": self._extract_optimized_letter(optimization_text)
            }
            
        except Exception as e:
            logger.error(f"Cover letter optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _retrieve_relevant_examples(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant cover letter examples using semantic search."""
        try:
            # Create query based on job and resume data
            job_title = job_data.get('title', '')
            skills = resume_data.get('skills', [])[:5]  # Top 5 skills
            query_text = f"Cover letter for {job_title} position with skills: {', '.join(skills)}"
            
            # Get query engine for cover letter examples
            query_engine = self.ai_service.get_query_engine("cover_letters", similarity_top_k=3)
            
            # Retrieve similar examples
            examples_response = query_engine.query(query_text)
            
            # Parse actual results from the response
            examples = []
            if hasattr(examples_response, 'source_nodes'):
                for node in examples_response.source_nodes[:3]:  # Top 3 examples
                    example = {
                        "content": node.get_text() if hasattr(node, 'get_text') else str(node),
                        "job_title": node.metadata.get('job_title', '') if hasattr(node, 'metadata') else '',
                        "success_rate": node.metadata.get('response_rate', 0.0) if hasattr(node, 'metadata') else 0.0,
                        "similarity_score": node.score if hasattr(node, 'score') else 0.0
                    }
                    examples.append(example)
            
            return examples if examples else []
            
        except Exception as e:
            logger.error(f"Failed to retrieve examples: {e}")
            return []
    
    def _research_company(self, company_name: str, job_description: str) -> Dict[str, str]:
        """Extract company insights from job description."""
        try:
            if not company_name:
                return {
                    "mission": "innovation and excellence",
                    "values": "quality and customer satisfaction",
                    "culture": "collaborative and growth-oriented"
                }
            
            # Use AI to extract company insights from job description
            prompt = f"""Analyze this job description and extract key information about the company:

Job Description:
{job_description[:1000]}

Extract and provide:
1. Company mission or focus (1 sentence)
2. Company values (2-3 key values)
3. Company culture indicators (1 sentence)

Format your response as:
MISSION: <mission statement>
VALUES: <value1>, <value2>, <value3>
CULTURE: <culture description>
"""
            
            response = self.ai_service.llm.complete(prompt)
            response_text = response.text.strip()
            
            # Parse the response
            insights = {
                "mission": "innovation and excellence",
                "values": "quality and customer satisfaction",
                "culture": "collaborative and growth-oriented"
            }
            
            for line in response_text.split('\n'):
                if line.startswith('MISSION:'):
                    insights['mission'] = line.replace('MISSION:', '').strip()
                elif line.startswith('VALUES:'):
                    insights['values'] = line.replace('VALUES:', '').strip()
                elif line.startswith('CULTURE:'):
                    insights['culture'] = line.replace('CULTURE:', '').strip()
            
            return insights
            
        except Exception as e:
            logger.error(f"Company research failed: {e}")
            return {
                "mission": "innovation and excellence",
                "values": "quality and customer satisfaction",
                "culture": "collaborative and growth-oriented"
            }
    
    def _extract_quantifiable_achievements(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract quantifiable achievements from experience."""
        achievements = []
        
        # Look for numbers, percentages, metrics in experience descriptions
        import re
        
        for exp in experience[:3]:
            description = exp.get('description', '')
            if not description:
                continue
            
            # Find sentences with numbers or percentages
            sentences = description.split('.')
            for sentence in sentences:
                # Check for quantifiable achievements
                if any(pattern in sentence.lower() for pattern in [
                    'increased', 'decreased', 'improved', 'reduced', 'grew',
                    'achieved', 'delivered', 'saved', 'generated', 'led'
                ]):
                    # Check if it has numbers
                    if re.search(r'\d+[%x\$]?|\d+\s*(percent|users|customers|projects)', sentence, re.I):
                        achievement = sentence.strip()
                        if len(achievement) > 20 and len(achievement) < 200:
                            achievements.append(achievement)
        
        return achievements[:3]  # Top 3 achievements
    
    def _is_recent_graduate(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if candidate is a recent graduate with limited or no work experience.
        
        Returns:
            Dict with:
                - is_graduate: bool
                - graduation_year: int or None
                - has_relevant_experience: bool
                - academic_projects: List[str]
                - technical_skills_learned: List[str]
        """
        from datetime import datetime
        import re
        
        experience = resume_data.get("experience", [])
        education = resume_data.get("education", [])
        skills = resume_data.get("skills", [])
        
        # Check graduation year
        current_year = datetime.now().year
        graduation_year = None
        latest_education = None
        
        for edu in education:
            # Look for graduation year in various fields
            for field in ['graduation_year', 'year', 'end_date', 'dates', 'details']:
                text = str(edu.get(field, ''))
                years = re.findall(r'20\d{2}', text)
                if years:
                    year = int(years[-1])  # Take the latest year
                    if not graduation_year or year > graduation_year:
                        graduation_year = year
                        latest_education = edu
        
        # Criteria for recent graduate
        is_recent = False
        if graduation_year and (current_year - graduation_year) <= 2:
            is_recent = True
        
        # Check work experience quantity and relevance
        has_significant_experience = False
        total_experience_months = 0
        
        for exp in experience:
            duration_text = exp.get('duration', '')
            # Try to parse duration
            years_match = re.search(r'(\d+)\s*(?:year|yr)', duration_text, re.I)
            months_match = re.search(r'(\d+)\s*(?:month|mo)', duration_text, re.I)
            
            if years_match:
                total_experience_months += int(years_match.group(1)) * 12
            if months_match:
                total_experience_months += int(months_match.group(1))
        
        # Less than 18 months of experience = limited experience
        if total_experience_months > 18:
            has_significant_experience = True
        
        # Also check if experience list is short or contains internships/student jobs
        if len(experience) <= 2:
            internship_keywords = ['intern', 'trainee', 'student', 'volunteer', 'freelance', 'project']
            for exp in experience:
                title = exp.get('title', '').lower()
                if any(keyword in title for keyword in internship_keywords):
                    # Mostly internships/student work
                    has_significant_experience = False
                    break
        
        # Extract academic projects from education
        academic_projects = []
        for edu in education:
            projects = edu.get('projects', [])
            if isinstance(projects, list):
                academic_projects.extend(projects)
            elif isinstance(projects, str) and projects:
                academic_projects.append(projects)
            
            # Also check in details
            details = edu.get('details', '')
            if 'project' in details.lower():
                # Extract project mentions
                project_sentences = [s.strip() for s in details.split('.') if 'project' in s.lower()]
                academic_projects.extend(project_sentences[:3])
        
        # Identify technical/academic skills
        technical_keywords = [
            'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css',
            'machine learning', 'data science', 'algorithms', 'data structures',
            'web development', 'mobile development', 'cloud', 'database',
            'git', 'agile', 'testing', 'debugging', 'programming'
        ]
        
        technical_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in technical_keywords):
                technical_skills.append(skill)
        
        return {
            "is_graduate": is_recent and not has_significant_experience,
            "graduation_year": graduation_year,
            "has_relevant_experience": has_significant_experience,
            "academic_projects": academic_projects[:5],  # Top 5 projects
            "technical_skills_learned": technical_skills[:10],  # Top 10 technical skills
            "latest_degree": latest_education.get('degree', '') if latest_education else '',
            "latest_institution": latest_education.get('institution', '') if latest_education else ''
        }
    
    def _generate_personalized_letter(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], examples: List[Dict[str, Any]], tone: str, focus: str, length: str, variation_seed: int = 0) -> str:
        """Generate personalized cover letter using AI with variation."""
        try:
            import random
            import re
            random.seed(variation_seed)
            
            # Extract comprehensive candidate information
            personal_info = resume_data.get("personal_info", {})
            candidate_name = personal_info.get("name", "")
            candidate_email = personal_info.get("email", "")
            candidate_phone = personal_info.get("phone", "")
            
            contact_info = resume_data.get("contact_info", {})
            linkedin = contact_info.get("linkedin", "")
            github = contact_info.get("github", "")
            portfolio = contact_info.get("portfolio", "")
            
            # Get raw skills and deduplicate aggressively
            raw_skills = resume_data.get("skills", [])
            skills_dedup = []
            seen_skills_normalized = []
            
            for skill in raw_skills:
                if not skill:
                    continue
                    
                skill_clean = skill.strip()
                if len(skill_clean) < 2:
                    continue
                
                skill_lower = skill_clean.lower()
                
                # Check for duplicates or substrings
                is_duplicate = False
                for seen_skill in seen_skills_normalized:
                    # Skip if exact match
                    if skill_lower == seen_skill:
                        is_duplicate = True
                        break
                    
                    # Skip if one is substring of another (e.g., "Agile" vs "Agile Methodology")
                    if skill_lower in seen_skill or seen_skill in skill_lower:
                        # Keep the shorter, more general term
                        if len(skill_lower) < len(seen_skill):
                            # Replace with shorter term
                            idx = seen_skills_normalized.index(seen_skill)
                            skills_dedup[idx] = skill_clean
                            seen_skills_normalized[idx] = skill_lower
                        is_duplicate = True
                        break
                    
                    # Skip if very similar (share most words)
                    skill_words = set(skill_lower.split())
                    seen_words = set(seen_skill.split())
                    if skill_words and seen_words:
                        overlap = len(skill_words & seen_words) / max(len(skill_words), len(seen_words))
                        if overlap > 0.7:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    skills_dedup.append(skill_clean)
                    seen_skills_normalized.append(skill_lower)
            
            skills = skills_dedup[:25]  # Limit to top 25 unique skills
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            
            # CRITICAL: Detect if candidate is a recent graduate
            graduate_info = self._is_recent_graduate(resume_data)
            is_recent_graduate = graduate_info["is_graduate"]
            
            # Add variation by selecting different skill subsets
            import random
            if len(skills) > 15:
                # Shuffle and take different subsets each time
                shuffled_skills = skills.copy()
                random.shuffle(shuffled_skills)
                skills = shuffled_skills[:15]
            
            # Extract quantifiable achievements
            achievements = self._extract_quantifiable_achievements(experience)
            
            # Build detailed experience summary
            experience_details = []
            for exp in experience[:3]:  # Top 3 experiences
                title = exp.get("title", "")
                company = exp.get("company", "")
                description = exp.get("description", "")
                if title:
                    exp_str = f"{title}"
                    if company:
                        exp_str += f" at {company}"
                    if description:
                        exp_str += f": {description[:200]}"
                    experience_details.append(exp_str)
            
            # Build education summary
            education_details = []
            for edu in education:
                institution = edu.get("institution", "")
                degree = edu.get("degree", "")
                details = edu.get("details", "")
                if institution:
                    edu_str = institution
                    if degree:
                        edu_str += f" - {degree}"
                    if details:
                        edu_str += f" ({details})"
                    education_details.append(edu_str)
            
            # Job information with better fallbacks and validation
            job_title = job_data.get("title", "") or job_data.get("job_title", "")
            company_name = job_data.get("company", "") or job_data.get("company_name", "")
            location = job_data.get("location", "")
            required_skills = job_data.get("required_skills", []) or job_data.get("skills", [])
            experience_level = job_data.get("experience_level", "") or job_data.get("level", "")
            responsibilities = job_data.get("responsibilities", []) or job_data.get("description", "").split(".")[:5]
            job_description = job_data.get("description", "") or job_data.get("job_description", "")
            
            # Clean and validate job title
            if job_title:
                job_title = job_title.strip()
                # Remove any corrupted fragments
                job_title = re.sub(r'\s+', ' ', job_title)
            if not job_title or job_title.lower() in ["", "this position", "the position", "position"]:
                job_title = "this role"
            
            # Clean and validate company name - more aggressive validation
            if company_name:
                company_name = company_name.strip()
                # Fix common corruptions where location got mixed with company name
                # e.g., "ion Nairobi Kenya" should be just the company or a proper name
                if re.match(r'^[a-z]{2,4}\s+[A-Z]', company_name):
                    # Looks like corruption (starts with lowercase fragment + location)
                    # Try to extract proper company name or use generic
                    if location:
                        company_name = "the company"
                    else:
                        company_name = "your organization"
                # Remove location from company name if accidentally included
                if location and location in company_name:
                    company_name = company_name.replace(location, "").strip()
            
            if not company_name or company_name.lower() in ["", "your company", "your organization", "ion", "the company"]:
                company_name = "your organization"
            
            # Additional safeguard: if company name is suspiciously short (< 3 chars), use generic
            if len(company_name) < 3:
                company_name = "your organization"
            
            # Research company insights
            company_insights = self._research_company(company_name, job_description)
            
            # Define variation strategies for different cover letter approaches
            variation_strategies = [
                {
                    "approach": "achievement-focused",
                    "opening": "Lead with a strong achievement that demonstrates impact",
                    "emphasis": "Quantifiable results and measurable outcomes"
                },
                {
                    "approach": "passion-driven",
                    "opening": "Express genuine excitement about the company's mission",
                    "emphasis": "Alignment with company values and cultural fit"
                },
                {
                    "approach": "problem-solver",
                    "opening": "Identify a challenge the company faces and position yourself as the solution",
                    "emphasis": "How your skills solve their specific problems"
                },
                {
                    "approach": "story-telling",
                    "opening": "Start with a brief relevant anecdote or career moment",
                    "emphasis": "Your professional journey and how it led to this opportunity"
                },
                {
                    "approach": "direct-value",
                    "opening": "Immediately state the unique value you bring",
                    "emphasis": "Your distinctive combination of skills and experience"
                }
            ]
            
            # Select variation strategy based on seed
            import random
            selected_strategy = variation_strategies[variation_seed % len(variation_strategies)]
            
            # Define tone-specific guidelines
            tone_guidelines = {
                "professional": {
                    "style": "formal, business-like, and respectful",
                    "greeting": "Dear Hiring Manager,",
                    "closing": "Sincerely,",
                    "language": "Use formal language, avoid contractions, focus on accomplishments and qualifications"
                },
                "enthusiastic": {
                    "style": "energetic, passionate, and engaging",
                    "greeting": "Dear Hiring Team,",
                    "closing": "With enthusiasm,",
                    "language": "Use active voice, show excitement, express genuine interest and passion for the role"
                },
                "formal": {
                    "style": "traditional, highly professional, and ceremonious",
                    "greeting": "Dear Sir or Madam,",
                    "closing": "Yours faithfully,",
                    "language": "Use traditional business language, maintain utmost professionalism, emphasize credentials"
                },
                "conversational": {
                    "style": "friendly, approachable, yet professional",
                    "greeting": "Hello Hiring Team,",
                    "closing": "Best regards,",
                    "language": "Use natural language, be personable while maintaining professionalism, show personality"
                }
            }
            
            tone_guide = tone_guidelines.get(tone.lower(), tone_guidelines["professional"])
            
            # Create comprehensive prompt with ALL resume details
            prompt = f"""
            Generate a highly personalized and detailed cover letter for this job application using the following information:

            === CANDIDATE INFORMATION ===
            Name: {candidate_name}
            Email: {candidate_email}
            Phone: {candidate_phone}
            LinkedIn: {linkedin}
            GitHub: {github}
            Portfolio: {portfolio}

            === CANDIDATE SKILLS (Top Skills) ===
            {', '.join(skills[:15]) if skills else 'No specific skills listed'}

            === WORK EXPERIENCE (Detailed) ===
            {chr(10).join(f"• {exp}" for exp in experience_details) if experience_details else '• No work experience listed'}

            === KEY ACHIEVEMENTS (Quantifiable) ===
            {chr(10).join(f"• {ach}" for ach in achievements) if achievements else '• Use achievements from experience descriptions'}

            === EDUCATION ===
            {chr(10).join(f"• {edu}" for edu in education_details) if education_details else '• No education listed'}

            === JOB DETAILS ===
            Position: {job_title}
            Company: {company_name}
            Experience Level: {experience_level}
            Required Skills: {', '.join(required_skills[:10]) if required_skills else 'Not specified'}
            Key Responsibilities: {', '.join(responsibilities[:5]) if responsibilities else 'Not specified'}

            === CANDIDATE PROFILE TYPE ===
            {"🎓 RECENT GRADUATE / ENTRY-LEVEL CANDIDATE" if is_recent_graduate else "💼 EXPERIENCED PROFESSIONAL"}
            {"Graduation Year: " + str(graduate_info['graduation_year']) if is_recent_graduate and graduate_info['graduation_year'] else ""}
            {"Degree: " + graduate_info['latest_degree'] if is_recent_graduate and graduate_info['latest_degree'] else ""}
            {"Institution: " + graduate_info['latest_institution'] if is_recent_graduate and graduate_info['latest_institution'] else ""}
            {f"Academic Projects:{chr(10)}{chr(10).join(f'  • {proj}' for proj in graduate_info['academic_projects'][:3])}" if is_recent_graduate and graduate_info['academic_projects'] else ""}
            {f"Technical Skills from Education: {', '.join(graduate_info['technical_skills_learned'][:8])}" if is_recent_graduate and graduate_info['technical_skills_learned'] else ""}

            === COMPANY INSIGHTS ===
            Mission: {company_insights['mission']}
            Values: {company_insights['values']}
            Culture: {company_insights['culture']}

            === COVER LETTER REQUIREMENTS ===
            Tone: {tone} - {tone_guide['style']}
            Greeting: {tone_guide['greeting']}
            Closing: {tone_guide['closing']}
            Language Style: {tone_guide['language']}
            Focus Area: {focus} (emphasize {focus} aspects in the letter)
            Length Target: {length} (short=250 words, medium=350-400 words, long=450-500 words)

            === VARIATION STRATEGY (Use This Approach) ===
            Approach: {selected_strategy['approach']}
            Opening Style: {selected_strategy['opening']}
            Main Emphasis: {selected_strategy['emphasis']}
            
            IMPORTANT: Follow this variation strategy to create a UNIQUE cover letter that differs from typical templates.
            Do NOT use generic phrases. Make it specific and personalized.

            === DETAILED INSTRUCTIONS ===
            Write a compelling, personalized, and contextually rich cover letter that:

            STRUCTURE:
            1. **Opening Paragraph**: 
               - Start with {tone_guide['greeting']}
               - APPLY THE VARIATION STRATEGY: {selected_strategy['opening']}
               - Express clear interest in the {job_title} position at {company_name}
               - Make it unique and memorable, not generic
            
            2. **Body Paragraph 1 - {"Academic Background & Technical Skills" if is_recent_graduate else "Skills & Experience Match"}**:
               {"FOR RECENT GRADUATES:" if is_recent_graduate else ""}
               {"- Emphasize your degree from " + graduate_info['latest_institution'] + " and graduation year" if is_recent_graduate and graduate_info['latest_institution'] else ""}
               {"- Highlight 4-5 technical skills you MASTERED through coursework, labs, and academic projects" if is_recent_graduate else "- Highlight 3-4 specific skills from your background that directly match job requirements"}
               {"- Reference specific academic projects that demonstrate practical application of these skills" if is_recent_graduate else "- Use the KEY ACHIEVEMENTS section to provide concrete quantifiable examples"}
               {"- Use project examples with concrete outcomes (e.g., 'Built a web app that...', 'Developed an algorithm that...')" if is_recent_graduate else "- Include specific metrics, percentages, or numbers from achievements"}
               {"- Connect your academic preparation and project work to job requirements" if is_recent_graduate else "- Connect your experience to the company's needs"}
               {"- Show how your coursework and projects prepared you for this role" if is_recent_graduate else "- Show measurable impact you've made in previous roles"}
               {"- Emphasize your proficiency and readiness to apply learned skills in a professional setting" if is_recent_graduate else ""}
            
            3. **Body Paragraph 2 - {"Learning Ability & Enthusiasm" if is_recent_graduate else "Value Proposition & Cultural Fit"}**:
               {"FOR RECENT GRADUATES:" if is_recent_graduate else ""}
               {"- Emphasize your quick learning ability and adaptability as a recent graduate" if is_recent_graduate else "- Explain what unique value you bring to the role"}
               {"- Express genuine enthusiasm and passion for entering the field professionally" if is_recent_graduate else ""}
               {"- Highlight any internships, hackathons, coding competitions, or volunteer work" if is_recent_graduate else ""}
               {"- Showcase your up-to-date knowledge of modern technologies and industry trends" if is_recent_graduate else ""}
               {"- Demonstrate eagerness to contribute fresh perspectives and innovative ideas" if is_recent_graduate else ""}
               - Reference company mission: {company_insights['mission']}
               - Align with company values: {company_insights['values']}
               - Show cultural fit: {company_insights['culture']}
               {"- Express willingness to grow with the company and commitment to continuous learning" if is_recent_graduate else "- Show how your career goals align with the company's direction"}
               {"- Mention specific courses, certifications, or online learning that prepared you" if is_recent_graduate else "- Mention specific projects, technologies, or methodologies relevant to the role"}
            
            4. **Closing Paragraph**:
               - Reiterate enthusiasm for the opportunity
               - Include a strong call to action (requesting an interview)
               - Thank the reader for their consideration
               - End with {tone_guide['closing']}
               - Include full contact details

            TONE & STYLE:
            - Maintain consistent {tone} tone throughout: {tone_guide['language']}
            - Use active voice and strong action verbs
            - Be specific and detailed, not generic
            - Show genuine personality while remaining professional
            - Avoid clichés like "I am writing to apply" or "I believe I would be a good fit"
            - Vary sentence structure (mix short and long sentences)
            - Use different transition words and phrases
            - Make each paragraph flow naturally but differently from typical cover letters

            CONTENT REQUIREMENTS:
            {"FOR RECENT GRADUATES - SPECIAL FOCUS:" if is_recent_graduate else ""}
            {"- EMPHASIZE academic projects with concrete examples (e.g., 'Developed a full-stack e-commerce platform using React and Node.js')" if is_recent_graduate else "- Include at least 2-3 specific examples from work experience"}
            {"- Highlight PROFICIENCY in technical skills learned in school with specific examples of application" if is_recent_graduate else ""}
            {"- Reference 2-3 academic projects that demonstrate job-relevant skills" if is_recent_graduate else ""}
            {"- Show how coursework prepared you (e.g., 'Through advanced algorithms course, I mastered...')" if is_recent_graduate else ""}
            {"- Mention any capstone projects, senior projects, or thesis work" if is_recent_graduate else ""}
            {"- DO NOT apologize for lack of experience - focus on what you HAVE learned and CAN do" if is_recent_graduate else ""}
            {"- Frame education as strength: 'Fresh knowledge of latest technologies', 'Up-to-date with modern practices'" if is_recent_graduate else ""}
            - Reference specific skills that match job requirements
            - Demonstrate knowledge about {company_name}
            - Reference the company's mission: {company_insights['mission']}
            - Align with company values: {company_insights['values']}
            - Show cultural understanding: {company_insights['culture']}
            - Show how your background solves their problems
            - Make it feel personal and tailored, not template-based
            {"- Use metrics from projects: lines of code, users tested, performance improvements" if is_recent_graduate else "- Use specific numbers and metrics where possible"}

            FORMAT:
            [Candidate Name]
            [Email] | [Phone] | [LinkedIn/Portfolio if available]
            [Current Date]

            [Greeting]

            [Opening paragraph]

            [Body paragraph 1]

            [Body paragraph 2]

            [Closing paragraph]

            [Closing salutation]
            [Candidate Name]

            CRITICAL ANTI-REPETITION RULES:
            1. DO NOT list skills multiple times (e.g., "Agile, Agile Methodology, CI/CD" is WRONG - just say "Agile")
            2. DO NOT use incomplete or corrupted names (e.g., "ion Location" - use full company name: {company_name})
            3. DO NOT use placeholder text like "this position position" or "the position" - ALWAYS use: {job_title}
            4. DO NOT repeat the same phrases in multiple sentences
            5. VARY your sentence structure throughout the letter
            6. ALWAYS use the FULL EXACT company name: {company_name}
            7. Select 3-4 DIFFERENT, NON-OVERLAPPING skills to highlight (if one is "Python", don't also mention "Python programming")
            8. Make each paragraph discuss DIFFERENT aspects (skills, then experience, then cultural fit)
            9. Use specific examples and metrics, not generic statements like "proven track record"
            10. This is generation #{variation_seed} - use the {selected_strategy['approach']} strategy to make it UNIQUE
            11. DO NOT include redundant parenthetical skill lists like "as a Engineer (OOP, SDLC, Agile)"
            12. When mentioning job titles from experience, don't add skill acronyms in parentheses
            
            QUALITY CHECKLIST - Verify each item:
            ✓ No repeated or similar skills (check: is "Agile" and "Agile Methodology" both there? Remove duplicates!)
            ✓ Complete company name "{company_name}" used throughout (not "ion" or fragments)
            ✓ Actual job title "{job_title}" used consistently (not "this position" or "the position")
            ✓ Specific examples with numbers/metrics from achievements
            ✓ Varied sentence structures and transitions
            ✓ Natural, conversational flow without templates
            ✓ Professional grammar and spelling
            ✓ Unique approach following {selected_strategy['approach']} strategy
            ✓ No awkward phrases like "Software Engineering Principles (OOP, SDLC, Agile Methodology, CI/CD)"
            ✓ Skills mentioned naturally in context, not as comma-separated lists in parentheses
            
            BEFORE YOU WRITE: Review the job title and company name one more time:
            - Job Title: {job_title}
            - Company Name: {company_name}
            
            NOW generate the complete, detailed, and UNIQUE cover letter with NO repetitions or placeholder text:
            """
            
            # Generate using LLM with completion
            response = self.ai_service.llm.complete(prompt)
            generated_text = response.text
            
            # Post-process to fix common issues
            generated_text = self._post_process_cover_letter(generated_text, job_data, resume_data)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Letter generation failed: {e}")
            return self._generate_fallback_letter(resume_data, job_data, tone)
    
    def _generate_fallback_letter(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], tone: str) -> str:
        """Generate a fallback cover letter using enhanced templates."""
        import re
        
        personal_info = resume_data.get("personal_info", {})
        contact_info = resume_data.get("contact_info", {})
        
        name = personal_info.get("name", "Candidate")
        email = personal_info.get("email", "")
        phone = personal_info.get("phone", "")
        linkedin = contact_info.get("linkedin", "")
        github = contact_info.get("github", "")
        
        # Get job info with validation
        job_title = job_data.get("title", "") or job_data.get("job_title", "")
        company = job_data.get("company", "") or job_data.get("company_name", "")
        
        # Validate job title
        if not job_title or job_title.strip().lower() in ["", "this position", "the position"]:
            job_title = "this role"
        
        # Validate company name
        if not company or company.strip().lower() in ["", "your company", "your organization"]:
            company = "your organization"
        
        # Deduplicate skills aggressively (same logic as main generation)
        raw_skills = resume_data.get('skills', [])
        skills_dedup = []
        seen_normalized = []
        
        for skill in raw_skills:
            if not skill or len(skill.strip()) < 2:
                continue
            
            skill_clean = skill.strip()
            skill_lower = skill_clean.lower()
            
            is_duplicate = False
            for seen in seen_normalized:
                if skill_lower == seen or skill_lower in seen or seen in skill_lower:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                skills_dedup.append(skill_clean)
                seen_normalized.append(skill_lower)
        
        skills = skills_dedup[:5]  # Top 5 unique skills
        
        experience = resume_data.get('experience', [])
        education = resume_data.get('education', [])
        
        # Detect if recent graduate
        graduate_info = self._is_recent_graduate(resume_data)
        is_recent_graduate = graduate_info["is_graduate"]
        
        # Get first experience for context
        first_exp = experience[0] if experience else {}
        current_role = first_exp.get('title', 'professional')
        current_company = first_exp.get('company', '')
        
        # Get education
        first_edu = education[0] if education else {}
        degree = first_edu.get('degree', '')
        institution = first_edu.get('institution', '')
        
        # Contact header
        contact_header = f"{name}\n"
        if email:
            contact_header += f"{email}"
        if phone:
            contact_header += f" | {phone}"
        if linkedin:
            contact_header += f"\n{linkedin}"
        if github:
            contact_header += f" | {github}"
        contact_header += "\n\nDate: November 10, 2025\n\n"
        
        # Get matching skills (deduplicated)
        required_skills = job_data.get('required_skills', [])
        if required_skills:
            matching_skills = []
            for skill in skills:
                for req in required_skills:
                    if req.lower() in skill.lower() or skill.lower() in req.lower():
                        if skill not in matching_skills:
                            matching_skills.append(skill)
                            break
            if not matching_skills:
                matching_skills = skills[:3]
        else:
            matching_skills = skills[:3]
        
        # Further deduplicate matching skills
        final_skills = []
        final_normalized = []
        for skill in matching_skills[:3]:  # Max 3 skills
            skill_lower = skill.lower()
            if not any(skill_lower in s or s in skill_lower for s in final_normalized):
                final_skills.append(skill)
                final_normalized.append(skill_lower)
        
        matching_skills = final_skills
        
        # SPECIAL CASE: Recent Graduate Template
        if is_recent_graduate:
            academic_projects = graduate_info.get("academic_projects", [])
            technical_skills = graduate_info.get("technical_skills_learned", [])
            
            # Build skill list emphasizing learned competencies
            skill_list = ', '.join(matching_skills[:3]) if matching_skills else 'programming and problem-solving'
            
            # Get 2-3 key projects
            project_examples = []
            for proj in academic_projects[:2]:
                if len(proj) > 20:  # Skip very short ones
                    project_examples.append(proj)
            
            project_text = ""
            if project_examples:
                if len(project_examples) == 1:
                    project_text = f"During my studies, I {project_examples[0][0].lower() + project_examples[0][1:]}"
                else:
                    project_text = f"My academic projects included {project_examples[0].lower()}, and {project_examples[1].lower()}"
            
            letter = f"""{contact_header}Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. As a recent graduate with a {degree} from {institution}, I am eager to apply my technical skills and fresh knowledge to contribute meaningfully to your team.

Throughout my academic journey, I developed strong proficiency in {skill_list} through comprehensive coursework and hands-on projects. {project_text}. These experiences have equipped me with practical skills in software development, problem-solving, and working with modern technologies.

What sets me apart is my combination of up-to-date technical knowledge, strong work ethic, and genuine enthusiasm for the field. I am a quick learner who thrives in collaborative environments and is committed to continuous improvement. While I am at the beginning of my professional career, I bring fresh perspectives, dedication, and a solid foundation in {'the technical skills' if technical_skills else 'computer science principles'} that are essential for this role.

I am particularly drawn to {company}'s innovative approach and would welcome the opportunity to contribute to your team's success. I am confident that my academic preparation, combined with my passion for technology, makes me a strong candidate for this position.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company}.

Sincerely,
{name}"""
            
            # Apply post-processing
            letter = self._post_process_cover_letter(letter, job_data, resume_data)
        
        elif tone.lower() == "enthusiastic":
            # Use skills smartly without repetition
            skill_list = ', '.join(matching_skills[:2]) if len(matching_skills) >= 2 else matching_skills[0] if matching_skills else 'key technologies'
            
            letter = f"""{contact_header}Dear Hiring Team,

I am excited to apply for the {job_title} position at {company}! As a passionate {current_role}, I've been following {company}'s innovative work and I'm thrilled about the opportunity to contribute to your team.

Throughout my career, I've developed strong expertise in {skill_list}, which aligns perfectly with this role's requirements. {f"In my current position at {current_company}, I've " if current_company else "I've "}successfully delivered projects that demonstrate my ability to make an immediate impact. {f"My {degree} from {institution} " if degree and institution else "My educational background "}has provided me with a solid foundation in the technical and analytical skills needed for this position.

What excites me most about {company} is your commitment to innovation and excellence. I am confident that my technical skills, combined with my enthusiasm and dedication, would make me a valuable addition to your team. I'm particularly drawn to the opportunity to work on challenging projects and contribute to your company's continued success.

I would love to discuss how my background and passion can benefit {company}. Thank you for considering my application, and I look forward to the opportunity to speak with you soon!

With enthusiasm,
{name}"""
            
            # Apply post-processing
            letter = self._post_process_cover_letter(letter, job_data, resume_data)
        
        elif tone.lower() == "formal":
            # Build skill phrases without repetition
            skill_list = ', '.join(matching_skills[:2]) if len(matching_skills) >= 2 else matching_skills[0] if matching_skills else 'relevant technologies and methodologies'
            
            letter = f"""{contact_header}Dear Sir or Madam,

I am writing to formally submit my application for the {job_title} position at {company}. I believe my professional qualifications and experience make me an excellent candidate for this role.

I currently serve as a {current_role}{f" at {current_company}" if current_company else ""}, where I have developed comprehensive expertise in {skill_list}. {f"I hold a {degree} from {institution}, which " if degree and institution else "My educational background "}has equipped me with the theoretical knowledge and practical skills necessary for success in this position. My professional experience has demonstrated my capability to deliver high-quality results and contribute meaningfully to organizational objectives.

I have thoroughly reviewed the requirements and am confident that my qualifications, combined with my proven track record of professional achievement, align well with your expectations. I am particularly qualified to address the challenges inherent in this role and would be honored to contribute my expertise to {company}'s esteemed team.

I respectfully request the opportunity to discuss my qualifications in further detail at your earliest convenience. Thank you for your consideration of my application.

Yours faithfully,
{name}"""
            
            # Apply post-processing
            letter = self._post_process_cover_letter(letter, job_data, resume_data)
        
        elif tone.lower() == "conversational":
            # Use skills naturally without repetition
            skill_phrase = ', '.join(matching_skills[:2]) if len(matching_skills) >= 2 else matching_skills[0] if matching_skills else 'various technologies'
            
            letter = f"""{contact_header}Hello Hiring Team,

I'm reaching out about the {job_title} opening at {company}. As someone who's passionate about technology and innovation, I was immediately drawn to this opportunity.

I'm currently working as a {current_role}{f" at {current_company}" if current_company else ""}, where I've had the chance to work extensively with {skill_phrase}. What I love most about my work is solving complex problems and creating solutions that make a real difference. {f"My {degree} from {institution} gave " if degree and institution else "My background has given "}me a strong technical foundation, but it's the hands-on experience that's really shaped my approach to software development.

I've been following {company}'s work, and I'm impressed by what you're building. This role seems like a perfect fit for my skills and interests. I think I could bring a lot to your team – not just technical expertise, but also a collaborative mindset and genuine enthusiasm for creating great products.

I'd love to chat more about how I can contribute to {company}. Thanks for taking the time to review my application!

Best regards,
{name}"""
            
            # Apply post-processing
            letter = self._post_process_cover_letter(letter, job_data, resume_data)
        
        else:  # professional (default)
            # Build skill phrase with variety
            if len(matching_skills) >= 2:
                skill_phrase = f"{matching_skills[0]} and {matching_skills[1]}"
            elif matching_skills:
                skill_phrase = matching_skills[0]
            else:
                skill_phrase = "software development and technology"
            
            # Pick different skills for second mention (avoid repetition)
            second_skill = matching_skills[1] if len(matching_skills) > 1 else matching_skills[0] if matching_skills else 'modern technologies'
            
            letter = f"""{contact_header}Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With my background in {skill_phrase} and proven track record as a {current_role}, I am confident in my ability to contribute effectively to your team.

In my current role{f" at {current_company}" if current_company else ""}, I have successfully developed and implemented solutions that demonstrate my technical capabilities and problem-solving skills. My experience with {second_skill} directly aligns with the requirements for this role. {f"Additionally, my {degree} from {institution} " if degree and institution else "My educational foundation "}has provided me with comprehensive knowledge in computer science principles and best practices.

I am particularly impressed by {company}'s innovative approach and commitment to excellence. I believe my technical skills, combined with my dedication to delivering high-quality results, would make me a valuable addition to your team. I am eager to contribute to {company}'s continued success.

I would welcome the opportunity to discuss how my qualifications align with your needs. Thank you for considering my application. I look forward to speaking with you.

Sincerely,
{name}"""
        
        # Apply post-processing to clean up any remaining issues
        letter = self._post_process_cover_letter(letter, job_data, resume_data)
        
        return letter
    
    def _analyze_cover_letter_quality(self, cover_letter: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of generated cover letter."""
        try:
            # Basic metrics
            word_count = len(cover_letter.split())
            paragraph_count = len([p for p in cover_letter.split('\n\n') if p.strip()])
            
            # Calculate scores
            scores = {
                "length_score": self._score_length(word_count),
                "structure_score": self._score_structure(cover_letter),
                "keyword_alignment": self._score_keyword_alignment(cover_letter, job_data),
                "personalization": self._score_personalization(cover_letter, job_data)
            }
            
            # Overall score (weighted average)
            overall_score = int(
                scores["length_score"] * 0.2 +
                scores["structure_score"] * 0.3 +
                scores["keyword_alignment"] * 0.3 +
                scores["personalization"] * 0.2
            )
            
            return {
                "overall_score": overall_score,
                "word_count": word_count,
                "paragraph_count": paragraph_count,
                "detailed_scores": scores,
                "recommendations": self._get_quality_recommendations(scores, overall_score)
            }
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {
                "overall_score": 75,
                "word_count": len(cover_letter.split()),
                "detailed_scores": {},
                "recommendations": ["Unable to perform detailed analysis"]
            }
    
    def _score_length(self, word_count: int) -> int:
        """Score based on cover letter length."""
        if 200 <= word_count <= 400:
            return 95
        elif 150 <= word_count < 200 or 400 < word_count <= 500:
            return 85
        elif 100 <= word_count < 150 or 500 < word_count <= 600:
            return 70
        else:
            return 50
    
    def _score_structure(self, cover_letter: str) -> int:
        """Score based on cover letter structure."""
        score = 50  # Base score
        
        # Check for greeting
        if "dear" in cover_letter.lower():
            score += 15
        
        # Check for introduction
        if any(phrase in cover_letter.lower() for phrase in ["writing to", "pleased to", "excited to", "interested in"]):
            score += 10
        
        # Check for body content
        if any(phrase in cover_letter.lower() for phrase in ["experience", "skills", "background", "qualified"]):
            score += 15
        
        # Check for closing
        if any(phrase in cover_letter.lower() for phrase in ["sincerely", "regards", "thank you"]):
            score += 10
        
        return min(100, score)
    
    def _score_keyword_alignment(self, cover_letter: str, job_data: Dict[str, Any]) -> int:
        """Score based on alignment with job keywords."""
        job_keywords = []
        
        # Extract keywords from job data
        if job_data.get("required_skills"):
            job_keywords.extend([skill.lower() for skill in job_data["required_skills"]])
        
        if job_data.get("title"):
            job_keywords.extend(job_data["title"].lower().split())
        
        if not job_keywords:
            return 75  # Default score if no keywords available
        
        # Count matches
        cover_letter_lower = cover_letter.lower()
        matches = sum(1 for keyword in job_keywords if keyword in cover_letter_lower)
        
        # Calculate score
        match_ratio = matches / len(job_keywords)
        return int(match_ratio * 100)
    
    def _score_personalization(self, cover_letter: str, job_data: Dict[str, Any]) -> int:
        """Score based on personalization level."""
        score = 50  # Base score
        
        # Check for company name
        company = job_data.get("company", "")
        if company and company.lower() in cover_letter.lower():
            score += 20
        
        # Check for job title
        job_title = job_data.get("title", "")
        if job_title and job_title.lower() in cover_letter.lower():
            score += 15
        
        # Check for specific details
        if any(phrase in cover_letter.lower() for phrase in ["your company", "your team", "your organization"]):
            score += 10
        
        # Check for enthusiasm indicators
        if any(phrase in cover_letter.lower() for phrase in ["excited", "passionate", "enthusiastic", "impressed"]):
            score += 5
        
        return min(100, score)
    
    def _get_quality_recommendations(self, scores: Dict[str, int], overall_score: int) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        if scores.get("length_score", 100) < 80:
            if scores["length_score"] < 70:
                recommendations.append("Consider expanding the cover letter with more specific examples")
            else:
                recommendations.append("The length is acceptable but could be optimized")
        
        if scores.get("structure_score", 100) < 80:
            recommendations.append("Improve structure with clear introduction, body, and conclusion")
        
        if scores.get("keyword_alignment", 100) < 70:
            recommendations.append("Include more keywords from the job description")
        
        if scores.get("personalization", 100) < 70:
            recommendations.append("Add more specific references to the company and role")
        
        if overall_score >= 90:
            recommendations.append("Excellent cover letter! Consider this version for your application.")
        elif overall_score >= 75:
            recommendations.append("Good cover letter with minor areas for improvement.")
        else:
            recommendations.append("Consider significant revisions to improve effectiveness.")
        
        return recommendations
    
    def _post_process_cover_letter(self, text: str, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> str:
        """Post-process generated cover letter to fix common issues."""
        import re
        
        # Fix placeholder text issues
        job_title = job_data.get("title", "") or job_data.get("job_title", "")
        company_name = job_data.get("company", "") or job_data.get("company_name", "")
        
        # Clean and validate job_title and company_name
        if job_title:
            job_title = job_title.strip()
        if company_name:
            company_name = company_name.strip()
        
        # Fix repeated "position position" or similar duplications
        text = re.sub(r'\b(position|role|job)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Replace common placeholders with proper job title
        if job_title and job_title.lower() not in ["", "this position", "the position"]:
            text = re.sub(r'\bthis position\b', job_title, text, flags=re.IGNORECASE)
            text = re.sub(r'\bthe position(?! of| at| with| in)\b', job_title, text, flags=re.IGNORECASE)
        
        # Fix incomplete or corrupted company names
        if company_name and company_name.lower() not in ["", "your company", "your organization"]:
            # Fix patterns like "ion Nairobi Kenya" where "Location" got mangled
            text = re.sub(r'\bion\s+[A-Z][\w\s]+', company_name, text)
            # Fix generic company references
            text = re.sub(r'\byour company\b', company_name, text, flags=re.IGNORECASE)
            text = re.sub(r'\byour organization\b', company_name, text, flags=re.IGNORECASE)
            text = re.sub(r'\byour esteemed organization\b', company_name, text, flags=re.IGNORECASE)
        
        # Remove duplicate skills in listings more aggressively
        # Pattern 1: Find comma-separated lists and deduplicate
        def dedupe_skills(match):
            skills_text = match.group(0)
            skills_list = [s.strip() for s in skills_text.split(',')]
            seen = set()
            seen_normalized = set()
            unique_skills = []
            
            for skill in skills_list:
                if not skill or len(skill) < 2:
                    continue
                    
                skill_normalized = skill.lower().strip()
                
                # Check if this skill or a very similar one is already added
                is_duplicate = False
                for seen_skill in seen_normalized:
                    # Check for substring matches (e.g., "Agile" vs "Agile Methodology")
                    if skill_normalized in seen_skill or seen_skill in skill_normalized:
                        is_duplicate = True
                        break
                    # Check for high similarity (same words)
                    skill_words = set(skill_normalized.split())
                    seen_words = set(seen_skill.split())
                    if skill_words and seen_words and len(skill_words & seen_words) / max(len(skill_words), len(seen_words)) > 0.7:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_skills.append(skill)
                    seen_normalized.add(skill_normalized)
            
            return ', '.join(unique_skills[:5])  # Limit to 5 skills max in any listing
        
        # Apply deduplication to skill listings (more specific pattern)
        # Match patterns like "word, word, word" where each word could have multiple words
        text = re.sub(r'\b[\w\s]+(?:,\s*[\w\s]+){2,}\b', dedupe_skills, text)
        
        # Fix specific repetitive patterns like "Agile and Agile Methodology"
        text = re.sub(r'\b(\w+)\s+and\s+\1\s+\w+', r'\1', text, flags=re.IGNORECASE)
        
        # Remove parenthetical skill repetitions like "(OOP, SDLC, Agile Methodology, CI/CD)"
        # when those skills are already mentioned in the same sentence
        def remove_redundant_parens(match):
            main_text = match.group(1)
            paren_content = match.group(2)
            
            # Extract skills from both parts
            main_skills = set(re.findall(r'\b[A-Z][a-zA-Z]+\b', main_text))
            paren_skills = [s.strip() for s in paren_content.split(',')]
            
            # Check if paren skills are already in main text
            redundant = all(any(ps.lower() in ms.lower() or ms.lower() in ps.lower() 
                               for ms in main_skills) for ps in paren_skills)
            
            if redundant:
                return main_text  # Remove parenthetical
            return match.group(0)  # Keep original
        
        text = re.sub(r'([\w\s,]+)\s*\(([^)]+)\)', remove_redundant_parens, text)
        
        # Fix awkward phrasings like "as a Software Engineering Principles (OOP...)"
        text = re.sub(r'\bas a\s+([A-Z][\w\s]+)\s+\([^)]+\)', r'as a \1', text)
        
        # Clean up multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Fix paragraph spacing (normalize to exactly 2 newlines between paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Fix lines with only whitespace
        text = re.sub(r'\n[ \t]+\n', '\n\n', text)
        
        return text.strip()
    
    def _extract_optimization_suggestions(self, response: str) -> List[str]:
        """Extract optimization suggestions from AI response."""
        suggestions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                suggestion = line[1:].strip()
                if len(suggestion) > 10:
                    suggestions.append(suggestion)
        
        return suggestions[:8]  # Limit to top 8 suggestions
    
    def _extract_optimized_letter(self, response: str) -> str:
        """Extract optimized cover letter from AI response."""
        # Look for the optimized version in the response
        # This is a simplified extraction - in production, use more sophisticated parsing
        lines = response.split('\n')
        optimized_lines = []
        in_letter_section = False
        
        for line in lines:
            if "optimized" in line.lower() or "improved" in line.lower():
                in_letter_section = True
                continue
            elif in_letter_section and line.strip():
                optimized_lines.append(line)
        
        if optimized_lines:
            return '\n'.join(optimized_lines)
        else:
            return "Optimized version not available in current response format."