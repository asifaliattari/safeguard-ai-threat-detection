"""
SafeGuard AI - Enhanced Backend
Complete Humanitarian Threat Detection System

Features:
- OpenCV + YOLOv8 detection
- Activity recognition
- Multi-channel alerts (Email, SMS, Call)
- AI chatbot analysis
- Real-time monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import asyncio
import json
from typing import Dict, List
from datetime import datetime
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import time

# Load environment variables
load_dotenv()

# Import our enhanced modules
from app.models.enhanced_detector import get_enhanced_detector
from app.services.alert_system import get_alert_system
from app.services.ai_analyst import get_ai_analyst

# Initialize FastAPI
app = FastAPI(
    title="SafeGuard AI - Humanitarian Threat Detection",
    description="Real-time threat detection for public safety",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ User {user_id} connected. Total: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"❌ User {user_id} disconnected. Total: {len(self.active_connections)}")

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")

manager = ConnectionManager()

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=4)

# User preferences storage (in production, use database)
user_preferences = {}

# Frame processing tracker (prevents frame buildup)
processing_frames = {}


# API Models
class UserPreferences(BaseModel):
    email: str = ""
    phone: str = ""
    whatsapp: str = ""
    enable_email: bool = True
    enable_sms: bool = False
    enable_call: bool = False
    auto_call_emergency: bool = False


class ChatMessage(BaseModel):
    user_id: str
    message: str


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SafeGuard AI Enhanced",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/preferences/{user_id}")
async def set_preferences(user_id: str, prefs: UserPreferences):
    """Set user alert preferences"""
    user_preferences[user_id] = prefs.dict()
    return {"status": "success", "message": "Preferences updated"}


@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user alert preferences"""
    return user_preferences.get(user_id, {
        "email": "",
        "enable_email": True,
        "enable_sms": False,
        "enable_call": False,
        "auto_call_emergency": False
    })


