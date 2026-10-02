import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.profile import UserProfile
from models.skill import Skill, UserSkill
from ai.nlp_engine import nlp_engine

resume_bp = Blueprint('resume', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access resume parsing.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def extract_text_from_pdf(filepath):
    """
    Extracts text from PDF file using pypdf / PyMuPDF with fallback options.
    """
    extracted_text = ""
    try:
        # Try PyMuPDF (fitz) first if available
        import fitz
        doc = fitz.open(filepath)
        for page in doc:
            extracted_text += page.get_text() + "\n"
        if extracted_text.strip():
            return extracted_text
    except Exception:
        pass

    try:
        # Fallback to pypdf
        import pypdf
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                extracted_text += t + "\n"
        if extracted_text.strip():
            return extracted_text
    except Exception:
        pass

    return extracted_text


@resume_bp.route('/resume/upload')
@login_required
def upload_page():
    user = User.query.get(session['user_id'])
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    return render_template('resume_upload.html', user=user, profile=profile)


@resume_bp.route('/api/analyze-resume', methods=['POST'])
@login_required
def analyze_resume():
    user = User.query.get(session['user_id'])
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    if 'resume' not in request.files and 'resume_text' not in request.form:
        return jsonify({'success': False, 'error': 'No resume file or text provided.'}), 400

    extracted_text = ""

    # Check file upload
    if 'resume' in request.files:
        file = request.files['resume']
        if file and file.filename != '':
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'success': False, 'error': 'Only PDF format files are supported.'}), 400

            filename = secure_filename(f"user_{user.id}_{file.filename}")
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Extract PDF text
            extracted_text = extract_text_from_pdf(filepath)

    # Fallback to form text if uploaded PDF text was empty
    if not extracted_text.strip() and 'resume_text' in request.form:
        extracted_text = request.form.get('resume_text', '')

    if not extracted_text.strip():
        return jsonify({
            'success': False,
            'error': 'Could not extract readable text from the uploaded PDF. Please copy-paste your resume text or add skills manually.'
        }), 422

    # Save extracted resume text to profile
    profile.resume_text = extracted_text
    db.session.commit()

    # NLP Skill Extraction
    extracted_skills = nlp_engine.extract_skills(extracted_text)

    return jsonify({
        'success': True,
        'extracted_skills': extracted_skills,
        'total_found': len(extracted_skills),
        'preview_text': extracted_text[:400] + "..." if len(extracted_text) > 400 else extracted_text
    })


@resume_bp.route('/api/confirm-extracted-skills', methods=['POST'])
@login_required
def confirm_extracted_skills():
    user = User.query.get(session['user_id'])
    data = request.json or {}
    skills_list = data.get('skills', [])

    for sk in skills_list:
        sname = sk.get('name', '').strip()
        sprof = sk.get('proficiency', 'Intermediate')

        if sname:
            skill_obj = Skill.query.filter(Skill.name.ilike(sname)).first()
            if not skill_obj:
                skill_obj = Skill(name=sname, category=sk.get('category', 'General Tech'))
                db.session.add(skill_obj)
                db.session.flush()

            # Add or update user skill
            user_skill = UserSkill.query.filter_by(user_id=user.id, skill_id=skill_obj.id).first()
            if not user_skill:
                user_skill = UserSkill(user_id=user.id, skill_id=skill_obj.id, proficiency=sprof)
                db.session.add(user_skill)
            else:
                user_skill.proficiency = sprof

    db.session.commit()

    # Re-trigger recommendation calculations
    from ai.recommendation_engine import recommendation_engine
    recommendation_engine.generate_and_save_recommendations_for_user(user)

    return jsonify({'success': True, 'message': f'{len(skills_list)} skills added to your profile successfully!'})
