from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User
from models.job import Job, JobSkill
from models.skill import Skill, UserSkill, UserInterest
from models.profile import UserProfile
from ai.recommendation_engine import recommendation_engine
from ai.fuzzy_matcher import fuzzy_matcher

jobs_bp = Blueprint('jobs', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to explore job recommendations.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@jobs_bp.route('/jobs')
@jobs_bp.route('/jobs/recommended')
@login_required
def recommended_jobs():
    user = User.query.get(session['user_id'])
    
    # Run dynamic AI recommendation engine for current user
    recommendations_data = recommendation_engine.generate_and_save_recommendations_for_user(user)

    # Filtering parameters
    search_query = request.args.get('q', '').strip().lower()
    role_filter = request.args.get('role', '').strip().lower()
    location_filter = request.args.get('location', '').strip().lower()
    exp_filter = request.args.get('experience', '').strip().lower()
    min_score = int(request.args.get('min_score', 0))
    sort_by = request.args.get('sort', 'best')

    filtered_list = []
    for item in recommendations_data:
        job = item['job']
        score = item['overall_score']

        # Apply score filter
        if score < min_score:
            continue

        # Apply search query
        if search_query:
            matches_q = (
                search_query in job.title.lower() or
                search_query in job.company.lower() or
                search_query in job.description.lower() or
                any(search_query in (js.skill.name.lower() if js.skill else '') for js in job.job_skills)
            )
            if not matches_q:
                continue

        # Apply role filter
        if role_filter and role_filter not in job.title.lower():
            continue

        # Apply location filter
        if location_filter and location_filter not in job.location.lower():
            continue

        # Apply experience filter
        if exp_filter and exp_filter not in job.experience.lower():
            continue

        filtered_list.append(item)

    # Sorting
    if sort_by == 'newest':
        filtered_list.sort(key=lambda x: x['job'].created_at, reverse=True)
    elif sort_by == 'location':
        filtered_list.sort(key=lambda x: x['job'].location)
    else:  # 'best'
        filtered_list.sort(key=lambda x: x['overall_score'], reverse=True)

    # Extract distinct locations and titles for dropdown filters
    all_jobs = Job.query.filter_by(status='active').all()
    locations = sorted(list({j.location for j in all_jobs if j.location}))
    titles = sorted(list({j.title for j in all_jobs if j.title}))

    return render_template(
        'jobs.html',
        recommendations=filtered_list,
        total_count=len(filtered_list),
        locations=locations,
        roles=titles,
        search_query=search_query,
        role_filter=role_filter,
        location_filter=location_filter,
        exp_filter=exp_filter,
        min_score=min_score,
        sort_by=sort_by
    )


@jobs_bp.route('/jobs/<int:job_id>')
@login_required
def job_details(job_id):
    user = User.query.get(session['user_id'])
    job = Job.query.get_or_404(job_id)

    profile = UserProfile.query.filter_by(user_id=user.id).first()
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    user_interests = UserInterest.query.filter_by(user_id=user.id).all()

    # Calculate exact AI compatibility for this specific job
    match_data = recommendation_engine.calculate_job_compatibility(
        user, profile, user_skills, user_interests, job
    )

    # Map user skills for skill-by-skill comparison table
    user_skill_dict = {us.skill.name.lower(): us.proficiency for us in user_skills if us.skill}

    skill_comparisons = []
    for js in job.job_skills:
        sname = js.skill.name if js.skill else 'Skill'
        req_prof = js.required_proficiency
        user_prof = user_skill_dict.get(sname.lower())

        if user_prof is None:
            status = 'Gap (Missing)'
            status_class = 'badge bg-danger'
        else:
            match_score = fuzzy_matcher.calculate_skill_match_score(user_prof, req_prof)
            category = fuzzy_matcher.get_membership_category(match_score)
            if match_score >= 0.85:
                status = 'Strong Match'
                status_class = 'badge bg-success'
            else:
                status = f'Partial ({category})'
                status_class = 'badge bg-warning text-dark'

        skill_comparisons.append({
            'skill_name': sname,
            'user_proficiency': user_prof if user_prof else 'Not Added',
            'required_proficiency': req_prof,
            'weight': js.weight,
            'status': status,
            'status_class': status_class
        })

    return render_template(
        'job_details.html',
        job=job,
        overall_score=match_data['overall_score_int'],
        sub_scores=match_data['sub_scores'],
        explanation=match_data['explanation'],
        improvement_suggestion=match_data['improvement_suggestion'],
        matched_skills=match_data['matched_skills'],
        partial_skills=match_data['partial_skills'],
        missing_skills=match_data['missing_skills'],
        skill_comparisons=skill_comparisons
    )