@app.post("/api/chat")
async def chat_with_ai(message: ChatMessage):
    """Chat with AI analyst"""
    analyst = get_ai_analyst()
    response = await analyst.analyze(message.message)

    return {
        "user_message": message.message,
        "ai_response": response,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/threat-assessment")
async def get_threat_assessment():
    """Get quick threat assessment"""
    analyst = get_ai_analyst()
    assessment = analyst.quick_threat_assessment()
    return assessment


# =============================================================================
# WEBSOCKET - REAL-TIME DETECTION
# =============================================================================

@app.websocket("/ws/detect/{user_id}")
async def detection_websocket(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time threat detection

    Flow:
    1. Client connects
    2. Client sends base64 encoded frames
    3. Server processes with YOLOv8 + Activity Recognition
    4. Server sends back:
       - All objects detected
       - Dangerous items
       - Unhappy activities
       - Annotated frame
    5. Server triggers alerts if needed
    """
    await manager.connect(user_id, websocket)
    print(f"✅ WebSocket connected for user: {user_id}")

    # Get services
    detector = get_enhanced_detector()
    alert_system = get_alert_system()
    ai_analyst = get_ai_analyst()
    print(f"✅ Services loaded for user: {user_id}")

    # Get user preferences
    prefs = user_preferences.get(user_id, {})

    # Initialize frame tracking for this user
    processing_frames[user_id] = {'processing': False, 'last_time': 0}

    print(f"🚀 Starting detection for user: {user_id}")

    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get('type') == 'frame':
                # FRAME RATE LIMITING: Skip if already processing or too soon
                current_time = time.time()
                if processing_frames[user_id]['processing']:
                    continue  # Skip this frame, still processing previous

                if current_time - processing_frames[user_id]['last_time'] < 0.1:  # Max 10 FPS
                    continue

                processing_frames[user_id]['last_time'] = current_time
                processing_frames[user_id]['processing'] = True

                try:
                    # Decode base64 frame
                    frame_data = message['frame'].split(',')[1] if ',' in message['frame'] else message['frame']
                    frame_bytes = base64.b64decode(frame_data)
                    nparr = np.frombuffer(frame_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is None:
                        processing_frames[user_id]['processing'] = False
                        continue

                    # DETECT THREATS (run in thread pool to avoid blocking)
                    loop = asyncio.get_event_loop()
                    results = await loop.run_in_executor(
                        executor,
                        detector.detect_frame,
                        frame,
                        0.4  # Lower confidence for better detection
                    )

                    # Add to AI analyst's knowledge
                    ai_analyst.add_detection(results)

                    # Encode annotated frame (also CPU intensive, run in thread pool)
                    def encode_frame(frame_with_boxes):
                        _, buffer = cv2.imencode('.jpg', frame_with_boxes)
                        return base64.b64encode(buffer).decode('utf-8')

                    annotated_frame_b64 = await loop.run_in_executor(
                        executor,
                        encode_frame,
                        results['frame_with_boxes']
                    )

                    # Determine audio alert configuration
                    audio_alert = None
                    if results['dangerous_items']:
                        # Critical threats: weapons, fire, etc.
                        critical_item = results['dangerous_items'][0]
                        audio_alert = {
                            'enabled': True,
                            'severity': 'critical',
                            'pattern': 'triple',
                            'frequency': 2500,
                            'duration': 200,
                            'threat_type': critical_item['type']
                        }
                    elif results['unhappy_activities']:
                        # Activity-based alerts
                        activity = results['unhappy_activities'][0]
                        activity_type = activity['type'].lower()

                        if 'unconscious' in activity_type:
                            audio_alert = {'enabled': True, 'severity': 'critical', 'pattern': 'triple', 'frequency': 2500, 'duration': 200, 'threat_type': 'unconscious'}
                        elif 'drowning' in activity_type:
                            audio_alert = {'enabled': True, 'severity': 'critical', 'pattern': 'triple', 'frequency': 2500, 'duration': 200, 'threat_type': 'drowning'}
                        elif 'falling' in activity_type:
                            audio_alert = {'enabled': True, 'severity': 'high', 'pattern': 'single', 'frequency': 2000, 'duration': 800, 'threat_type': 'falling'}
                        elif 'sleeping' in activity_type:
                            audio_alert = {'enabled': True, 'severity': 'medium', 'pattern': 'single', 'frequency': 1500, 'duration': 500, 'threat_type': 'sleeping'}
                        elif 'eyes' in activity_type or 'closed' in activity_type:
                            audio_alert = {'enabled': True, 'severity': 'high', 'pattern': 'continuous', 'frequency': 3000, 'duration': 800, 'threat_type': 'eyes_closed'}

                    # Prepare response
                    response = {
                        'type': 'detection_result',
                        'timestamp': results['timestamp'],
                        'all_objects': results['all_objects'],
                        'dangerous_items': results['dangerous_items'],
                        'unhappy_activities': results['unhappy_activities'],
                        'annotated_frame': f"data:image/jpeg;base64,{annotated_frame_b64}",
                        'audio_alert': audio_alert
                    }

                    # Send to client
                    await manager.send_message(user_id, response)

                    # CHECK FOR ALERTS (run in background, don't block)
                    async def send_alerts_background():
                        alerts_sent = []

                        # Alert for dangerous items
                        for item in results['dangerous_items']:
                            if item['severity'] in ['critical', 'high']:
                                threat_data = {
                                    'type': 'dangerous_item',
                                    'severity': item['severity'],
                                    'description': f"{item['type']} detected (confidence: {item['confidence']:.0%})",
                                    'timestamp': datetime.now().isoformat(),
                                    'location': f"Camera - User {user_id}"
                                }

                                # Send alerts
                                try:
                                    alert_result = await alert_system.send_threat_alert(threat_data, prefs)
                                    alerts_sent.append({
                                        'threat': item['type'],
                                        'alerts': alert_result
                                    })
                                except Exception as e:
                                    print(f"Alert error: {e}")

                        # Alert for unhappy activities
                        for activity in results['unhappy_activities']:
                            if activity['severity'] in ['critical', 'high']:
                                threat_data = {
                                    'type': 'unhappy_activity',
                                    'severity': activity['severity'],
                                    'description': activity['description'],
                                    'timestamp': datetime.now().isoformat(),
                                    'location': f"Camera - User {user_id}"
                                }

                                # Send alerts
                                try:
                                    alert_result = await alert_system.send_threat_alert(threat_data, prefs)
                                    alerts_sent.append({
                                        'threat': activity['type'],
                                        'alerts': alert_result
                                    })
                                except Exception as e:
                                    print(f"Alert error: {e}")

                        # Send alert confirmation to client
                        if alerts_sent:
                            await manager.send_message(user_id, {
                                'type': 'alerts_sent',
                                'alerts': alerts_sent
                            })

                    # Fire and forget - don't wait for alerts
                    asyncio.create_task(send_alerts_background())

                finally:
                    # Always reset processing flag
                    processing_frames[user_id]['processing'] = False

            elif message.get('type') == 'chat':
                # Handle chat message
                query = message.get('message', 'Give me analysis')
                analysis = await ai_analyst.analyze(query)

                await manager.send_message(user_id, {
                    'type': 'chat_response',
                    'message': analysis
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        if user_id in processing_frames:
            del processing_frames[user_id]
        print(f"❌ User {user_id} disconnected")

    except Exception as e:
        print(f"❌ ERROR in WebSocket for {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        manager.disconnect(user_id)
        if user_id in processing_frames:
            del processing_frames[user_id]


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("\n" + "="*60)
    print("🚀 SafeGuard AI - Humanitarian Threat Detection System")
    print("="*60)
    print("\n📡 Initializing services...\n")

    # Initialize detector (will download YOLOv8 if needed)
    detector = get_enhanced_detector()

    # Initialize alert system
    alert_system = get_alert_system()

    # Initialize AI analyst
    ai_analyst = get_ai_analyst()

    print("\n" + "="*60)
    print("✅ All services ready!")
    print("="*60)
    print("\n📚 API Docs: http://localhost:8000/api/docs")
    print("📡 WebSocket: ws://localhost:8000/ws/detect/{user_id}")
    print("❤️  Health: http://localhost:8000/health")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
