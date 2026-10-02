from datetime import datetime
from models import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    experience = db.Column(db.String(50), nullable=False, default='0-2 Years')
    salary = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), default='Full-time')
    application_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')  # 'active', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_skills = db.relationship('JobSkill', backref='job', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='job', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.title} @ {self.company}>'


class JobSkill(db.Model):
    __tablename__ = 'job_skills'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    required_proficiency = db.Column(db.String(30), nullable=False, default='Intermediate') # Beginner, Basic, Intermediate, Advanced, Expert
    weight = db.Column(db.Float, nullable=False, default=20.0) # Weight out of 100 total for the job

    __table_args__ = (
        db.UniqueConstraint('job_id', 'skill_id', name='unique_job_skill'),
    )

    def __repr__(self):
        return f'<JobSkill job={self.job_id} skill={self.skill_id} req={self.required_proficiency} weight={self.weight}>'
