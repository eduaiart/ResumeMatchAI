#!/bin/bash

# Resume Match AI - Google Cloud Setup Script
# This script helps beginners deploy to Google Cloud Platform

echo "=== Resume Match AI - Google Cloud Setup ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed!"
        echo "Please install it from: https://cloud.google.com/sdk/docs/install"
        echo "Then run this script again."
        exit 1
    fi
    print_success "Google Cloud CLI is installed"
}

# Get project details from user
get_project_info() {
    echo ""
    print_status "Let's set up your Google Cloud project..."
    
    read -p "Enter your desired project name (e.g., my-resume-app): " PROJECT_BASE
    # Add random numbers to make it unique
    PROJECT_ID="${PROJECT_BASE}-$(date +%s)"
    
    read -s -p "Enter a strong database password: " DB_PASSWORD
    echo ""
    
    read -p "Enter a secret key for sessions (long random string): " SESSION_SECRET
    
    echo ""
    print_status "Project ID will be: $PROJECT_ID"
}

# Main setup function
setup_gcp() {
    print_status "Starting Google Cloud setup..."
    
    # Login to gcloud
    print_status "Logging in to Google Cloud..."
    gcloud auth login
    
    # Create project
    print_status "Creating project: $PROJECT_ID"
    gcloud projects create $PROJECT_ID
    gcloud config set project $PROJECT_ID
    
    print_warning "IMPORTANT: You need to enable billing for this project!"
    print_warning "Go to: https://console.cloud.google.com/billing"
    read -p "Press Enter after you've enabled billing..."
    
    # Enable services
    print_status "Enabling required services..."
    gcloud services enable appengine.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    # Create App Engine app
    print_status "Creating App Engine application..."
    gcloud app create --region=us-central1
    
    # Create Cloud SQL instance
    print_status "Creating database (this takes 5-10 minutes)..."
    gcloud sql instances create resume-db \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=us-central1 \
        --storage-size=10GB \
        --storage-type=SSD
    
    # Create database and user
    print_status "Setting up database..."
    gcloud sql databases create resumematchai --instance=resume-db
    gcloud sql users create appuser --instance=resume-db --password="$DB_PASSWORD"
    
    # Get connection name
    CONNECTION_NAME=$(gcloud sql instances describe resume-db --format="value(connectionName)")
    
    # Create .env.yaml file
    print_status "Creating environment configuration..."
    cat > .env.yaml << EOF
env_variables:
  DATABASE_URL: "postgresql://appuser:${DB_PASSWORD}@/resumematchai?host=/cloudsql/${CONNECTION_NAME}"
  SESSION_SECRET: "${SESSION_SECRET}"
EOF
    
    print_success "Setup complete!"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Run: gcloud app deploy app.yaml --env-vars-file=.env.yaml"
    echo "2. Run: gcloud app browse"
    echo ""
    echo "=== Important Information ==="
    echo "Project ID: $PROJECT_ID"
    echo "Database Connection: $CONNECTION_NAME"
    echo "Environment file created: .env.yaml"
    echo ""
    print_warning "Keep your .env.yaml file secure - it contains passwords!"
}

# Main execution
main() {
    check_gcloud
    get_project_info
    setup_gcp
}

# Run the script
main