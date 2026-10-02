from datetime import datetime
from models import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    
    # Detailed sub-scores for complete explainability
    overall_score = db.Column(db.Float, nullable=False)
    skill_score = db.Column(db.Float, nullable=False)
    education_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    interest_score = db.Column(db.Float, nullable=False)
    location_score = db.Column(db.Float, nullable=False)
    
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_recommendation'),
    )

    def __repr__(self):
        return f'<Recommendation user={self.user_id} job={self.job_id} score={self.overall_score}%>'


class Rule(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.Text, nullable=False) # Stored JSON condition string
    conclusion = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Rule {self.name}>'


class SkillGap(db.Model):
    __tablename__ = 'skill_gaps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    gap_level = db.Column(db.String(30), nullable=False) # 'Strong Match', 'Partial Match', 'Missing'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skill = db.relationship('Skill')
    job = db.relationship('Job')

    def __repr__(self):
        return f'<SkillGap user={self.user_id} job={self.job_id} skill={self.skill_id} gap={self.gap_level}>'
