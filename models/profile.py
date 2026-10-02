from datetime import datetime
from models import db

class UserProfile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    degree = db.Column(db.String(100), default='B.Tech Computer Engineering')
    field = db.Column(db.String(100), default='Computer Engineering')
    graduation_year = db.Column(db.Integer, default=2026)
    experience_level = db.Column(db.String(50), default='Fresher') # 'Fresher', '0-1 years', '1-3 years', '3+ years'
    preferred_role = db.Column(db.String(100), default='Python Developer')
    preferred_location = db.Column(db.String(100), default='Ahmedabad')
    resume_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def completion_percentage(self):
        # Calculate dynamic profile completion percentage
        score = 0
        if self.degree: score += 15
        if self.field: score += 10
        if self.experience_level: score += 15
        if self.preferred_role: score += 15
        if self.preferred_location: score += 15
        
        # Check skills count
        skills_count = len(self.user.user_skills)
        if skills_count >= 1: score += 15
        if skills_count >= 3: score += 10
        
        if self.resume_text: score += 5
        return min(100, score)

    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'
