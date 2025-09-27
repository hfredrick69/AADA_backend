#!/bin/bash

# === CONFIGURATION ===
ACR_NAME="aadaregistry12345"
IMAGE_NAME="aada-backend"
RESOURCE_GROUP="aada-backend-rg"
WEBAPP_NAME="aada-backend-app12345"
TAG="latest"  # You can set this to a version if you want (e.g., v1.0.1)

# === STEP 1: Build Docker image locally ===
echo "🚀 Building Docker image..."
docker build -t $IMAGE_NAME .

# === STEP 2: Tag the image for ACR ===
echo "🏷️ Tagging image for ACR push..."
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# === STEP 3: Login to ACR ===
echo "🔐 Logging in to Azure Container Registry..."
az acr login --name $ACR_NAME

# === STEP 4: Push image to ACR ===
echo "📦 Pushing image to ACR..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# === STEP 5: Restart Azure Web App ===
echo "🔄 Restarting Azure Web App..."
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deployment complete!"
