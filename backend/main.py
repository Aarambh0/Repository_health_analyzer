
from fastapi import FastAPI
from backend.routes.repository_routes import router as repository_router

app = FastAPI(
    title="Repository Health Analyzer",
    description="Analyze GitHub repositories and evaluate their health.",
    version="1.0.0",
)

app.include_router(repository_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Repository Health Analyzer",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Repository Health Analyzer",
    }