from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
from dotenv import load_dotenv

# Import existing services
from resume_parser import ResumeParser
from job_analyzer import JobAnalyzer, SimilarityCalculator

# Import new AI services
from ai_services.llama_service import get_ai_service
from indices.resume_analyzer import EnhancedResumeAnalyzer
from indices.job_recommender import JobRecommender
from indices.cover_letter_generator import EnhancedCoverLetterGenerator
from indices.similarity_analyzer import EnhancedSimilarityAnalyzer

# Import ATS optimizer
from ats_optimizer import ATSOptimizer

# Import agentic optimizer
from agentic_optimizer import AgenticResumeOptimizer

# Import configuration validator
from utils.config_validator import validate_configuration, print_configuration_status

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize existing services
resume_parser = ResumeParser()
job_analyzer = JobAnalyzer()
similarity_calculator = SimilarityCalculator()

# Initialize ATS optimizer
ats_optimizer = ATSOptimizer()

# Initialize AI services
try:
    ai_service = get_ai_service()
    enhanced_resume_analyzer = EnhancedResumeAnalyzer()
    job_recommender = JobRecommender()
    cover_letter_generator = EnhancedCoverLetterGenerator()
    enhanced_similarity_analyzer = EnhancedSimilarityAnalyzer()
    agentic_optimizer = AgenticResumeOptimizer(ai_service)  # Initialize agentic agent
    ai_services_available = True
    print(" AI services initialized successfully")
    print(" Agentic optimizer ready")
except Exception as e:
    print(f" AI services initialization failed: {e}")
    print(" Falling back to basic services only")
    ai_services_available = False
    ai_service = None
    enhanced_resume_analyzer = None
    job_recommender = None
    cover_letter_generator = None
    enhanced_similarity_analyzer = None

# Create upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Resume Parser API'})

@app.route('/config-status', methods=['GET'])
def config_status():
    """Check configuration status for all AI services."""
    is_valid, missing_keys, service_status = validate_configuration()
    
    return jsonify({
        'is_valid': is_valid,
        'ai_services_available': ai_services_available,
        'missing_keys': missing_keys,
        'service_status': service_status,
        'message': 'Configuration is complete' if is_valid else 'Configuration required'
    })

