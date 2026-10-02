from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User
from models.profile import UserProfile
from models.skill import Skill, UserSkill, UserInterest
from ai.recommendation_engine import recommendation_engine
from ai.career_guidance import career_guidance_engine
from ai.fuzzy_matcher import fuzzy_matcher

user_bp = Blueprint('user', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    # Generate or fetch dynamic AI recommendations
    recommendations_data = recommendation_engine.generate_and_save_recommendations_for_user(user)

    top_recommended = recommendations_data[:4]

    # Calculate average AI match score for top recommendations
    avg_match = int(round(sum(r['overall_score'] for r in recommendations_data[:5]) / max(1, len(recommendations_data[:5])))) if recommendations_data else 0

    # User Skills Overview
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    skills_overview = []
    for us in user_skills:
        val = int(round(fuzzy_matcher.get_numerical_value(us.proficiency) * 100))
        skills_overview.append({
            'name': us.skill.name if us.skill else 'Skill',
            'proficiency': us.proficiency,
            'percentage': val
        })

    # Skill Gap Preview from top recommendation
    skill_gap_preview = []
    if top_recommended:
        skill_gap_preview = top_recommended[0]['missing_skills'][:3] + top_recommended[0]['partial_skills'][:2]

    # Career Direction
    user_interests = UserInterest.query.filter_by(user_id=user.id).all()
    career_guidance = career_guidance_engine.generate_career_guidance(user, profile, user_skills, user_interests)

    return render_template(
        'dashboard.html',
        user=user,
        profile=profile,
        completion_pct=profile.completion_percentage(),
        avg_match=avg_match,
        top_jobs=top_recommended,
        skills_overview=skills_overview,
        skill_gap_preview=skill_gap_preview,
        career_guidance=career_guidance
    )


@user_bp.route('/profile/setup', methods=['GET', 'POST'])
@login_required
def profile_setup():
    user = User.query.get(session['user_id'])
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == 'POST':
        profile.degree = request.form.get('degree', 'B.Tech Computer Engineering')
        profile.field = request.form.get('field', 'Computer Engineering')
        profile.graduation_year = int(request.form.get('graduation_year', 2026))
        profile.experience_level = request.form.get('experience_level', 'Fresher')
        profile.preferred_role = request.form.get('preferred_role', 'Python Developer')
        profile.preferred_location = request.form.get('preferred_location', 'Ahmedabad')

        # Clear existing skills and re-add
        UserSkill.query.filter_by(user_id=user.id).delete()
        selected_skills = request.form.getlist('skill_name')
        selected_profs = request.form.getlist('skill_proficiency')

        for sname, sprof in zip(selected_skills, selected_profs):
            if sname.strip():
                skill_obj = Skill.query.filter(Skill.name.ilike(sname.strip())).first()
                if not skill_obj:
                    skill_obj = Skill(name=sname.strip(), category='General Tech')
                    db.session.add(skill_obj)
                    db.session.flush()

                user_skill = UserSkill(user_id=user.id, skill_id=skill_obj.id, proficiency=sprof)
                db.session.add(user_skill)

        # Clear existing interests and re-add
        UserInterest.query.filter_by(user_id=user.id).delete()
        interests = request.form.getlist('interests')
        for intr in interests:
            if intr.strip():
                db.session.add(UserInterest(user_id=user.id, interest=intr.strip()))

        db.session.commit()

        # Re-run recommendation calculations
        recommendation_engine.generate_and_save_recommendations_for_user(user)

        flash('Your profile has been saved and analyzed by CareerMatch AI!', 'success')
        return redirect(url_for('user.dashboard'))

    existing_skills = UserSkill.query.filter_by(user_id=user.id).all()
    existing_interests = [i.interest for i in UserInterest.query.filter_by(user_id=user.id).all()]

    return render_template(
        'profile_setup.html',
        user=user,
        profile=profile,
        all_skills=all_skills,
        existing_skills=existing_skills,
        existing_interests=existing_interests
    )


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    return profile_setup()
