import os
import json
import logging
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import JobDescription, Candidate, MatchScore, Appointment
from document_parser import DocumentParser
from nlp_processor import NLPProcessor
from matching_engine import MatchingEngine
from utils import allowed_file, export_candidates_csv
from google_calendar_service import GoogleCalendarService
import pandas as pd

# Initialize processors
nlp_processor = NLPProcessor()
matching_engine = MatchingEngine(nlp_processor)

@app.route('/')
def index():
    """Home page with overview of the system"""
    total_jobs = JobDescription.query.count()
    total_candidates = Candidate.query.count()
    recent_jobs = JobDescription.query.order_by(JobDescription.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_jobs=total_jobs,
                         total_candidates=total_candidates,
                         recent_jobs=recent_jobs)

@app.route('/upload')
def upload():
    """Upload page for job descriptions and resumes"""
    jobs = JobDescription.query.all()
    return render_template('upload.html', jobs=jobs)

@app.route('/upload_job', methods=['POST'])
def upload_job():
    """Handle job description upload"""
    try:
        title = request.form.get('job_title')
        description = request.form.get('job_description')
        
        if not title or not description:
            flash('Job title and description are required', 'error')
            return redirect(url_for('upload'))
        
        # Process job description with NLP
        job_analysis = nlp_processor.analyze_job_description(description)
        
        # Create job record
        job = JobDescription(
            title=title,
            description=description,
            requirements=job_analysis['requirements'],
            skills_required=job_analysis['skills'],
            skill_weights=job_analysis['skill_weights']
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash(f'Job description "{title}" uploaded successfully!', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
        
    except Exception as e:
        logging.error(f"Error uploading job: {str(e)}")
        flash('Error processing job description. Please try again.', 'error')
        return redirect(url_for('upload'))

@app.route('/upload_resumes', methods=['POST'])
def upload_resumes():
    """Handle bulk resume upload"""
    try:
        job_id = request.form.get('job_id')
        if not job_id:
            flash('Please select a job to match candidates against', 'error')
            return redirect(url_for('upload'))
        
        job = JobDescription.query.get_or_404(job_id)
        files = request.files.getlist('resumes')
        
        if not files or files[0].filename == '':
            flash('No files selected', 'error')
            return redirect(url_for('upload'))
        
        uploaded_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Save file
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Parse document
                    parser = DocumentParser()
                    raw_text = parser.extract_text(file_path)
                    
                    # Process with NLP
                    candidate_data = nlp_processor.extract_candidate_info(raw_text)
                    
                    # Create candidate record
                    candidate = Candidate(
                        name=candidate_data.get('name', 'Unknown'),
                        email=candidate_data.get('email'),
                        phone=candidate_data.get('phone'),
                        filename=filename,
                        file_path=file_path,
                        raw_text=raw_text,
                        extracted_skills=candidate_data.get('skills', []),
                        experience_years=candidate_data.get('experience_years'),
                        education=candidate_data.get('education', []),
                        work_experience=candidate_data.get('work_experience', []),
                        job_id=job.id
                    )
                    
                    db.session.add(candidate)
                    db.session.flush()  # Get the ID
                    
                    # Calculate match score
                    match_result = matching_engine.calculate_match_score(candidate, job)
                    
                    # Create match score record
                    match_score = MatchScore(
                        candidate_id=candidate.id,
                        job_id=job.id,
                        overall_score=match_result['overall_score'],
                        skill_match_score=match_result['skill_score'],
                        experience_score=match_result['experience_score'],
                        education_score=match_result['education_score'],
                        detailed_breakdown=match_result['breakdown'],
                        skill_gaps=match_result['skill_gaps'],
                        match_justification=match_result['justification']
                    )
                    
                    db.session.add(match_score)
                    uploaded_count += 1
                    
                except Exception as e:
                    logging.error(f"Error processing file {filename}: {str(e)}")
                    continue
        
        db.session.commit()
        flash(f'Successfully processed {uploaded_count} resumes!', 'success')
        return redirect(url_for('candidates', job_id=job_id))
        
    except Exception as e:
        logging.error(f"Error uploading resumes: {str(e)}")
        flash('Error processing resumes. Please try again.', 'error')
        return redirect(url_for('upload'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard with job and candidate overview"""
    jobs = JobDescription.query.order_by(JobDescription.created_at.desc()).all()
    
    # Calculate statistics for each job
    job_stats = []
    for job in jobs:
        candidate_count = Candidate.query.filter_by(job_id=job.id).count()
        if candidate_count > 0:
            avg_score = db.session.query(db.func.avg(MatchScore.overall_score)).filter_by(job_id=job.id).scalar()
            avg_score = round(avg_score, 2) if avg_score else 0
        else:
            avg_score = 0
            
        job_stats.append({
            'job': job,
            'candidate_count': candidate_count,
            'avg_score': avg_score
        })
    
    return render_template('dashboard.html', job_stats=job_stats)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Detailed view of a specific job"""
    job = JobDescription.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@app.route('/candidates/<int:job_id>')
def candidates(job_id):
    """View ranked candidates for a specific job"""
    job = JobDescription.query.get_or_404(job_id)
    
    # Get candidates with their match scores, ordered by score
    candidates_with_scores = db.session.query(Candidate, MatchScore).join(
        MatchScore, Candidate.id == MatchScore.candidate_id
    ).filter(
        Candidate.job_id == job_id
    ).order_by(MatchScore.overall_score.desc()).all()
    
    # Debug logging
    logging.info(f"Found {len(candidates_with_scores)} candidates for job {job_id}")
    if candidates_with_scores:
        first_candidate = candidates_with_scores[0][0]
        logging.info(f"First candidate: name={first_candidate.name}, skills={first_candidate.extracted_skills}")
    
    return render_template('candidates.html', 
                         job=job, 
                         candidates_with_scores=candidates_with_scores)

@app.route('/update_weights/<int:job_id>', methods=['POST'])
def update_weights(job_id):
    """Update skill weights for a job"""
    try:
        job = JobDescription.query.get_or_404(job_id)
        weights = request.get_json()
        
        job.skill_weights = weights
        db.session.commit()
        
        # Recalculate all match scores for this job
        candidates = Candidate.query.filter_by(job_id=job_id).all()
        for candidate in candidates:
            match_result = matching_engine.calculate_match_score(candidate, job)
            
            # Update existing match score
            match_score = MatchScore.query.filter_by(
                candidate_id=candidate.id, 
                job_id=job_id
            ).first()
            
            if match_score:
                match_score.overall_score = match_result['overall_score']
                match_score.skill_match_score = match_result['skill_score']
                match_score.experience_score = match_result['experience_score']
                match_score.education_score = match_result['education_score']
                match_score.detailed_breakdown = match_result['breakdown']
                match_score.skill_gaps = match_result['skill_gaps']
                match_score.match_justification = match_result['justification']
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error updating weights: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export_candidates/<int:job_id>')
def export_candidates(job_id):
    """Export shortlisted candidates to CSV"""
    try:
        job = JobDescription.query.get_or_404(job_id)
        
        # Get candidates with scores above threshold (default: all candidates)
        threshold = request.args.get('threshold', 0, type=float)
        
        candidates_data = db.session.query(Candidate, MatchScore).join(
            MatchScore, Candidate.id == MatchScore.candidate_id
        ).filter(
            Candidate.job_id == job_id,
            MatchScore.overall_score >= threshold
        ).order_by(MatchScore.overall_score.desc()).all()
        
        if not candidates_data:
            flash('No candidates meet the specified threshold', 'warning')
            return redirect(url_for('candidates', job_id=job_id))
        
        # Create CSV file
        csv_path = export_candidates_csv(candidates_data, job.title)
        
        return send_file(csv_path, as_attachment=True, 
                        download_name=f"{job.title}_candidates.csv")
        
    except Exception as e:
        logging.error(f"Error exporting candidates: {str(e)}")
        flash('Error exporting candidates. Please try again.', 'error')
        return redirect(url_for('candidates', job_id=job_id))

@app.route('/clear_all_data', methods=['POST'])
def clear_all_data():
    """Clear all data from the database"""
    try:
        # Delete all match scores first (due to foreign key constraints)
        MatchScore.query.delete()
        
        # Delete all candidates
        Candidate.query.delete()
        
        # Delete all job descriptions
        JobDescription.query.delete()
        
        # Commit the changes
        db.session.commit()
        
        flash('All dashboard data has been successfully cleared.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing data: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# Google Calendar Integration Routes
calendar_service = GoogleCalendarService()

@app.route('/calendar/auth')
def calendar_auth():
    """Initialize Google Calendar OAuth flow"""
    try:
        auth_url = calendar_service.get_auth_url()
        return redirect(auth_url)
    except ValueError as e:
        flash(f'Google Calendar setup error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/oauth2callback')
def oauth2callback():
    """Handle Google Calendar OAuth callback"""
    try:
        success = calendar_service.handle_oauth_callback(request.url)
        if success:
            flash('Successfully connected to Google Calendar!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Failed to connect to Google Calendar. Please try again.', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'OAuth error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/schedule_appointment/<int:candidate_id>')
def schedule_appointment(candidate_id):
    """Show appointment scheduling form"""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Check if Google Calendar is authenticated
    if not calendar_service.is_authenticated():
        flash('Please connect to Google Calendar first to schedule appointments.', 'warning')
        return redirect(url_for('calendar_auth'))
    
    # Get available time slots (next 7 days)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    available_slots = calendar_service.get_available_slots(start_date, end_date)
    
    return render_template('schedule_appointment.html', 
                         candidate=candidate, 
                         available_slots=available_slots)

@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    try:
        # Get form data
        candidate_id = request.form.get('candidate_id')
        job_id = request.form.get('job_id')
        interviewer_name = request.form.get('interviewer_name')
        interviewer_email = request.form.get('interviewer_email')
        appointment_type = request.form.get('appointment_type', 'Interview')
        scheduled_start = request.form.get('scheduled_start')
        duration = int(request.form.get('duration', 60))  # Default 60 minutes
        notes = request.form.get('notes', '')
        
        # Validate required fields
        if not all([candidate_id, job_id, interviewer_name, interviewer_email, scheduled_start]):
            flash('All required fields must be filled', 'error')
            return redirect(request.referrer)
        
        # Get candidate and job
        candidate = Candidate.query.get_or_404(candidate_id)
        job = JobDescription.query.get_or_404(job_id)
        
        # Parse datetime
        start_time = datetime.fromisoformat(scheduled_start)
        end_time = start_time + timedelta(minutes=duration)
        
        # Create Google Calendar event
        calendar_result = calendar_service.create_appointment(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            interviewer_name=interviewer_name,
            interviewer_email=interviewer_email,
            start_time=start_time,
            end_time=end_time,
            job_title=job.title,
            meeting_type=appointment_type
        )
        
        if calendar_result:
            # Save to database
            appointment = Appointment(
                candidate_id=candidate_id,
                job_id=job_id,
                interviewer_name=interviewer_name,
                interviewer_email=interviewer_email,
                appointment_type=appointment_type,
                scheduled_start=start_time,
                scheduled_end=end_time,
                google_event_id=calendar_result.get('event_id'),
                google_meet_link=calendar_result.get('meet_link'),
                google_calendar_link=calendar_result.get('event_link'),
                notes=notes
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash(f'Appointment scheduled successfully! Google Meet link: {calendar_result.get("meet_link", "N/A")}', 'success')
            return redirect(url_for('candidates', job_id=job_id))
        else:
            flash('Failed to create calendar appointment. Please try again.', 'error')
            return redirect(request.referrer)
            
    except Exception as e:
        flash(f'Error creating appointment: {str(e)}', 'error')
        return redirect(request.referrer)

@app.route('/appointments')
def appointments():
    """View all appointments"""
    appointments = Appointment.query.order_by(Appointment.scheduled_start.desc()).all()
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointment/<int:appointment_id>')
def appointment_detail(appointment_id):
    """View appointment details"""
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('appointment_detail.html', appointment=appointment)

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Cancel in Google Calendar
        if appointment.google_event_id:
            success = calendar_service.cancel_appointment(appointment.google_event_id)
            if success:
                appointment.status = 'cancelled'
                db.session.commit()
                flash('Appointment cancelled successfully', 'success')
            else:
                flash('Failed to cancel calendar event, but appointment marked as cancelled', 'warning')
                appointment.status = 'cancelled'
                db.session.commit()
        else:
            appointment.status = 'cancelled'
            db.session.commit()
            flash('Appointment cancelled successfully', 'success')
            
        return redirect(url_for('appointments'))
        
    except Exception as e:
        flash(f'Error cancelling appointment: {str(e)}', 'error')
        return redirect(url_for('appointments'))

@app.route('/reschedule_appointment/<int:appointment_id>', methods=['POST'])
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        new_start_time = datetime.fromisoformat(request.form.get('new_start_time'))
        duration = int(request.form.get('duration', 60))
        new_end_time = new_start_time + timedelta(minutes=duration)
        
        # Update in Google Calendar
        if appointment.google_event_id:
            result = calendar_service.update_appointment(
                appointment.google_event_id,
                start_time=new_start_time,
                end_time=new_end_time
            )
            
            if result:
                appointment.scheduled_start = new_start_time
                appointment.scheduled_end = new_end_time
                appointment.status = 'rescheduled'
                db.session.commit()
                flash('Appointment rescheduled successfully', 'success')
            else:
                flash('Failed to reschedule calendar event', 'error')
        else:
            appointment.scheduled_start = new_start_time
            appointment.scheduled_end = new_end_time
            appointment.status = 'rescheduled'
            db.session.commit()
            flash('Appointment rescheduled successfully', 'success')
            
        return redirect(url_for('appointment_detail', appointment_id=appointment_id))
        
    except Exception as e:
        flash(f'Error rescheduling appointment: {str(e)}', 'error')
        return redirect(url_for('appointment_detail', appointment_id=appointment_id))

@app.route('/calendar/disconnect')
def calendar_disconnect():
    """Disconnect from Google Calendar"""
    if 'google_credentials' in session:
        del session['google_credentials']
        flash('Disconnected from Google Calendar', 'info')
    return redirect(url_for('dashboard'))
