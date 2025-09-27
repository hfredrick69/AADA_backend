#!/bin/bash

#Build the Docker Image (linux/amd64 compatible)
docker buildx create --use --name aada-builder || true
docker buildx use aada-builder
echo "Building docker image....."
docker buildx build --platform linux/amd64 -t aadaregistry12345.azurecr.io/aada-backend:latest --push .

#Restart the Azure App Service
echo "Restarting AADA Azure webapp...."
az webapp restart --name aada-backend-app12345 --resource-group aada-backend-rg
