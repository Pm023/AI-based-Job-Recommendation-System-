from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User
from models.job import Job, JobSkill
from models.skill import Skill
from models.recommendation import Recommendation, SkillGap
from models.profile import UserProfile

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Admin authentication required. Access denied.', 'danger')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email, role='admin').first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('Admin authentication successful.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return render_template('admin_login.html')

    return render_template('admin_login.html')


@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='student').count()
    total_jobs = Job.query.count()
    total_recs = Recommendation.query.count()

    all_recs = Recommendation.query.all()
    avg_match = round(sum(r.overall_score for r in all_recs) / max(1, len(all_recs)), 1) if all_recs else 0.0

    recent_users = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_jobs=total_jobs,
        total_recs=total_recs,
        avg_match=avg_match,
        recent_users=recent_users,
        recent_jobs=recent_jobs
    )


@admin_bp.route('/admin/jobs')
@admin_required
def manage_jobs():
    search_q = request.args.get('q', '').strip()
    query = Job.query
    if search_q:
        query = query.filter((Job.title.ilike(f'%{search_q}%')) | (Job.company.ilike(f'%{search_q}%')))
    jobs_list = query.order_by(Job.created_at.desc()).all()
    return render_template('manage_jobs.html', jobs=jobs_list, search_q=search_q)


@admin_bp.route('/admin/jobs/add', methods=['GET', 'POST'])
@admin_required
def add_job():
    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        experience = request.form.get('experience', '0-2 Years')
        salary = request.form.get('salary', '₹4.0 - ₹6.0 LPA')
        job_type = request.form.get('job_type', 'Full-time')
        app_url = request.form.get('application_url', '')

        if not title or not company or not description:
            flash('Title, Company, and Description are required.', 'danger')
            return render_template('job_form.html', job=None, all_skills=all_skills)

        new_job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            experience=experience,
            salary=salary,
            job_type=job_type,
            application_url=app_url,
            status='active'
        )
        db.session.add(new_job)
        db.session.flush()

        # Job skills & weights processing
        skill_names = request.form.getlist('skill_name')
        skill_profs = request.form.getlist('skill_proficiency')
        skill_weights = request.form.getlist('skill_weight')

        total_weight = 0.0
        for sname, sprof, sweight in zip(skill_names, skill_profs, skill_weights):
            if sname.strip():
                weight_val = float(sweight) if sweight else 20.0
                total_weight += weight_val

                skill_obj = Skill.query.filter(Skill.name.ilike(sname.strip())).first()
                if not skill_obj:
                    skill_obj = Skill(name=sname.strip(), category='General Tech')
                    db.session.add(skill_obj)
                    db.session.flush()

                job_skill = JobSkill(
                    job_id=new_job.id,
                    skill_id=skill_obj.id,
                    required_proficiency=sprof,
                    weight=weight_val
                )
                db.session.add(job_skill)

        db.session.commit()

        flash(f"Job '{title}' created successfully!", 'success')
        return redirect(url_for('admin.manage_jobs'))

    return render_template('job_form.html', job=None, all_skills=all_skills)


@admin_bp.route('/admin/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.company = request.form.get('company', '').strip()
        job.location = request.form.get('location', '').strip()
        job.description = request.form.get('description', '').strip()
        job.experience = request.form.get('experience', '0-2 Years')
        job.salary = request.form.get('salary', '')
        job.job_type = request.form.get('job_type', 'Full-time')
        job.application_url = request.form.get('application_url', '')

        # Replace job skills
        JobSkill.query.filter_by(job_id=job.id).delete()
        skill_names = request.form.getlist('skill_name')
        skill_profs = request.form.getlist('skill_proficiency')
        skill_weights = request.form.getlist('skill_weight')

        for sname, sprof, sweight in zip(skill_names, skill_profs, skill_weights):
            if sname.strip():
                weight_val = float(sweight) if sweight else 20.0
                skill_obj = Skill.query.filter(Skill.name.ilike(sname.strip())).first()
                if not skill_obj:
                    skill_obj = Skill(name=sname.strip(), category='General Tech')
                    db.session.add(skill_obj)
                    db.session.flush()

                db.session.add(JobSkill(
                    job_id=job.id,
                    skill_id=skill_obj.id,
                    required_proficiency=sprof,
                    weight=weight_val
                ))

        db.session.commit()
        flash(f"Job '{job.title}' updated successfully!", 'success')
        return redirect(url_for('admin.manage_jobs'))

    return render_template('job_form.html', job=job, all_skills=all_skills)


@admin_bp.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f"Job '{title}' deleted successfully.", 'info')
    return redirect(url_for('admin.manage_jobs'))
