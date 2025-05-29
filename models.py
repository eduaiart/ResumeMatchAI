from app import db
from datetime import datetime
from sqlalchemy import Text, JSON

class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text, nullable=False)
    requirements = db.Column(JSON)  # Extracted requirements
    skills_required = db.Column(JSON)  # Categorized skills
    skill_weights = db.Column(JSON)  # Configurable weights
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to candidates
    candidates = db.relationship('Candidate', backref='job', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    raw_text = db.Column(Text)
    extracted_skills = db.Column(JSON)
    experience_years = db.Column(db.Integer)
    education = db.Column(JSON)
    work_experience = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    job_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=True)

class MatchScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    skill_match_score = db.Column(db.Float)
    experience_score = db.Column(db.Float)
    education_score = db.Column(db.Float)
    detailed_breakdown = db.Column(JSON)
    skill_gaps = db.Column(JSON)
    match_justification = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = db.relationship('Candidate', backref='match_scores')
    job = db.relationship('JobDescription', backref='match_scores')
