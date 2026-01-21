"""
Route handlers for Novo application
"""

from flask import request, render_template, jsonify, redirect, url_for, current_app, session
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {
    'pdf': {'pdf'},
    'audio': {'mp3', 'wav', 'm4a', 'ogg'}
}

def allowed_file(filename, file_type='pdf'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

def init_routes(app):
    """Initialize routes for the Flask app"""
    
    @app.route('/')
    def index():
        """Home page - redirect to profile page"""
        return redirect(url_for('profile'))
    
    @app.route('/profile', methods=['GET'])
    def profile():
        """Render the profile page with file upload form"""
        return render_template('profile.html')
    
    @app.route('/profile', methods=['POST'])
    def upload_profile():
        """Handle profile upload (CV PDF and optional audio brain dump)"""
        try:
            # Check if CV file is present
            if 'cv_file' not in request.files:
                return jsonify({'error': 'CV file is required'}), 400
            
            cv_file = request.files['cv_file']
            
            # Check if CV file is selected
            if cv_file.filename == '':
                return jsonify({'error': 'No CV file selected'}), 400
            
            # Validate CV file type
            if not allowed_file(cv_file.filename, 'pdf'):
                return jsonify({'error': 'CV must be a PDF file'}), 400
            
            # Secure CV filename
            cv_filename = secure_filename(cv_file.filename)
            cv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], cv_filename)
            cv_file.save(cv_path)
            
            # Handle optional audio file
            audio_path = None
            audio_file = request.files.get('audio_file')
            
            if audio_file and audio_file.filename != '':
                # Validate audio file type
                if not allowed_file(audio_file.filename, 'audio'):
                    return jsonify({'error': 'Audio must be mp3, wav, m4a, or ogg'}), 400
                
                audio_filename = secure_filename(audio_file.filename)
                audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_filename)
                audio_file.save(audio_path)
            
            # Import and call AI agent analyzer
            from src.services.ai_agent import analyze_profile
            from src.services.db import save_student_profile
            
            # Analyze profile
            result = analyze_profile(cv_path, audio_path)

            # Persist result to Supabase
            saved_row = save_student_profile(result)
            session["student_row"] = saved_row
            
            # Store result in session for results page
            session['analysis_result'] = result
            session['cv_filename'] = cv_filename
            
            # Redirect to results page
            return redirect(url_for('results'))
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/results', methods=['GET'])
    def results():
        """Display analysis results"""
        result = session.get('analysis_result')
        cv_filename = session.get('cv_filename')
        student_row = session.get("student_row")
        
        if not result:
            return redirect(url_for('profile'))
        
        return render_template('results.html', result=result, cv_filename=cv_filename, student_row=student_row)
