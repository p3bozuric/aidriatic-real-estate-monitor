from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import users, user_goals, properties

app = FastAPI(
    title="Adriatic Real Estate Monitor API",
    description="API for monitoring and filtering real estate properties in the Adriatic region",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"]
)

app.include_router(
    user_goals.router,
    prefix="/api/v1/user-goals",
    tags=["user-goals"]
)

app.include_router(
    properties.router,
    prefix="/api/v1/properties",
    tags=["properties"]
)

@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Adriatic Real Estate Monitor API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)