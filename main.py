from fastapi import FastAPI
from app.api.v1 import blogs

app = FastAPI(title="Blog Service API", version="1.0.0")

# Include routers
app.include_router(blogs.router, prefix="/api/v1", tags=["blogs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)