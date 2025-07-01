#!/usr/bin/env python3
"""
Local development runner for Resume Match AI
This script sets up the environment and runs the Flask application locally
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment variables for local development"""
    
    # Load environment variables from .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print("Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Set {key}")
    
    # Set default values if not provided
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/resumematchai'
        print("Using default DATABASE_URL")
    
    if 'SESSION_SECRET' not in os.environ:
        os.environ['SESSION_SECRET'] = 'dev-secret-key-change-in-production'
        print("Using default SESSION_SECRET")
    
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
        print("Using development environment")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import spacy
        import sklearn
        import pandas
        import pdfplumber
        import docx
        print("✓ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_spacy_model():
    """Check if spaCy model is downloaded"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model 'en_core_web_sm' is available")
        return True
    except OSError:
        print("✗ spaCy model 'en_core_web_sm' not found")
        print("Please run: python -m spacy download en_core_web_sm")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'instance']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def main():
    """Main function to run the local development server"""
    print("🚀 Starting Resume Match AI - Local Development")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check spaCy model
    if not check_spacy_model():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete! Starting Flask application...")
    print("📱 Access your app at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 50 + "\n")
    
    # Import and run the Flask app
    from main import app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()