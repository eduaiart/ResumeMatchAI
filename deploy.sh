#!/bin/bash

# Fit2Hire - Google Cloud Run Deployment Script
# This script automates the deployment of the Fit2Hire application to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"europe-west1"}
SERVICE_NAME="fit2hire"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}🚀 Starting deployment of Fit2Hire to Google Cloud Run${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Authenticate with gcloud (if not already authenticated)
echo -e "${YELLOW}🔐 Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${YELLOW}Please authenticate with gcloud:${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${YELLOW}📋 Setting project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

# Build the Docker image
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
docker build -t ${IMAGE_NAME} .

# Push the image to Google Container Registry
echo -e "${YELLOW}📦 Pushing image to Container Registry...${NC}"
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --concurrency 80 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --set-env-vars "FLASK_ENV=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${YELLOW}📝 Don't forget to:${NC}"
echo -e "${YELLOW}   1. Set up your database connection (DATABASE_URL)${NC}"
echo -e "${YELLOW}   2. Configure your Google Calendar OAuth credentials${NC}"
echo -e "${YELLOW}   3. Update your OAuth redirect URI to: ${SERVICE_URL}/oauth2callback${NC}"
echo -e "${YELLOW}   4. Set your environment variables in Cloud Run${NC}"

echo -e "${GREEN}🎉 Fit2Hire is now running on Google Cloud Run!${NC}"