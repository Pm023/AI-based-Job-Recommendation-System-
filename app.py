import os
import json
from flask import Flask, render_template
from config import Config
from models import db
from models.user import User
from models.profile import UserProfile
from models.skill import Skill, UserSkill, UserInterest
from models.job import Job, JobSkill
from models.recommendation import Rule

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.jobs import jobs_bp
    from routes.recommendations import recommendations_bp
    from routes.admin import admin_bp
    from routes.resume import resume_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(resume_bp)

    @app.route('/')
    def landing_page():
        # Get count stats for landing page hero
        total_jobs_count = Job.query.filter_by(status='active').count()
        total_skills_count = Skill.query.count()
        return render_template('index.html', total_jobs=total_jobs_count, total_skills=total_skills_count)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('how_it_works.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return "Internal Server Error", 500

    # Ensure DB tables & Seed Data exist
    with app.app_context():
        # Create instance directory if not exists
        os.makedirs(app.config['BASE_DIR'], exist_ok=True)
        os.makedirs(os.path.join(app.config['BASE_DIR'], 'instance'), exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        db.create_all()
        seed_database()

    return app


def seed_database():
    """Seeds initial skills, 30+ jobs, rules, demo student user, and demo admin user."""
    base_dir = Config.BASE_DIR

    # 1. Seed Skills
    if Skill.query.count() == 0:
        skills_file = os.path.join(base_dir, 'data', 'skills.json')
        if os.path.exists(skills_file):
            with open(skills_file, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)
                for item in skills_data:
                    skill = Skill(id=item['id'], name=item['name'], category=item.get('category', 'General Tech'))
                    db.session.add(skill)
            db.session.commit()
            print("Successfully seeded Skills dictionary.")

    # 2. Seed Jobs & Job Skills
    if Job.query.count() == 0:
        jobs_file = os.path.join(base_dir, 'data', 'jobs.json')
        if os.path.exists(jobs_file):
            with open(jobs_file, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
                for j_item in jobs_data:
                    job = Job(
                        id=j_item['id'],
                        title=j_item['title'],
                        company=j_item['company'],
                        location=j_item['location'],
                        description=j_item['description'],
                        experience=j_item.get('experience', '0-2 Years'),
                        salary=j_item.get('salary', '₹4.5 - ₹6.5 LPA'),
                        job_type=j_item.get('job_type', 'Full-time'),
                        application_url=j_item.get('application_url', 'https://example.com/careers'),
                        status='active'
                    )
                    db.session.add(job)
                    db.session.flush()

                    for req_skill in j_item.get('skills', []):
                        skill_name = req_skill['name']
                        skill_obj = Skill.query.filter(Skill.name.ilike(skill_name)).first()
                        if not skill_obj:
                            skill_obj = Skill(name=skill_name, category='General Tech')
                            db.session.add(skill_obj)
                            db.session.flush()

                        js = JobSkill(
                            job_id=job.id,
                            skill_id=skill_obj.id,
                            required_proficiency=req_skill.get('required_proficiency', 'Intermediate'),
                            weight=float(req_skill.get('weight', 20.0))
                        )
                        db.session.add(js)

            db.session.commit()
            print("Successfully seeded 30+ Job opportunities.")

    # 3. Seed Expert Rules
    if Rule.query.count() == 0:
        rules_file = os.path.join(base_dir, 'data', 'rules.json')
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
                for r in rules_data:
                    rule = Rule(
                        id=r['id'],
                        name=r['name'],
                        condition=json.dumps(r['condition']),
                        conclusion=r['conclusion'],
                        description=r['description']
                    )
                    db.session.add(rule)
            db.session.commit()

    # 4. Seed Demo Student User
    demo_user = User.query.filter_by(email='demo@careermatch.ai').first()
    if not demo_user:
        demo_user = User(name='Student Demo', email='demo@careermatch.ai', role='student')
        demo_user.set_password('Demo@123')
        db.session.add(demo_user)
        db.session.commit()

        # Seed Demo User Profile
        demo_profile = UserProfile(
            user_id=demo_user.id,
            degree='B.Tech Computer Engineering',
            field='Computer Engineering',
            graduation_year=2026,
            experience_level='Fresher',
            preferred_role='Python Developer',
            preferred_location='Ahmedabad',
            resume_text='Experienced student programmer with expertise in Python backend microservices, SQL databases, FastAPI, HTML, and version control Git.'
        )
        db.session.add(demo_profile)

        # Seed Demo User Skills
        demo_skills = [
            ('Python', 'Advanced'),
            ('SQL', 'Intermediate'),
            ('FastAPI', 'Intermediate'),
            ('HTML', 'Advanced'),
            ('CSS', 'Intermediate'),
            ('Git', 'Basic')
        ]
        for sname, prof in demo_skills:
            sobj = Skill.query.filter(Skill.name.ilike(sname)).first()
            if sobj:
                db.session.add(UserSkill(user_id=demo_user.id, skill_id=sobj.id, proficiency=prof))

        # Seed Demo User Interests
        db.session.add(UserInterest(user_id=demo_user.id, interest='Backend Development'))
        db.session.add(UserInterest(user_id=demo_user.id, interest='AI/ML'))
        db.session.commit()

        # Trigger AI Recommendation Engine for Demo User
        from ai.recommendation_engine import recommendation_engine
        recommendation_engine.generate_and_save_recommendations_for_user(demo_user)
        print("Successfully seeded Demo Student account (demo@careermatch.ai / Demo@123).")

    # 5. Seed Demo Admin Account
    admin_user = User.query.filter_by(email='admin@careermatch.ai').first()
    if not admin_user:
        admin_user = User(name='CareerMatch Admin', email='admin@careermatch.ai', role='admin')
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.commit()
        print("Successfully seeded Demo Admin account (admin@careermatch.ai / Admin@123).")


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
