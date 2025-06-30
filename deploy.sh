#!/bin/bash

# Resume Match AI - Google Cloud Deployment Script
# This script deploys the application to Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print functions
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="resume-match-ai"
DB_INSTANCE="resume-db"
DB_NAME="resumematchai"
DB_USER="appuser"

echo "=== Resume Match AI - Google Cloud Deployment ==="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI is not installed!"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "No project set. Run: gcloud config set project YOUR_PROJECT_ID"
            exit 1
        fi
    fi
    print_info "Using project: $PROJECT_ID"
}

# Check if services are enabled
check_services() {
    print_info "Checking required services..."
    
    REQUIRED_SERVICES=(
        "appengine.googleapis.com"
        "sqladmin.googleapis.com"
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
    )
    
    for service in "${REQUIRED_SERVICES[@]}"; do
        if ! gcloud services list --enabled --filter="name:$service" --format="value(name)" | grep -q "$service"; then
            print_info "Enabling $service..."
            gcloud services enable "$service"
        fi
    done
    
    print_success "All required services are enabled"
}

# Setup database
setup_database() {
    print_info "Setting up Cloud SQL database..."
    
    # Check if instance exists
    if ! gcloud sql instances describe "$DB_INSTANCE" &>/dev/null; then
        print_info "Creating Cloud SQL instance (this takes 10-15 minutes)..."
        gcloud sql instances create "$DB_INSTANCE" \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region="$REGION" \
            --storage-size=10GB \
            --storage-type=SSD \
            --backup \
            --backup-start-time=03:00
    else
        print_info "Cloud SQL instance already exists"
    fi
    
    # Create database
    if ! gcloud sql databases describe "$DB_NAME" --instance="$DB_INSTANCE" &>/dev/null; then
        print_info "Creating database..."
        gcloud sql databases create "$DB_NAME" --instance="$DB_INSTANCE"
    fi
    
    # Get database connection
    CONNECTION_NAME=$(gcloud sql instances describe "$DB_INSTANCE" --format="value(connectionName)")
    print_success "Database setup complete. Connection: $CONNECTION_NAME"
}

# Deploy to App Engine
deploy_app_engine() {
    print_info "Deploying to App Engine..."
    
    # Check if App Engine app exists
    if ! gcloud app describe &>/dev/null; then
        print_info "Creating App Engine application..."
        gcloud app create --region="$REGION"
    fi
    
    # Create .env.yaml if it doesn't exist
    if [ ! -f ".env.yaml" ]; then
        print_warning "Creating .env.yaml file. Please update with your credentials!"
        cat > .env.yaml << EOF
env_variables:
  DATABASE_URL: "postgresql://$DB_USER:YOUR_PASSWORD@/resumematchai?host=/cloudsql/$CONNECTION_NAME"
  SESSION_SECRET: "$(openssl rand -base64 32)"
EOF
        print_warning "Please edit .env.yaml with your database password!"
        read -p "Press Enter after updating .env.yaml..."
    fi
    
    # Deploy
    gcloud app deploy app.yaml --env-vars-file=.env.yaml --quiet
    
    APP_URL=$(gcloud app describe --format="value(defaultHostname)")
    print_success "App Engine deployment complete!"
    print_success "URL: https://$APP_URL"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    print_info "Deploying to Cloud Run..."
    
    # Build and push Docker image
    print_info "Building Docker image..."
    gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME" .
    
    # Get database password
    echo -n "Enter database password: "
    read -s DB_PASSWORD
    echo
    
    # Deploy to Cloud Run
    print_info "Deploying to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --port 5000 \
        --set-env-vars "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@/resumematchai?host=/cloudsql/$CONNECTION_NAME" \
        --set-env-vars "SESSION_SECRET=$(openssl rand -base64 32)" \
        --set-env-vars "FLASK_ENV=production" \
        --add-cloudsql-instances "$CONNECTION_NAME"
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)")
    print_success "Cloud Run deployment complete!"
    print_success "URL: $SERVICE_URL"
}

# Main menu
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) App Engine (Traditional hosting)"
    echo "2) Cloud Run (Serverless containers)"
    echo "3) Setup database only"
    echo "4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            get_project_id
            check_services
            setup_database
            deploy_app_engine
            ;;
        2)
            get_project_id
            check_services
            setup_database
            deploy_cloud_run
            ;;
        3)
            get_project_id
            check_services
            setup_database
            ;;
        4)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            show_menu
            ;;
    esac
}

# Check if running with arguments
if [ "$1" = "appengine" ]; then
    get_project_id
    check_services
    setup_database
    deploy_app_engine
elif [ "$1" = "cloudrun" ]; then
    get_project_id
    check_services
    setup_database
    deploy_cloud_run
elif [ "$1" = "database" ]; then
    get_project_id
    check_services
    setup_database
else
    show_menu
fi

print_success "Deployment completed successfully!"