#!/bin/bash
# Deployment script for SynOmix V5

set -e

echo "🚀 SynOmix V5 Deployment Script"
echo "================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build frontend
echo -e "${BLUE}📦 Building frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

echo -e "${GREEN}✅ Frontend built successfully${NC}"

# Build Docker image
echo -e "${BLUE}🐳 Building Docker image...${NC}"
docker build -t synomix-v5 .

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Run with docker-compose
echo -e "${BLUE}🚢 Starting services with Docker Compose...${NC}"
docker-compose up -d

echo -e "${GREEN}✅ Services started successfully${NC}"

echo ""
echo "🎉 Deployment complete!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
