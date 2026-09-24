from fastapi import FastAPI

# Initialize FastAPI ASGI application instance
app = FastAPI(title="Health Check API")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Service is healthy"
    }
