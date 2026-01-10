"""
Claude LLM Diagnosis
Intelligent analysis of detections for threat assessment
"""

from anthropic import Anthropic
import os
import json
import base64
import cv2
import numpy as np
from typing import Dict, Optional


class ClaudeDiagnoser:
    """Claude-powered intelligent detection diagnosis"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            print("⚠️  WARNING: ANTHROPIC_API_KEY not set. LLM diagnosis disabled.")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)
            print("✅ Claude LLM initialized for diagnosis")

    async def diagnose(
        self,
        detection: Dict,
        frame: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Diagnose a detection using Claude

        Args:
            detection: Detection dict with type, confidence, bbox
            frame: Optional video frame for visual analysis

        Returns:
            {
                "is_genuine": true/false,
                "severity": "low|medium|high|critical",
                "message": "Brief description",
                "should_alert": true/false,
                "reasoning": "Why this assessment"
            }
        """

        if not self.client:
            # Fallback to rule-based if no API key
            return self._fallback_diagnosis(detection)

        try:
            # Prepare prompt
            detection_info = f"""Detection Information:
Type: {detection['type']}
Confidence: {detection['confidence']:.2f} ({detection['confidence']*100:.0f}%)
Timestamp: {detection.get('timestamp', 'N/A')}
"""

            # Build message content
            content = []

            # Add image if available
            if frame is not None:
                try:
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    image_b64 = base64.b64encode(buffer).decode('utf-8')

                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64
                        }
                    })
                except Exception as e:
                    print(f"Failed to encode image: {e}")

            # Add text prompt
            prompt = f"""{detection_info}

Analyze this security detection and provide assessment:

1. Is this a genuine safety concern or likely false positive?
2. What is the severity level? (low/medium/high/critical)
3. Should we send an immediate alert?
4. Provide a brief, clear description for notification

Respond in JSON format:
{{
  "is_genuine": true/false,
  "severity": "low|medium|high|critical",
  "message": "Brief alert message (1-2 sentences)",
  "should_alert": true/false,
  "reasoning": "Why you made this assessment"
}}"""

            content.append({
                "type": "text",
                "text": prompt
            })

            # Call Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.3,  # Lower temperature for consistent assessment
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON (may be wrapped in markdown)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            diagnosis = json.loads(response_text)

            print(f"🤖 Claude diagnosis: {diagnosis['severity']} - {diagnosis['message']}")

            return diagnosis

        except Exception as e:
            print(f"❌ Claude diagnosis error: {e}")
            return self._fallback_diagnosis(detection)

    def _fallback_diagnosis(self, detection: Dict) -> Dict:
        """Rule-based fallback when Claude is unavailable"""

        dangerous_objects = ['knife', 'scissors', 'gun', 'rifle', 'weapon']
        obj_type = detection['type'].lower()

        is_dangerous = any(danger in obj_type for danger in dangerous_objects)
        confidence = detection['confidence']

        if is_dangerous:
            severity = "critical" if confidence > 0.7 else "high"
            message = f"Dangerous object detected: {detection['type']}. Immediate attention required."
            should_alert = True
        elif obj_type == 'person' and confidence > 0.8:
            severity = "medium"
            message = f"Person detected with high confidence."
            should_alert = False
        else:
            severity = "low"
            message = f"{detection['type'].title()} detected."
            should_alert = False

        return {
            "is_genuine": True,
            "severity": severity,
            "message": message,
            "should_alert": should_alert,
            "reasoning": "Rule-based assessment (LLM unavailable)"
        }


# Global instance
_diagnoser = None


def get_diagnoser() -> ClaudeDiagnoser:
    """Get or create global diagnoser instance"""
    global _diagnoser
    if _diagnoser is None:
        _diagnoser = ClaudeDiagnoser()
    return _diagnoser
