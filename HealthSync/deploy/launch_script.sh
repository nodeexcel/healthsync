#!/bin/bash

# HealthSync Deployment Script

set -e

# Variables
APP_NAME="HealthSync"
REPO_URL="https://github.com/yourusername/HealthSync.git"
BRANCH="main"
ENV_FILE=".env"
DB_URL="postgresql://user:password@localhost:5432/healthsync"
NEXT_PUBLIC_API_URL="https://api.healthsync.com"
DEPLOY_DIR="/var/www/$APP_NAME"
NODE_ENV="production"

# Function to log messages
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Clone the repository
log "Cloning repository..."
if [ -d "$DEPLOY_DIR" ]; then
    log "Directory $DEPLOY_DIR already exists. Pulling latest changes..."
    cd $DEPLOY_DIR
    git pull origin $BRANCH
else
    git clone -b $BRANCH $REPO_URL $DEPLOY_DIR
    cd $DEPLOY_DIR
fi

# Install dependencies for FastAPI
log "Installing FastAPI dependencies..."
pip install -r requirements.txt

# Install dependencies for Next.js
log "Installing Next.js dependencies..."
cd frontend
npm install

# Build Next.js application
log "Building Next.js application..."
npm run build

# Migrate the database
log "Running database migrations..."
cd ../backend
alembic upgrade head

# Start FastAPI application
log "Starting FastAPI application..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Start Next.js application
log "Starting Next.js application..."
cd ../frontend
nohup npm start &

# Set environment variables
log "Setting environment variables..."
export DATABASE_URL=$DB_URL
export NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
export NODE_ENV=$NODE_ENV

log "Deployment of $APP_NAME completed successfully!"