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


class Appointment(db.Model):
    """Model for storing calendar appointments"""
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    interviewer_name = db.Column(db.String(100), nullable=False)
    interviewer_email = db.Column(db.String(120), nullable=False)
    appointment_type = db.Column(db.String(50), default='Interview')  # Interview, Phone Screen, Technical Review
    scheduled_start = db.Column(db.DateTime, nullable=False)
    scheduled_end = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, rescheduled
    google_event_id = db.Column(db.String(255))  # Google Calendar event ID
    google_meet_link = db.Column(db.String(500))  # Google Meet link
    google_calendar_link = db.Column(db.String(500))  # Google Calendar event link
    notes = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = db.relationship('Candidate', backref='appointments')
    job = db.relationship('JobDescription', backref='appointments')
    
    def to_dict(self):
        """Convert appointment to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'candidate_name': self.candidate.name,
            'candidate_email': self.candidate.email,
            'job_title': self.job.title,
            'interviewer_name': self.interviewer_name,
            'interviewer_email': self.interviewer_email,
            'appointment_type': self.appointment_type,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'scheduled_end': self.scheduled_end.isoformat() if self.scheduled_end else None,
            'status': self.status,
            'google_meet_link': self.google_meet_link,
            'google_calendar_link': self.google_calendar_link,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
