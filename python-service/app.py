from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from resume_parser import ResumeParser
from job_analyzer import JobAnalyzer, SimilarityCalculator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

resume_parser = ResumeParser()
job_analyzer = JobAnalyzer()
similarity_calculator = SimilarityCalculator()

# Create upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Resume Parser API'})

@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
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

@app.route('/calculate-similarity', methods=['POST'])
def calculate_similarity():
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'job_text' not in data:
            return jsonify({'error': 'Resume text and job text required'}), 400
        
        resume_text = data['resume_text']
        job_text = data['job_text']
        
        # Calculate similarity
        similarity_scores = similarity_calculator.calculate_similarity(resume_text, job_text)
        
        return jsonify({
            'success': True,
            'data': similarity_scores
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)