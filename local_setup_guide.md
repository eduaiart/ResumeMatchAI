# Local Setup Guide - Resume Match AI

## 📁 Essential Files for Local Development

### Core Application Files
```
├── main.py                    # Flask application entry point
├── app.py                     # Flask app initialization and database setup
├── models.py                  # Database models (JobDescription, Candidate, MatchScore)
├── routes.py                  # All web routes and endpoints
├── nlp_processor.py           # NLP processing for resume/job analysis
├── matching_engine.py         # Candidate matching algorithms
├── document_parser.py         # Document parsing (PDF, DOCX, TXT)
├── utils.py                   # Utility functions
└── requirements.txt           # Python dependencies
```

### Frontend Files
```
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── upload.html            # Upload page
│   ├── dashboard.html         # Main dashboard
│   ├── job_detail.html        # Job details page
│   ├── candidates.html        # Candidate ranking page
│   └── ...
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   └── js/
│       └── main.js            # JavaScript functionality
```

### Configuration Files
```
├── .env.example               # Environment variables template
├── docker-compose.yml         # Local development with database
└── requirements.txt           # Python dependencies
```

## 🛠️ Local Setup Steps

### 1. Install Python Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy model (required for NLP)
python -m spacy download en_core_web_sm
```

### 2. Set Up Database
```bash
# Option 1: Use Docker (easiest)
docker-compose up -d postgres

# Option 2: Install PostgreSQL locally
# Create database: resumematchai
# Create user with permissions
```

### 3. Environment Variables
Create `.env` file with:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/resumematchai
SESSION_SECRET=your-long-random-secret-key
FLASK_ENV=development
```

### 4. Run Application
```bash
# Start the Flask development server
python main.py

# Or use gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 main:app

# Access at: http://localhost:5000
```

## 📦 Quick Start with Docker
```bash
# Start everything (app + database)
docker-compose up -d

# Access at: http://localhost:5000
# Database runs on: localhost:5432
```

## 🔍 File Dependencies

### Python Dependencies (requirements.txt):
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
spacy==3.7.2
scikit-learn==1.3.2
pandas==2.1.4
pypdf2==3.0.1
python-docx==1.1.0
pdfplumber==0.10.0
gunicorn==23.0.0
```

### Key Folders:
- **uploads/** - Stores uploaded resume files
- **instance/** - Flask instance folder
- **templates/** - HTML templates
- **static/** - CSS, JavaScript, images

## 🚀 Minimal Setup (Core Files Only)

For basic functionality, you need these files:
```
main.py
app.py
models.py
routes.py
nlp_processor.py
matching_engine.py
document_parser.py
utils.py
requirements.txt
templates/ (all HTML files)
static/ (CSS/JS files)
```

## 🔧 Environment Setup

### Create Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Install Dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Database Setup:
```bash
# With PostgreSQL installed locally
createdb resumematchai
psql resumematchai

# Create tables (automatic on first run)
python main.py
```

## 📋 Testing Your Setup

1. **Start the application**: `python main.py`
2. **Visit**: http://localhost:5000
3. **Upload a job description** (PDF/TXT)
4. **Upload some resumes** (PDF/DOCX/TXT)
5. **View candidate rankings** in dashboard

## 🛠️ Development Tools

### Recommended Extensions:
- **Flask development server** (automatic reloading)
- **Database browser** (view PostgreSQL data)
- **Code editor** with Python support

### Debug Mode:
Set `FLASK_ENV=development` for:
- Automatic reloading on code changes
- Detailed error messages
- Debug toolbar

All the files are already in your project and ready to run locally!