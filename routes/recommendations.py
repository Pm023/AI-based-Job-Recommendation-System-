from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User
from models.job import Job
from models.skill import UserSkill, UserInterest
from models.profile import UserProfile
from ai.skill_gap import skill_gap_engine
from ai.career_guidance import career_guidance_engine

recommendations_bp = Blueprint('recommendations', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@recommendations_bp.route('/skill-gap')
@login_required
def skill_gap():
    user = User.query.get(session['user_id'])
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    
    # Target role selection
    target_role = request.args.get('role', 'Backend Developer')
    job_id = request.args.get('job_id', type=int)

    all_jobs = Job.query.filter_by(status='active').all()

    target_job = None
    if job_id:
        target_job = Job.query.get(job_id)
        if target_job:
            target_role = target_job.title

    if target_job and target_job.job_skills:
        skill_analysis = skill_gap_engine.analyze_job_skill_gap(user_skills, target_job.job_skills)
    else:
        # Match against role ontology
        mock_job_skills = []
        if target_role == "Data Analyst":
            reqs = [("Python", "Intermediate", 30), ("SQL", "Intermediate", 30), ("Pandas", "Intermediate", 20), ("Statistics", "Basic", 20)]
        elif target_role == "AI Engineer":
            reqs = [("Python", "Advanced", 30), ("Machine Learning", "Intermediate", 30), ("NLP", "Intermediate", 20), ("PyTorch", "Basic", 20)]
        elif target_role == "Full Stack Developer":
            reqs = [("JavaScript", "Intermediate", 25), ("HTML", "Advanced", 20), ("CSS", "Intermediate", 15), ("Python", "Intermediate", 25), ("SQL", "Basic", 15)]
        else: # Backend Developer
            reqs = [("Python", "Intermediate", 30), ("FastAPI", "Intermediate", 25), ("SQL", "Intermediate", 20), ("Git", "Basic", 15), ("Docker", "Beginner", 10)]

        for sname, req_p, weight in reqs:
            mock_job_skills.append({
                'name': sname,
                'required_proficiency': req_p,
                'weight': weight
            })
        skill_analysis = skill_gap_engine.analyze_job_skill_gap(user_skills, mock_job_skills)

    learning_path_data = skill_gap_engine.get_role_learning_path(target_role, user_skills)

    return render_template(
        'skill_gap.html',
        user=user,
        target_role=target_role,
        target_job=target_job,
        all_jobs=all_jobs,
        skill_analysis=skill_analysis,
        learning_path=learning_path_data['learning_path'],
        role_description=learning_path_data['description'],
        alternatives=learning_path_data['alternatives']
    )


@recommendations_bp.route('/career-guidance')
@login_required
def career_guidance():
    user = User.query.get(session['user_id'])
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    user_interests = UserInterest.query.filter_by(user_id=user.id).all()

    guidance = career_guidance_engine.generate_career_guidance(user, profile, user_skills, user_interests)

    return render_template(
        'career_guidance.html',
        user=user,
        profile=profile,
        guidance=guidance,
        user_skills=user_skills
    )


@recommendations_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')
