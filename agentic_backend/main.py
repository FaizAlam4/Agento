from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Agentic Backend",
    description="Backend service for Agentic application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    environment: str

class TestResponse(BaseModel):
    message: str
    version: str
    timestamp: str

# In-memory storage (replace with database in production)
users_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
]

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="OK",
        message="Backend service is running",
        timestamp=datetime.now().isoformat(),
        environment=os.getenv("PYTHON_ENV", "development")
    )

# API routes
@app.get("/api/test", response_model=TestResponse)
async def test_endpoint():
    return TestResponse(
        message="Hello from Agentic Backend!",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

# Users endpoints
@app.get("/api/users", response_model=List[User])
async def get_users():
    return users_db

@app.post("/api/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    new_user = {
        "id": int(datetime.now().timestamp() * 1000),  # Using timestamp as ID
        "name": user.name,
        "email": user.email,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    return new_user

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    env = os.getenv("PYTHON_ENV", "development")
    error_message = str(exc) if env == "development" else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong!",
            "message": error_message
        }
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Route {request.url.path} not found"
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    env = os.getenv("PYTHON_ENV", "development")
    
    print(f"🚀 Backend server starting on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌍 Environment: {env}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=env == "development"
    )