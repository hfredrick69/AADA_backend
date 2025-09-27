# AADA Backend API

American Academy of Dental Assistants - Student Management System

## Tech Stack
- FastAPI
- PostgreSQL (Azure)
- Square Payments API
- Firebase Cloud Messaging
- Azure App Service

## Setup
1. Copy `.env.example` to `.env`
2. Fill in your credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn main:app --reload`

## Project Structure
- `main.py` - FastAPI application entry
- `models.py` - SQLAlchemy database models
- `routers/` - API endpoints
- `alembic/` - Database migrations

## Deployment
Deployed on Azure App Service
See deployment scripts in root directory

## Development Status
Currently implementing:
- [ ] JWT Authentication
- [ ] User registration flow
- [ ] Document upload system
- [ ] Enhanced payment integration
