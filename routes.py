import os
import json
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import JobDescription, Candidate, MatchScore
from document_parser import DocumentParser
from nlp_processor import NLPProcessor
from matching_engine import MatchingEngine
from utils import allowed_file, export_candidates_csv
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
        
        # Get candidates with scores above threshold (e.g., 70%)
        threshold = request.args.get('threshold', 70, type=float)
        
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

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
