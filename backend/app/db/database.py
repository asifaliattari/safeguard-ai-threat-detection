"""
Database helper functions
Using Prisma Client from frontend (via HTTP API)
For MVP, we'll use simple HTTP calls to Next.js API routes
"""

import aiohttp
from typing import Optional, Dict, List
import os
from datetime import datetime


class DatabaseClient:
    """Simple database client that calls Next.js API routes"""

    def __init__(self, frontend_url: str = None):
        self.frontend_url = frontend_url or os.getenv("FRONTEND_URL", "http://localhost:3000")

    async def save_detection(
        self,
        user_id: str,
        detection_type: str,
        confidence: float,
        bbox: List[float],
        severity: str = "low",
        llm_diagnosis: Optional[str] = None,
        camera_id: Optional[str] = None
    ) -> Dict:
        """Save detection event to database"""

        data = {
            "userId": user_id,
            "detectionType": detection_type,
            "confidence": confidence,
            "boundingBox": bbox,
            "severity": severity,
            "llmDiagnosis": llm_diagnosis,
            "cameraId": camera_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.frontend_url}/api/detections/create",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to save detection: {response.status}")
                        return None
        except Exception as e:
            print(f"Error saving detection: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.frontend_url}/api/users/{user_id}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None


# Global instance
_db_client = None


def get_db_client() -> DatabaseClient:
    """Get or create database client"""
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client
