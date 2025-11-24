#!/bin/bash

# ============================================================================
# Azure Deployment Script for Diabetes Predictor
# ============================================================================

set -e  # Exit on error

# Configuration - CHANGE THESE VALUES
RG="diabetes-predictor-rg"
ACR_NAME="diabetesacr"
APP_NAME="diabetes-predictor-ai"
PLAN_NAME="diabetes-plan"
LOCATION="eastus"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Azure Deployment for Diabetes Predictor${NC}"
echo "=================================================="

# Check if required tools are installed
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v az >/dev/null 2>&1 || { echo -e "${RED}❌ Azure CLI not installed${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker not installed${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js not installed${NC}"; exit 1; }
echo -e "${GREEN}✅ All prerequisites met${NC}"

# Login to Azure
echo -e "${YELLOW}🔐 Logging into Azure...${NC}"
az login --use-device-code

# Set subscription (optional - uncomment and set if you have multiple subscriptions)
# echo -e "${YELLOW}Setting subscription...${NC}"
# az account set --subscription "Your-Subscription-Name"

# Create Resource Group
echo -e "${YELLOW}🏗️  Creating resource group: $RG${NC}"
az group create --name $RG --location $LOCATION --output table

# Create Azure Container Registry
echo -e "${YELLOW}📦 Creating Azure Container Registry: $ACR_NAME${NC}"
az acr create \
  --resource-group $RG \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true \
  --output table

# Build Frontend
echo -e "${YELLOW}📦 Building React frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi
npm run build
cd ..
echo -e "${GREEN}✅ Frontend built successfully${NC}"

# Build Docker Image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
docker build -t $ACR_NAME.azurecr.io/diabetes-predictor:$IMAGE_TAG .
echo -e "${GREEN}✅ Docker image built${NC}"

# Login to ACR and Push Image
echo -e "${YELLOW}📤 Pushing Docker image to ACR...${NC}"
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/diabetes-predictor:$IMAGE_TAG
echo -e "${GREEN}✅ Image pushed to registry${NC}"

# Get ACR Credentials
echo -e "${YELLOW}🔑 Retrieving ACR credentials...${NC}"
ACR_CREDS=$(az acr credential show --name $ACR_NAME -o json)
ACR_USER=$(echo $ACR_CREDS | grep -oP '"username":\s*"\K[^"]+')
ACR_PASS=$(echo $ACR_CREDS | grep -oP '"passwords".*?"value":\s*"\K[^"]+' | head -1)

# Create App Service Plan
echo -e "${YELLOW}🌐 Creating App Service Plan: $PLAN_NAME${NC}"
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RG \
  --is-linux \
  --sku B1 \
  --output table

# Create Web App
echo -e "${YELLOW}🌍 Creating Web App: $APP_NAME${NC}"
az webapp create \
  --resource-group $RG \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --deployment-container-image-name $ACR_NAME.azurecr.io/diabetes-predictor:$IMAGE_TAG \
  --output table

# Configure Container Settings
echo -e "${YELLOW}⚙️  Configuring container settings...${NC}"
az webapp config container set \
  --name $APP_NAME \
  --resource-group $RG \
  --docker-custom-image-name $ACR_NAME.azurecr.io/diabetes-predictor:$IMAGE_TAG \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $ACR_USER \
  --docker-registry-server-password $ACR_PASS

# Prompt for environment variables
echo -e "${YELLOW}🔧 Setting environment variables...${NC}"
echo -e "${BLUE}Please enter your configuration:${NC}"
read -p "GROQ_API_KEY: " GROQ_KEY
read -p "FIREBASE_DATABASE_URL (or press Enter for default): " FIREBASE_URL
FIREBASE_URL=${FIREBASE_URL:-"https://diabetes-prediction-22082-default-rtdb.firebaseio.com"}
read -p "SECRET_KEY (or press Enter to generate): " SECRET_KEY
SECRET_KEY=${SECRET_KEY:-$(openssl rand -base64 32)}

# Set App Settings
az webapp config appsettings set \
  --resource-group $RG \
  --name $APP_NAME \
  --settings \
    GROQ_API_KEY="$GROQ_KEY" \
    FIREBASE_DATABASE_URL="$FIREBASE_URL" \
    SECRET_KEY="$SECRET_KEY" \
    WEBSITES_PORT=8080 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
  --output table

# Enable HTTPS Only
echo -e "${YELLOW}🔒 Enabling HTTPS only...${NC}"
az webapp update \
  --resource-group $RG \
  --name $APP_NAME \
  --https-only true

# Enable Container Logging
echo -e "${YELLOW}📋 Enabling container logging...${NC}"
az webapp log config \
  --name $APP_NAME \
  --resource-group $RG \
  --docker-container-logging filesystem \
  --level information

# Restart App
echo -e "${YELLOW}🔄 Restarting application...${NC}"
az webapp restart \
  --name $APP_NAME \
  --resource-group $RG

# Show deployment info
echo ""
echo -e "${GREEN}=================================================="
echo -e "✅ Deployment Completed Successfully!"
echo -e "==================================================${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Information:${NC}"
echo -e "Resource Group: ${GREEN}$RG${NC}"
echo -e "App Name: ${GREEN}$APP_NAME${NC}"
echo -e "Container Registry: ${GREEN}$ACR_NAME${NC}"
echo -e "App Service Plan: ${GREEN}$PLAN_NAME${NC}"
echo ""
echo -e "${BLUE}🌍 Your application is available at:${NC}"
echo -e "${GREEN}https://$APP_NAME.azurewebsites.net${NC}"
echo ""
echo -e "${YELLOW}📝 Useful commands:${NC}"
echo -e "View logs: ${BLUE}az webapp log tail -n $APP_NAME -g $RG${NC}"
echo -e "Restart app: ${BLUE}az webapp restart -n $APP_NAME -g $RG${NC}"
echo -e "SSH into container: ${BLUE}az webapp ssh -n $APP_NAME -g $RG${NC}"
echo -e "Delete resources: ${BLUE}az group delete -n $RG --yes${NC}"
echo ""
echo -e "${YELLOW}⏳ Note: It may take 2-3 minutes for the app to start.${NC}"
echo -e "${YELLOW}Monitor logs with: az webapp log tail -n $APP_NAME -g $RG${NC}"
