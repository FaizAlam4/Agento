import os
import uuid
from datetime import datetime
from typing import List
from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from dotenv import load_dotenv

# Import database and models
from database import get_async_db, engine
from models.auth import Organization
from models import *  # Import all models
from auth.dependencies import get_current_user
from auth.rbac import RBACManager
from auth.decorators import require_system_admin, require_org_admin

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Smart Customer Support API",
    description="Multi-modal RAG chatbot for customer support with RBAC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include organization router
from routers.organizations import router as org_router
app.include_router(org_router)

app.include_router(org_router)



# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "Backend service is running",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("PYTHON_ENV", "development")
    }

# Test endpoint
@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "Hello from Smart Customer Support Backend!",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "RBAC Authentication",
            "Multi-modal RAG",
            "Web Scraping",
            "Real-time Chat"
        ]
    }

# Database check endpoint
@app.get("/api/db-check")
async def database_check(db: AsyncSession = Depends(get_async_db)):
    """Check database connectivity"""
    try:
        # Simple query to test connection
        await db.execute("SELECT 1")
        return {
            "status": "OK",
            "message": "Database connection successful",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Protected test endpoint
@app.get("/api/protected-test")
async def protected_test(current_user: User = Depends(get_current_user)):
    """Test endpoint that requires authentication"""
    return {
        "message": f"Hello {current_user.username}!",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "timestamp": datetime.now().isoformat()
    }

# RBAC test endpoint
@app.get("/api/rbac-test")
async def rbac_test(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Test endpoint to check RBAC functionality"""
    rbac = RBACManager(db)
    
    permissions = await rbac.get_user_permissions(str(current_user.id))
    roles = await rbac.get_user_roles(str(current_user.id))
    
    return {
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email
        },
        "roles": roles,
        "permissions": permissions,
        "timestamp": datetime.now().isoformat()
    }

# Example: Organization creation endpoint (super-admin only)
@app.post("/api/organizations/create")
async def create_organization(
    name: str,
    slug: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    return await require_system_admin(_create_organization)(
        name=name, slug=slug, db=db, current_user=current_user
    )

async def _create_organization(name, slug, db, current_user):
    # ...organization creation logic...
    return {"status": "created", "name": name, "slug": slug}

# Example: Scrap UI endpoint (org-admin only)
@app.get("/api/scrap-ui")
async def scrap_ui(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    return await require_org_admin(_scrap_ui)(db=db, current_user=current_user)

async def _scrap_ui(db, current_user):
    # ...scrap UI logic...
    return {"status": "visible", "user": current_user.username}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    env = os.getenv("PYTHON_ENV", "development")
    error_message = str(exc) if env == "development" else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong!",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Route {request.url.path} not found",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    env = os.getenv("PYTHON_ENV", "development")
    
    print(f"🚀 Smart Customer Support Backend starting on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"📚 API docs: http://localhost:{port}/docs")
    print(f"🌍 Environment: {env}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=env == "development"
    )