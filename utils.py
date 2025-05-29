import os
import csv
import tempfile
import logging
from datetime import datetime

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename_custom(filename):
    """Custom secure filename function with better handling"""
    import re
    from werkzeug.utils import secure_filename
    
    # Use werkzeug's secure_filename as base
    filename = secure_filename(filename)
    
    # Add timestamp to prevent conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    
    return f"{name}_{timestamp}{ext}"

def export_candidates_csv(candidates_data, job_title):
    """Export candidates data to CSV file"""
    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = f"candidates_{job_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join(temp_dir, filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Rank', 'Name', 'Email', 'Phone', 'Overall Score',
                'Skill Score', 'Experience Score', 'Education Score',
                'Experience Years', 'Key Skills', 'Skill Gaps',
                'Match Justification', 'Resume File'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rank, (candidate, match_score) in enumerate(candidates_data, 1):
                # Extract key skills (top 5)
                key_skills = ', '.join(candidate.extracted_skills[:5] if candidate.extracted_skills else [])
                
                # Extract skill gaps
                skill_gaps = ', '.join(match_score.skill_gaps[:5] if match_score.skill_gaps else [])
                
                writer.writerow({
                    'Rank': rank,
                    'Name': candidate.name,
                    'Email': candidate.email or 'N/A',
                    'Phone': candidate.phone or 'N/A',
                    'Overall Score': f"{match_score.overall_score:.1f}%",
                    'Skill Score': f"{match_score.skill_match_score:.1f}%",
                    'Experience Score': f"{match_score.experience_score:.1f}%",
                    'Education Score': f"{match_score.education_score:.1f}%",
                    'Experience Years': candidate.experience_years or 0,
                    'Key Skills': key_skills,
                    'Skill Gaps': skill_gaps,
                    'Match Justification': match_score.match_justification[:200] + '...' if len(match_score.match_justification) > 200 else match_score.match_justification,
                    'Resume File': candidate.filename
                })
        
        logging.info(f"CSV export created: {csv_path}")
        return csv_path
        
    except Exception as e:
        logging.error(f"Error creating CSV export: {str(e)}")
        raise

def format_score_badge(score):
    """Return Bootstrap badge class based on score"""
    if score >= 80:
        return 'badge bg-success'
    elif score >= 60:
        return 'badge bg-warning'
    else:
        return 'badge bg-danger'

def format_skill_list(skills, max_display=5):
    """Format skills list for display"""
    if not skills:
        return "No skills extracted"
    
    if len(skills) <= max_display:
        return ', '.join(skills)
    else:
        displayed = ', '.join(skills[:max_display])
        return f"{displayed} (+{len(skills) - max_display} more)"

def calculate_file_size_mb(file_path):
    """Calculate file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except:
        return 0

def validate_job_description(description):
    """Validate job description content"""
    if not description or len(description.strip()) < 50:
        return False, "Job description must be at least 50 characters long"
    
    # Check for basic job description elements
    required_keywords = ['experience', 'skill', 'require', 'qualif', 'responsib']
    description_lower = description.lower()
    
    found_keywords = sum(1 for keyword in required_keywords if keyword in description_lower)
    
    if found_keywords < 2:
        return False, "Job description should include information about requirements, skills, or qualifications"
    
    return True, "Valid job description"

def get_file_extension_icon(filename):
    """Get appropriate icon class for file extension"""
    ext = os.path.splitext(filename)[1].lower()
    
    icons = {
        '.pdf': 'bi-file-earmark-pdf',
        '.docx': 'bi-file-earmark-word',
        '.txt': 'bi-file-earmark-text'
    }
    
    return icons.get(ext, 'bi-file-earmark')

def truncate_text(text, max_length=100):
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def parse_skill_weights_form(form_data):
    """Parse skill weights from form data"""
    weights = {}
    
    for key, value in form_data.items():
        if key.startswith('weight_'):
            skill_name = key.replace('weight_', '')
            try:
                weight = float(value)
                # Ensure weight is between 0 and 1
                weight = max(0, min(1, weight))
                weights[skill_name] = weight
            except (ValueError, TypeError):
                logging.warning(f"Invalid weight value for skill {skill_name}: {value}")
                weights[skill_name] = 0.5  # Default weight
    
    return weights
