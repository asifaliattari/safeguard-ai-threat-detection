"""
SafeGuard AI Backend - Main FastAPI Application
AI-Native Video Anomaly Detection System

@spec docs/specs/001-backend-foundation.md
@plan docs/plans/001-backend-foundation-plan.md
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SafeGuard AI Backend",
    description="AI-powered real-time video anomaly detection system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.pipelines: dict[str, any] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.pipelines:
            del self.pipelines[user_id]
        print(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_detection(self, user_id: str, detection: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(detection)
            except Exception as e:
                print(f"Failed to send detection to {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SafeGuard AI Backend",
        "active_connections": len(manager.active_connections),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SafeGuard AI Backend API",
        "docs": "/api/docs",
        "health": "/health"
    }

# WebSocket endpoint for video stream detection
@app.websocket("/ws/detect/{user_id}")
async def websocket_detect_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time video detection

    Receives video frames from frontend, processes them through
    the detection pipeline, and sends back detection results.
    """
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Receive frame as bytes
            data = await websocket.receive_bytes()

            # TODO: Decode image and run detection pipeline
            # For now, just echo back a test response
            await manager.send_detection(user_id, {
                "message": "Detection pipeline not yet implemented",
                "frame_size": len(data),
                "user_id": user_id
            })

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"Error in WebSocket for {user_id}: {e}")
        manager.disconnect(user_id)

# Models info endpoint
@app.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "models": {
            "yolo": {"status": "not_loaded", "version": "yolov8n"},
            "action": {"status": "not_loaded", "model": "timesformer-base"},
            "fire": {"status": "not_loaded", "model": "resnet-18"},
            "clip": {"status": "not_loaded", "model": "clip-vit-base-patch32"}
        },
        "pipelines_active": len(manager.pipelines)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
