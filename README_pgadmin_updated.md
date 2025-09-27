# AADA Backend Deployment Guide

This README details step-by-step instructions to deploy the AADA FastAPI + PostgreSQL backend to Azure.

---

## Prerequisites

- Run `curl -4 ifconfig.me` to get your public IPv4 address before adding a firewall rule.


- **Azure CLI** installed and authenticated (`az login`).
- **Docker** installed for local container builds.
- Your FastAPI project is in `AADA_backend_full/`.

---

## 1. Provision Azure Resources

### 1.1 Create a Resource Group
```bash
RG="aada-backend-rg"
LOCATION="eastus"
az group create --name $RG --location $LOCATION
```

### 1.2 Create Azure PostgreSQL Server & Database
```bash
PG_SERVER="aada-pg-server$RANDOM"
PG_ADMIN="aadaadmin"
PG_PASS="YourStrongP@ssw0rd!"

az postgres flexible-server create --resource-group $RG --name $PG_SERVER --location $LOCATION --admin-user $PG_ADMIN --admin-password $PG_PASS --sku-name Standard_B1ms --tier Burstable --version 14 --storage-size 32 --public-access 0.0.0.0

# Create the application-specific database (used by FastAPI and the mobile app)
az postgres flexible-server db create --resource-group $RG --server-name $PG_SERVER --database-name aada_local

az postgres server firewall-rule create   --resource-group $RG   --server-name $PG_SERVER   --name AllowAll   --start-ip-address 0.0.0.0   --end-ip-address 255.255.255.255
```

**Connection string**:  
```
postgresql://$PG_ADMIN:$PG_PASS@$PG_SERVER.postgres.database.azure.com:5432/aada_local?sslmode=require
```

---

## 2. Containerize FastAPI App

Create `Dockerfile` in `AADA_backend_full/`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build & test:
```bash
cd AADA_backend_full
docker build -t aada-backend:latest .
docker run -e DATABASE_URL="<your-conn-string>" -p 8000:8000 aada-backend:latest
```

---

## 3. Push to Azure Container Registry (ACR)
```bash
ACR_NAME="aadaRegistry$RANDOM"
az acr create --resource-group $RG --name $ACR_NAME --sku Basic
az acr login --name $ACR_NAME
docker tag aada-backend:latest $ACR_NAME.azurecr.io/aada-backend:latest
docker push $ACR_NAME.azurecr.io/aada-backend:latest
```

---

## 4. Deploy to Azure Web App for Containers
```bash
APP_NAME="aada-backend-app$RANDOM"

az appservice plan create   --resource-group $RG   --name aada-backend-plan   --is-linux   --sku B1

az webapp create   --resource-group $RG   --plan aada-backend-plan   --name $APP_NAME   --deployment-container-image-name $ACR_NAME.azurecr.io/aada-backend:latest

ACR_PASS=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
az webapp config container set   --resource-group $RG   --name $APP_NAME   --docker-custom-image-name $ACR_NAME.azurecr.io/aada-backend:latest   --docker-registry-server-url https://$ACR_NAME.azurecr.io   --docker-registry-server-user $ACR_NAME   --docker-registry-server-password $ACR_PASS

az webapp config appsettings set   --resource-group $RG   --name $APP_NAME   --settings     DATABASE_URL="postgresql://$PG_ADMIN:$PG_PASS@$PG_SERVER.postgres.database.azure.com:5432/aada_local?sslmode=require"     ALLOW_ORIGINS="*"
```

Service URL:  
```
https://$APP_NAME.azurewebsites.net
```

---

## 5. (Optional) CI/CD with GitHub Actions

Create `.github/workflows/azure-deploy.yml`:
```yaml
name: Azure Container Deploy

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.ACR_NAME }}.azurecr.io
          username: ${{ secrets.ACR_NAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      - run: |
          docker build -t ${{ secrets.ACR_NAME }}.azurecr.io/aada-backend:latest .
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/aada-backend:latest

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ secrets.APP_NAME }}
          images: ${{ secrets.ACR_NAME }}.azurecr.io/aada-backend:latest
```

---

## 6. Verify & Update Flutter App

Test endpoint:
```bash
curl https://$APP_NAME.azurewebsites.net/students
```

Update Flutter base URLs to:
```dart
Uri.parse('https://$APP_NAME.azurewebsites.net/auth/login?email=\$email')
```

---

Done! 

---

## 7. Using pgAdmin (Optional)

To connect to your Azure PostgreSQL Flexible Server from pgAdmin:

- **Host**: `aada-pg-server27841.postgres.database.azure.com`
- **Port**: `5432`
- **Username**: `aadaadmin@aada-pg-server27841`
- **Password**: `![Screenshot 2025-06-29 at 12.49.15 PM](/Users/herbert/Library/Application Support/typora-user-images/Screenshot 2025-06-29 at 12.49.15 PM.png)` (or your updated value)
- **Maintenance DB**: `postgres`
- **SSL Mode**: `Require`

> 🔐 Note: `postgres` is the default maintenance database. Your application backend should use the `aada_local` database instead.

### Application Connection String Example

```bash
postgresql://aadaadmin:Universe1111@aada-pg-server27841.postgres.database.azure.com:5432/aada_local?sslmode=require
```
