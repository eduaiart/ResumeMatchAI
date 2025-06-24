# Resume Match AI

## Overview

Resume Match AI is a Flask-based web application that intelligently matches candidate resumes to job descriptions using advanced Natural Language Processing (NLP) techniques. The system automatically extracts information from uploaded resumes, analyzes job requirements, and provides scored rankings of candidates based on their fit for specific positions.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Components**: Bootstrap 5 with dark theme support
- **JavaScript**: Vanilla JavaScript for interactivity
- **Styling**: Custom CSS with Bootstrap integration
- **Charts**: Chart.js for data visualization

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM
- **Server**: Gunicorn for production deployment
- **Database**: PostgreSQL (configurable via DATABASE_URL)
- **File Processing**: Multi-format document parsing (PDF, DOCX, TXT)
- **NLP Engine**: spaCy for text processing and analysis

### Data Storage
- **Primary Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Local filesystem for uploaded documents
- **Session Management**: Flask sessions with configurable secret key

## Key Components

### Document Processing Pipeline
1. **DocumentParser**: Handles PDF, DOCX, and TXT file extraction
2. **NLPProcessor**: Uses spaCy for text analysis, skill extraction, and entity recognition
3. **MatchingEngine**: Implements TF-IDF vectorization and cosine similarity for candidate scoring

### Core Models
- **JobDescription**: Stores job postings with extracted requirements and skill categorization
- **Candidate**: Contains resume data, extracted information, and contact details
- **MatchScore**: Tracks matching results with detailed scoring breakdown

### Matching Algorithm
- **Skill Matching**: Categorized skill comparison (technical, soft skills)
- **Experience Scoring**: Years of experience alignment
- **Education Evaluation**: Educational background assessment
- **Semantic Analysis**: Text similarity using TF-IDF and cosine similarity
- **Weighted Scoring**: Configurable weights for different criteria

## Data Flow

1. **Job Creation**: Job descriptions are uploaded and analyzed for requirements and skills
2. **Resume Upload**: Candidate resumes are parsed and information is extracted
3. **Matching Process**: Algorithms calculate comprehensive match scores
4. **Ranking**: Candidates are ranked by overall compatibility score
5. **Export**: Results can be exported as CSV with filtering options

## External Dependencies

### Python Packages
- **Flask Stack**: Flask, Flask-SQLAlchemy for web framework
- **NLP**: spaCy for natural language processing
- **ML**: scikit-learn for similarity calculations
- **Document Processing**: PyPDF2, python-docx, pdfplumber for file parsing
- **Data**: pandas, numpy for data manipulation
- **Database**: psycopg2-binary for PostgreSQL connectivity

### System Requirements
- Python 3.11+
- PostgreSQL database
- spaCy English model (en_core_web_sm)

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Server**: Gunicorn with autoscale deployment target
- **Port**: 5000 (internal) mapped to 80 (external)
- **Environment**: PostgreSQL, OpenSSL, and locale support

### Production Settings
- **WSGI Server**: Gunicorn with proxy fix middleware
- **Database**: PostgreSQL with connection pooling
- **File Uploads**: 16MB size limit with secure filename handling
- **Logging**: Configurable logging levels

## Changelog

- June 24, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
Deployment preference: Google Cloud Platform for production hosting.