@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique filename
        filename = str(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Determine file type and parse
        if file_extension == '.pdf':
            file_type = 'pdf'
        elif file_extension == '.docx':
            file_type = 'docx'
        else:
            return jsonify({'error': 'Unsupported file type. Use PDF or DOCX'}), 400
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_path, file_type)
        
        # Log extracted skills for debugging
        print(f" Resume parsed successfully: {file.filename}")
        print(f" Skills extracted: {len(parsed_data.get('skills', []))} skills")
        if parsed_data.get('skills'):
            print(f"   Sample skills: {parsed_data['skills'][:10]}")
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'data': parsed_data
        })
        
    except Exception as e:
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-job', methods=['POST'])
def analyze_job():
    try:
        data = request.get_json()
        
        if not data or 'job_description' not in data:
            return jsonify({'error': 'No job description provided'}), 400
        
        job_text = data['job_description']
        
        # Analyze job description
        analysis = job_analyzer.analyze_job_description(job_text)
        
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-job/file', methods=['POST'])
def analyze_job_file():
    """Analyze job description from uploaded file (PDF, DOCX, TXT)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        filename = str(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()
        temp_path = os.path.join(UPLOAD_FOLDER, f"{file_id}{file_extension}")
        file.save(temp_path)
        
        try:
            # Extract text from file using resume parser's methods
            # (it can handle PDF, DOCX, TXT)
            if file_extension == '.pdf':
                job_text = resume_parser.extract_text_from_pdf(temp_path)
            elif file_extension in ['.docx', '.doc']:
                job_text = resume_parser.extract_text_from_docx(temp_path)
            elif file_extension == '.txt':
                with open(temp_path, 'r', encoding='utf-8') as f:
                    job_text = f.read()
            else:
                return jsonify({'error': f'Unsupported file format: {file_extension}'}), 400
            
            if not job_text or len(job_text.strip()) < 50:
                return jsonify({'error': 'Could not extract sufficient text from file'}), 400
            
            # Analyze job description
            analysis = job_analyzer.analyze_job_description(job_text)
            
            return jsonify({
                'success': True,
                'data': analysis
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/calculate-similarity', methods=['POST'])
def calculate_similarity():
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_text' not in data:
            return jsonify({'error': 'Resume text and job text required'}), 400
        
        resume_text = data['resume_text']
        job_text = data['job_text']
        
        # Extract skills for debugging/verification
        from resume_parser import ResumeParser
        resume_parser_debug = ResumeParser()
        extracted_resume_skills = resume_parser_debug.extract_skills_dynamically(resume_text)
        extracted_job_skills = job_analyzer.extract_required_skills(job_text)
        
        print(f" Resume Skills Extracted: {len(extracted_resume_skills)} skills")
        print(f"   Sample: {extracted_resume_skills[:10]}")
        print(f" Job Skills Extracted: {len(extracted_job_skills)} skills")
        print(f"   Sample: {extracted_job_skills[:10]}")
        
        # Calculate similarity
        similarity_scores = similarity_calculator.calculate_similarity(resume_text, job_text)
        
        # Add extracted skills to response for transparency
        return jsonify({
            'success': True,
            'data': similarity_scores,
            'debug_info': {
                'resume_skills_count': len(extracted_resume_skills),
                'job_skills_count': len(extracted_job_skills),
                'resume_skills_sample': extracted_resume_skills[:10],
                'job_skills_sample': extracted_job_skills[:10]
            }
        })
        
    except Exception as e:
        print(f" Similarity calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/calculate-similarity', methods=['POST'])
def calculate_similarity_ai():
    """Calculate enhanced similarity using AI embeddings and semantic analysis."""
    if not ai_services_available:
        # Fall back to basic similarity
        return calculate_similarity()
    
    try:
        data = request.get_json()
        
        if not data or 'resume_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume data and job data required'}), 400
        
        resume_data = data['resume_data']
        job_data = data['job_data']
        
        print(f" Calculating AI-powered similarity")
        print(f"   Resume skills: {len(resume_data.get('skills', []))} skills")
        print(f"   Job requirements: {len(job_data.get('required_skills', []))} skills")
        
        # Calculate enhanced similarity
        if enhanced_similarity_analyzer is None:
            return calculate_similarity()
        
        similarity_result = enhanced_similarity_analyzer.calculate_enhanced_similarity(resume_data, job_data)
        
        # Wrap in standard response format
        return jsonify({
            'success': True,
            'data': similarity_result
        })
        
    except Exception as e:
        print(f" AI similarity calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-ats-compatibility', methods=['POST'])
def analyze_ats_compatibility():
    """Analyze ATS (Applicant Tracking System) compatibility of resume against job description."""
    try:
        data = request.get_json()
        
        if not data or 'resume_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume data and job data required'}), 400
        
        resume_data = data['resume_data']
        job_data = data['job_data']
        resume_text = data.get('resume_text', '')  # Optional raw resume text
        
        print(f" Analyzing ATS compatibility")
        print(f"   Job: {job_data.get('title', 'Unknown')}")
        print(f"   Resume skills: {len(resume_data.get('skills', []))}")
        print(f"   Required skills: {len(job_data.get('required_skills', []))}")
        
        # Perform ATS analysis
        ats_result = ats_optimizer.analyze_ats_compatibility(
            resume_data=resume_data,
            job_data=job_data,
            resume_text=resume_text
        )
        
        print(f"    ATS Score: {ats_result['overall_score']}/100 ({ats_result['category']})")
        print(f"   Pass Rate: {ats_result['estimated_pass_rate']['percentage']}")
        
        return jsonify({
            'success': True,
            'data': ats_result
        })
        
    except Exception as e:
        print(f" ATS analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/optimize-cover-letter-ats', methods=['POST'])
def optimize_cover_letter_ats():
    """Analyze ATS compatibility of a cover letter."""
    try:
        data = request.get_json()
        
        if not data or 'cover_letter' not in data or 'job_data' not in data:
            return jsonify({'error': 'Cover letter and job data required'}), 400
        
        cover_letter = data['cover_letter']
        job_data = data['job_data']
        
        print(f" Analyzing cover letter ATS compatibility")
        print(f"   Letter length: {len(cover_letter)} characters")
        
        # Analyze cover letter
        cl_result = ats_optimizer.optimize_cover_letter_for_ats(
            cover_letter=cover_letter,
            job_data=job_data
        )
        
        print(f"    Cover Letter ATS Score: {cl_result['score']}/100")
        print(f"   Skills mentioned: {cl_result['skills_mentioned']}/{cl_result['skills_total']}")
        
        return jsonify({
            'success': True,
            'data': cl_result
        })
        
    except Exception as e:
        print(f" Cover letter ATS analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===============================
# AI ENDPOINTS
# ===============================

@app.route('/ai/health', methods=['GET'])
def ai_health_check():
    """Health check for AI services."""
    if not ai_services_available:
        return jsonify({
            'status': 'unavailable',
            'message': 'AI services not initialized',
            'fallback_mode': True
        }), 503
    
    try:
        if ai_service is None:
            return jsonify({
                'status': 'unavailable',
                'message': 'AI service not initialized',
                'fallback_mode': True
            }), 503
        
        health_status = ai_service.health_check()
        return jsonify({
            'status': 'healthy',
            'ai_services': health_status,
            'message': 'All AI services operational'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/ai/analyze-resume-advanced', methods=['POST'])
def analyze_resume_advanced():
    """Enhanced AI-powered resume analysis."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({'error': 'Resume text required'}), 400
        
        resume_text = data['resume_text']
        user_id = data.get('user_id', 'anonymous')
        
        # Perform enhanced analysis
        if enhanced_resume_analyzer is None:
            return jsonify({'error': 'Enhanced resume analyzer not available'}), 503
        
        analysis_result = enhanced_resume_analyzer.analyze_resume_advanced(resume_text, user_id)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/skill-gap-analysis', methods=['POST'])
