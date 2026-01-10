"""
SafeGuard AI Backend - Main FastAPI Application
AI-Native Video Anomaly Detection System - MVP

@spec docs/specs/001-backend-foundation.md
@plan docs/plans/001-backend-foundation-plan.md
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv
import cv2
import numpy as np
import asyncio
from app.models.yolo_detector import get_detector

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
    allow_origins=["*"],  # Allow all for MVP (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detector (lazy loaded)
detector = None


def get_or_create_detector():
    """Get or create YOLOv8 detector instance"""
    global detector
    if detector is None:
        print("Initializing YOLOv8 detector...")
        detector = get_detector()
    return detector


# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.frame_counts: dict[str, int] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.frame_counts[user_id] = 0
        print(f"✅ User {user_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.frame_counts:
            del self.frame_counts[user_id]
        print(f"❌ User {user_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_detection(self, user_id: str, detections: list):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json({
                    "detections": detections
                })
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
        "detector_loaded": detector is not None,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SafeGuard AI Backend API",
        "docs": "/api/docs",
        "health": "/health",
        "websocket": "ws://localhost:8000/ws/detect/{user_id}"
    }


# WebSocket endpoint for video stream detection
@app.websocket("/ws/detect/{user_id}")
async def websocket_detect_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time video detection

    Receives video frames from frontend, processes them through
    YOLOv8, and sends back detection results.
    """
    await manager.connect(user_id, websocket)

    # Get detector (will auto-download model on first use)
    det = get_or_create_detector()

    try:
        while True:
            # Receive frame as bytes
            data = await websocket.receive_bytes()

            # Decode image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                print(f"Failed to decode frame from {user_id}")
                continue

            # Update frame count
            manager.frame_counts[user_id] = manager.frame_counts.get(user_id, 0) + 1

            # Run detection (every frame for MVP)
            detections = det.detect(frame, confidence=0.4)

            # Only send if we have detections
            if len(detections) > 0:
                print(f"🎯 Detected {len(detections)} objects for {user_id}")
                await manager.send_detection(user_id, detections)

            # Log progress every 30 frames
            if manager.frame_counts[user_id] % 30 == 0:
                print(f"📊 Processed {manager.frame_counts[user_id]} frames for {user_id}")

    except WebSocketDisconnect:
        print(f"WebSocket disconnected normally for {user_id}")
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ Error in WebSocket for {user_id}: {e}")
        manager.disconnect(user_id)


# Models info endpoint
@app.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    global detector

    return {
        "models": {
            "yolo": {
                "status": "loaded" if detector is not None else "not_loaded",
                "version": "yolov8n",
                "type": "object_detection"
            }
        },
        "active_connections": len(manager.active_connections),
        "total_frames_processed": sum(manager.frame_counts.values())
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 50)
    print("🚀 SafeGuard AI Backend Starting...")
    print("=" * 50)
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/detect/{user_id}")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("=" * 50)
    print("⚠️  YOLOv8 will download on first detection (~6MB)")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
