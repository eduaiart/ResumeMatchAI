# Resume Match AI

## Overview

Resume Match AI is a Flask-based web application that intelligently matches candidate resumes to job descriptions using advanced Natural Language Processing (NLP) techniques. The system automatically parses resumes in multiple formats (PDF, DOCX, TXT), extracts relevant information, and provides comprehensive scoring and ranking of candidates based on job requirements.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Components**: Bootstrap 5 with dark theme support and responsive design
- **JavaScript**: Vanilla JavaScript for interactive features (form validation, file uploads, search/filter functionality)
- **Styling**: Custom CSS with Bootstrap integration, featuring card-based layouts and hover effects
- **Charts**: Chart.js for data visualization and scoring breakdowns

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Server**: Gunicorn configured for production deployment
- **Database**: PostgreSQL (configurable via DATABASE_URL environment variable)
- **File Processing**: Multi-format document parsing supporting PDF, DOCX, and TXT files
- **NLP Engine**: spaCy (en_core_web_sm model) for text processing, entity recognition, and skill extraction
- **Machine Learning**: scikit-learn for TF-IDF vectorization and cosine similarity calculations

### Data Storage
- **Primary Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Local filesystem with secure filename handling
- **Session Management**: Flask sessions with configurable secret key
- **Data Models**: Three main entities (JobDescription, Candidate, MatchScore) with proper relationships

## Key Components

### Document Processing Pipeline
1. **DocumentParser**: Handles extraction from PDF (PyPDF2/pdfplumber), DOCX (python-docx), and TXT files
2. **NLPProcessor**: Uses spaCy for comprehensive text analysis including:
   - Named entity recognition for contact information
   - Skill extraction across technical and soft skill categories
   - Experience and education parsing
   - Text preprocessing and tokenization
3. **MatchingEngine**: Implements sophisticated scoring algorithms using:
   - TF-IDF vectorization for semantic similarity
   - Cosine similarity calculations
   - Weighted scoring across multiple criteria
   - Skill gap analysis

### Core Data Models
- **JobDescription**: Stores job postings with extracted requirements, categorized skills, and configurable weights
- **Candidate**: Contains resume data, extracted information (skills, experience, education), and contact details
- **MatchScore**: Tracks comprehensive matching results with detailed scoring breakdown and justification

### Matching Algorithm
The system uses a multi-criteria scoring approach:
- **Skill Matching**: Categorized comparison of technical skills, soft skills, and domain expertise
- **Experience Scoring**: Alignment of years of experience with job requirements
- **Education Evaluation**: Educational background assessment and relevance scoring
- **Semantic Analysis**: Text similarity using TF-IDF vectors and cosine similarity
- **Weighted Scoring**: Configurable weights (Skills: 40%, Experience: 30%, Education: 20%, Semantic: 10%)

## Data Flow

1. **Job Creation**: Job descriptions are uploaded, analyzed for requirements, and skills are categorized
2. **Resume Upload**: Candidate resumes are parsed, information is extracted, and profiles are created
3. **Matching Process**: Comprehensive scoring is performed using the matching engine
4. **Results Presentation**: Candidates are ranked and presented with detailed scoring breakdowns
5. **Export Functionality**: Results can be exported to CSV with configurable score thresholds

## External Dependencies

### Core Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **spaCy**: NLP processing (requires en_core_web_sm model)
- **scikit-learn**: Machine learning algorithms for text analysis
- **PyPDF2/pdfplumber**: PDF text extraction
- **python-docx**: DOCX document processing
- **pandas**: Data manipulation and export functionality

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Bootstrap Icons**: Icon library
- **Chart.js**: Data visualization
- **Custom CSS/JS**: Enhanced user experience

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with debug mode
- **Database**: PostgreSQL (local or cloud-based)
- **File Storage**: Local filesystem

### Production Deployment Options
1. **Google Cloud Platform**: 
   - App Engine for application hosting
   - Cloud SQL for PostgreSQL database
   - Cloud Storage for file uploads (future enhancement)

2. **Docker Containerization**:
   - Dockerized application with multi-stage builds
   - Docker Compose for local development with database
   - Container registry support for cloud deployment

3. **Traditional Hosting**:
   - Gunicorn WSGI server
   - Reverse proxy (nginx recommended)
   - PostgreSQL database
   - SSL/TLS termination

### Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string
- **SESSION_SECRET**: Flask session encryption key
- **UPLOAD_FOLDER**: Directory for file uploads
- **MAX_CONTENT_LENGTH**: File upload size limit (16MB)

## Changelog

- June 30, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.