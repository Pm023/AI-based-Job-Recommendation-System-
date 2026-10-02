from models import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, default='General Tech')

    # Relationships
    user_skills = db.relationship('UserSkill', backref='skill', cascade='all, delete-orphan')
    job_skills = db.relationship('JobSkill', backref='skill', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Skill {self.name}>'


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency = db.Column(db.String(30), nullable=False, default='Intermediate')  # Beginner, Basic, Intermediate, Advanced, Expert

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', name='unique_user_skill'),
    )

    def __repr__(self):
        return f'<UserSkill user={self.user_id} skill={self.skill_id} prof={self.proficiency}>'


class UserInterest(db.Model):
    __tablename__ = 'user_interests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    interest = db.Column(db.String(100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'interest', name='unique_user_interest'),
    )

    def __repr__(self):
        return f'<UserInterest user={self.user_id} interest={self.interest}>'