def skill_gap_analysis():
    """Analyze skill gaps between resume and job."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_description' not in data:
            return jsonify({'error': 'Resume text and job description required'}), 400
        
        resume_text = data['resume_text']
        job_description = data['job_description']
        
        # Perform skill gap analysis
        if enhanced_resume_analyzer is None:
            return jsonify({'error': 'Enhanced resume analyzer not available'}), 503
        
        gap_result = enhanced_resume_analyzer.get_skill_gap_analysis(resume_text, job_description)
        
        return jsonify(gap_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/recommend-jobs', methods=['POST'])
def recommend_jobs():
    """Get AI-powered job recommendations."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({'error': 'Resume text required'}), 400
        
        resume_text = data['resume_text']
        preferences = data.get('preferences', {})
        limit = data.get('limit', 10)
        
        # Get job recommendations
        if job_recommender is None:
            return jsonify({'error': 'Job recommender not available'}), 503
        
        recommendations = job_recommender.recommend_jobs(resume_text, preferences, limit)
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/explain-job-match', methods=['POST'])
def explain_job_match():
    """Explain why a job matches a candidate."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume text and job data required'}), 400
        
        resume_text = data['resume_text']
        job_data = data['job_data']
        
        # Get match explanation
        if job_recommender is None:
            return jsonify({'error': 'Job recommender not available'}), 503
        
        explanation = job_recommender.explain_job_match(resume_text, job_data)
        
        return jsonify(explanation)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/career-suggestions', methods=['POST'])
def career_suggestions():
    """Get AI-powered career progression suggestions."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({'error': 'Resume text required'}), 400
        
        resume_text = data['resume_text']
        
        # Get career suggestions
        if job_recommender is None:
            return jsonify({'error': 'Job recommender not available'}), 503
        
        suggestions = job_recommender.get_career_suggestions(resume_text)
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/generate-cover-letter', methods=['POST'])
def generate_cover_letter_ai():
    """Generate AI-powered cover letter."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume data and job data required'}), 400
        
        resume_data = data['resume_data']
        job_data = data['job_data']
        preferences = data.get('preferences', {})
        
        # Generate cover letter
        if cover_letter_generator is None:
            return jsonify({'error': 'Cover letter generator not available'}), 503
        
        cover_letter_result = cover_letter_generator.generate_cover_letter(resume_data, job_data, preferences)
        
        # Wrap result in 'data' field for consistent API response format
        if cover_letter_result.get('success'):
            return jsonify({
                'success': True,
                'data': cover_letter_result
            })
        else:
            return jsonify(cover_letter_result), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/generate-cover-letter-variations', methods=['POST'])
def generate_cover_letter_variations():
    """Generate multiple cover letter variations."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'resume_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume data and job data required'}), 400
        
        resume_data = data['resume_data']
        job_data = data['job_data']
        
        # Generate multiple variations
        if cover_letter_generator is None:
            return jsonify({'error': 'Cover letter generator not available'}), 503
        
        variations_result = cover_letter_generator.generate_multiple_variations(resume_data, job_data)
        
        return jsonify(variations_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/optimize-cover-letter', methods=['POST'])
def optimize_cover_letter():
    """Optimize an existing cover letter."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'cover_letter_text' not in data or 'job_data' not in data:
            return jsonify({'error': 'Cover letter text and job data required'}), 400
        
        cover_letter_text = data['cover_letter_text']
        job_data = data['job_data']
        
        # Optimize cover letter
        if cover_letter_generator is None:
            return jsonify({'error': 'Cover letter generator not available'}), 503
        
        optimization_result = cover_letter_generator.optimize_cover_letter(cover_letter_text, job_data)
        
        return jsonify(optimization_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai/index-job', methods=['POST'])
def index_job():
    """Index a job description for future recommendations."""
    if not ai_services_available:
        return jsonify({'error': 'AI services not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'job_data' not in data:
            return jsonify({'error': 'Job data required'}), 400
        
        job_data = data['job_data']
        
        # Index the job
        if job_recommender is None:
            return jsonify({'error': 'Job recommender not available'}), 503
        
        index_result = job_recommender.index_job_description(job_data)
        
        return jsonify(index_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter_basic():
    """Generate a basic cover letter (fallback when AI is not available)."""
    try:
        data = request.get_json()
        
        if not data or 'resume_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'Resume data and job data required'}), 400
        
        resume_data = data['resume_data']
        job_data = data['job_data']
        tone = data.get('tone', 'professional')
        
        print(f" Generating cover letter (AI: {ai_services_available})")
        print(f"   Job: {job_data.get('title', 'Unknown')}")
        print(f"   Tone: {tone}")
        
        # Use AI service if available
        if ai_services_available and cover_letter_generator is not None:
            preferences = {'tone': tone}
            cover_letter_result = cover_letter_generator.generate_cover_letter(
                resume_data, job_data, preferences
            )
            
            if cover_letter_result.get('success'):
                return jsonify({
                    'success': True,
                    'data': cover_letter_result
                })
            else:
                # Fall back to basic if AI fails
                print(f"    AI generation failed, using fallback")
        
        # Basic template-based cover letter (fallback)
        cover_letter = _generate_basic_cover_letter(resume_data, job_data, tone)
        
        return jsonify({
            'success': True,
            'data': {
                'cover_letter': cover_letter,
                'generated_with': 'template',
                'tone': tone
            }
        })
        
    except Exception as e:
        print(f" Cover letter generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _generate_basic_cover_letter(resume_data: dict, job_data: dict, tone: str) -> str:
    """Generate a basic template-based cover letter."""
    
    # Extract key information
    name = resume_data.get('name', 'Applicant')
    email = resume_data.get('email', '')
    phone = resume_data.get('phone', '')
    
    job_title = job_data.get('title', 'Position')
    company = job_data.get('company', 'Your Company')
    required_skills = job_data.get('required_skills', [])
    
    # Get candidate's skills
    candidate_skills = resume_data.get('skills', [])
    
    # Find matching skills
    matching_skills = [skill for skill in candidate_skills if skill in required_skills]
    if not matching_skills and candidate_skills:
        matching_skills = candidate_skills[:5]  # Use first 5 skills
    
    # Get experience
    experience = resume_data.get('experience', [])
    years_exp = len(experience) if experience else 0
    
    # Generate greeting based on tone
    if tone == 'formal':
        greeting = "Dear Hiring Manager,"
        closing = "Respectfully yours,"
    elif tone == 'enthusiastic':
        greeting = f"Dear {company} Team,"
        closing = "Enthusiastically,"
    else:  # professional
        greeting = "Dear Hiring Manager,"
        closing = "Sincerely,"
    
    # Build cover letter
    paragraphs = []
    
    # Opening paragraph
    if tone == 'enthusiastic':
        paragraphs.append(
            f"I am thrilled to submit my application for the {job_title} position at {company}. "
            f"With my background and passion for this field, I am excited about the opportunity to contribute to your team."
        )
    else:
        paragraphs.append(
            f"I am writing to express my strong interest in the {job_title} position at {company}. "
            f"With {years_exp}+ years of relevant experience and a proven track record in this field, "
            f"I am confident in my ability to make valuable contributions to your organization."
        )
    
    # Skills paragraph
    if matching_skills:
        skills_str = ", ".join(matching_skills[:5])
        paragraphs.append(
            f"My expertise includes {skills_str}, which aligns well with the requirements outlined in your job posting. "
            f"I have successfully applied these skills in various professional settings, consistently delivering results "
            f"and exceeding expectations."
        )
    
    # Experience paragraph
    if experience:
        recent_role = experience[0] if experience else {}
        role_title = recent_role.get('title', 'my previous role')
        role_company = recent_role.get('company', 'my previous company')
        
        paragraphs.append(
            f"In my role as {role_title} at {role_company}, I gained valuable experience that has prepared me "
            f"for the challenges of this position. I am adept at problem-solving, working collaboratively with teams, "
            f"and adapting to dynamic work environments."
        )
    
    # Closing paragraph
    if tone == 'enthusiastic':
        paragraphs.append(
            f"I am genuinely excited about the possibility of joining {company} and contributing to your continued success. "
            f"I would welcome the opportunity to discuss how my skills and enthusiasm can benefit your team. "
            f"Thank you for considering my application."
        )
    else:
        paragraphs.append(
            f"I am very interested in the opportunity to bring my skills and experience to {company}. "
            f"I would welcome the chance to discuss how I can contribute to your team's success. "
            f"Thank you for your time and consideration."
        )
    
    # Assemble the letter
    letter_parts = [
        greeting,
        "",
        "\n\n".join(paragraphs),
        "",
        closing,
        name
    ]
    
    if email:
        letter_parts.append(email)
    if phone:
        letter_parts.append(phone)
    
    return "\n".join(letter_parts)

@app.route('/enhance-resume', methods=['POST'])
def enhance_resume():
    """
    Enhance a resume by applying AI-generated recommendations
    Returns the enhanced resume text and recalculated similarity score
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_text' not in data:
            return jsonify({'error': 'Resume text and job text required'}), 400
        
        resume_text = data['resume_text']
        job_text = data['job_text']
        recommendations = data.get('recommendations', {})
        
        print("\n" + "="*80)
        print(" RESUME ENHANCEMENT REQUEST")
        print("="*80)
        
        # Step 1: Analyze the current resume and job
        job_analysis = job_analyzer.analyze_job_description(job_text)
        
        from resume_parser import ResumeParser
        resume_parser_instance = ResumeParser()
        current_skills = resume_parser_instance.extract_skills_dynamically(resume_text)
        
        print(f" Current Resume Skills: {len(current_skills)}")
        print(f" Required Job Skills: {len(job_analysis.get('required_skills', []))}")
        
        # Step 2: Use LLM to enhance the resume with recommendations
        enhancement_prompt = f"""You are a professional resume optimizer. Your task is to rewrite this resume to better match the job description WITHOUT adding false information.

**ORIGINAL RESUME (DO NOT CHANGE THE FACTS):**
{resume_text}

**TARGET JOB:**
Position: {job_analysis.get('job_title', 'Not specified')}
Company: {job_analysis.get('company_name', 'Not specified')}
Required Skills: {', '.join(job_analysis.get('required_skills', [])[:20])}

**YOUR TASK:**
Rewrite the resume to improve ATS matching by:

1. **REWORD existing experience** using keywords from the job description (but keep the same facts)
2. **ADD a professional summary** (2-3 sentences) that highlights relevant experience for this specific role
3. **REORGANIZE skills section** to put job-relevant skills first
4. **USE industry keywords** from the job description in your descriptions
5. **IMPROVE formatting** with clear section headers: SUMMARY, EXPERIENCE, EDUCATION, SKILLS

**CRITICAL RULES - FOLLOW EXACTLY:**
 DO NOT add companies, job titles, or dates that aren't in the original
 DO NOT add specific projects, achievements, or responsibilities not mentioned
 DO NOT add education degrees, certifications, or qualifications not listed
 DO NOT invent numbers, metrics, or quantifiable results
 DO NOT add skills unless they're clearly implied by existing experience

 DO reword existing bullet points to use job description keywords
 DO add a brief summary highlighting their relevant background
 DO reorganize content to emphasize job-relevant experience
 DO improve grammar, formatting, and professional language
 DO use ATS-friendly format (no tables, columns, or graphics)

**EXAMPLE:**
Original: "Worked with databases"
Enhanced: "Managed and optimized database systems" (if job requires database management)

NOT: "Managed PostgreSQL databases with 99.9% uptime" (don't add specific tech or metrics not mentioned)

Return ONLY the rewritten resume. Keep all original facts. Focus on better wording and organization."""

        # Use the LLM directly to generate the enhanced resume
        response = ai_service.llm.complete(enhancement_prompt)
        enhanced_resume = str(response) if response else None
        
        if not enhanced_resume or len(enhanced_resume) < 100:
            return jsonify({
                'success': False,
                'error': 'Failed to generate enhanced resume'
            }), 500
        
        print(f" Generated enhanced resume ({len(enhanced_resume)} characters)")
        
        # Step 3: Calculate similarity for BOTH original and enhanced resume
        original_similarity_scores = similarity_calculator.calculate_similarity(resume_text, job_text)
        new_similarity_scores = similarity_calculator.calculate_similarity(enhanced_resume, job_text)
        
        original_score = original_similarity_scores.get('overall_score', 0)
        new_score = new_similarity_scores.get('overall_score', 0)
        score_improvement = new_score - original_score
        
        print(f"\n SCORE COMPARISON:")
        print(f"   Before Enhancement: {original_score}%")
        print(f"   After Enhancement: {new_score}%")
        print(f"   Improvement: {score_improvement:+.1f}%")
        
        # Validate enhancement didn't make things worse
        if score_improvement < -2:  # Allow small variance
            print(f"  Warning: Enhancement decreased score by {abs(score_improvement):.1f}%")
            print(f"   This might indicate over-optimization or content loss")
        
        print("="*80 + "\n")
        
        return jsonify({
            'success': True,
            'data': {
                'enhanced_resume': enhanced_resume,
                'original_scores': original_similarity_scores,
                'new_similarity_scores': new_similarity_scores,
                'improvements': {
                    'score_change': score_improvement,
                    'skills_added': len(job_analysis.get('required_skills', [])) - len(current_skills),
                    'optimization_applied': True,
                    'warning': 'Enhancement may have removed important content' if score_improvement < -2 else None
                }
            }
        })
        
    except Exception as e:
        print(f" Resume enhancement error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/agentic-optimize-resume', methods=['POST'])
def agentic_optimize_resume():
    """
    Agentic resume optimization using ReAct pattern
    Agent iteratively improves resume through reasoning, action, and reflection
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_text' not in data:
            return jsonify({'error': 'Resume text and job text required'}), 400
        
        resume_text = data['resume_text']
        job_text = data['job_text']
        recommendations = data.get('recommendations', {})
        target_score = data.get('target_score', 85)  # Default target: 85%
        max_iterations = data.get('max_iterations', 3)  # Default: 3 iterations
        
        # Create agent instance with custom parameters
        agent = AgenticResumeOptimizer(
            ai_service=ai_service,
            max_iterations=max_iterations,
            target_score=target_score
        )
        
        # Run agentic optimization
        result = agent.optimize_resume(
            resume_text=resume_text,
            job_text=job_text,
            recommendations=recommendations
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f" Agentic optimization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)