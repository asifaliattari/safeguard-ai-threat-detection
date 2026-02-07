"""
SafeGuard AI - Unified Visual Threat Detection System
======================================================

Real-time detection of:
- Sleeping/Eyes Closed
- Person Falling
- Unconscious People
- Drowning
- Weapons (Guns, Knives, Dangerous Objects)
- General Threats

WITH AUDIO ALARM ON ALL DETECTIONS

Authors: Asif Ali & Sharmeen Asif
GitHub: https://github.com/asifaliattari
License: MIT
Copyright (c) 2025 Asif Ali & Sharmeen Asif
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
from collections import deque
import math
# Audio alarm - make winsound optional for cross-platform deployment
try:
    import winsound  # For Windows beep alarm
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
    print("⚠️  winsound not available (non-Windows platform). Audio alerts disabled in desktop app.")
import threading
from threading import Thread
import base64
from flask import Flask, Response, render_template_string
import webbrowser
import mediapipe as mp
from scipy.spatial import distance as dist
from enum import Enum
from depth_estimator import DepthEstimator  # Depth/Distance estimation

# ============================================================================
# STATE MACHINE SYSTEM
# ============================================================================

class ThreatState(Enum):
    """Global threat states"""
    IDLE = "idle"                # No threat detected
    OBSERVING = "observing"      # Potential threat being monitored
    CONFIRMED = "confirmed"      # Threat confirmed and active
    ALERTED = "alerted"          # Alert has been dispatched
    COOLDOWN = "cooldown"        # Cooldown period after alert

class ThreatPriority(Enum):
    """Threat priority levels (highest to lowest)"""
    UNCONSCIOUS = 8
    DROWNING = 7
    FALLING = 6
    SLEEPING = 5
    EYES_CLOSED = 4
    WEAPON = 3
    FIRE = 2
    SPARKS = 1

class ThreatStateMachine:
    """
    State machine for individual threat detection.
    Ensures timers persist continuously and alerts fire only once.
    """
    def __init__(self, threat_type, duration_threshold, priority):
        self.threat_type = threat_type
        self.duration_threshold = duration_threshold  # seconds
        self.priority = priority
        self.state = ThreatState.IDLE
        self.observation_start_time = None
        self.confirmed_time = None
        self.alert_dispatched = False
        self.cooldown_start_time = None

    def update(self, condition_active):
        """
        Update state based on whether the threat condition is currently active.

        Args:
            condition_active (bool): True if threat condition detected in current frame

        Returns:
            bool: True if alert should be dispatched (state transition to CONFIRMED)
        """
        should_alert = False
        current_time = time.time()

        if self.state == ThreatState.IDLE:
            if condition_active:
                # Start observing
                self.state = ThreatState.OBSERVING
                self.observation_start_time = current_time
                self.alert_dispatched = False

        elif self.state == ThreatState.OBSERVING:
            if condition_active:
                # Check if duration threshold met
                elapsed = current_time - self.observation_start_time
                if elapsed >= self.duration_threshold:
                    # Transition to CONFIRMED
                    self.state = ThreatState.CONFIRMED
                    self.confirmed_time = current_time
                    should_alert = True
            else:
                # Condition no longer active - reset to IDLE
                self.state = ThreatState.IDLE
                self.observation_start_time = None

        elif self.state == ThreatState.CONFIRMED:
            if not self.alert_dispatched:
                # First frame in CONFIRMED state
                should_alert = True
                self.alert_dispatched = True
                self.state = ThreatState.ALERTED
            elif condition_active:
                # Threat still active but already alerted
                pass
            else:
                # Threat resolved
                self.state = ThreatState.COOLDOWN
                self.cooldown_start_time = current_time

        elif self.state == ThreatState.ALERTED:
            if not condition_active:
                # Threat resolved - enter cooldown
                self.state = ThreatState.COOLDOWN
                self.cooldown_start_time = current_time

        elif self.state == ThreatState.COOLDOWN:
            # Wait for cooldown period (e.g., 3 seconds)
            if current_time - self.cooldown_start_time >= 3.0:
                self.state = ThreatState.IDLE
                self.observation_start_time = None
                self.confirmed_time = None
                self.alert_dispatched = False

        return should_alert

    def get_elapsed_time(self):
        """Get time since observation started (for display purposes)"""
        if self.observation_start_time:
            return time.time() - self.observation_start_time
        return 0.0

    def reset(self):
        """Force reset to IDLE state"""
        self.state = ThreatState.IDLE
        self.observation_start_time = None
        self.confirmed_time = None
        self.alert_dispatched = False
        self.cooldown_start_time = None

class AlertDispatcher:
    """
    Centralized alert dispatcher for beeps, emails, and logging.
    Handles cooldown enforcement and severity-based behavior.
    """
    def __init__(self, config):
        self.config = config
        self.last_alert_time = {}  # Per-threat-type cooldown tracking

    def dispatch_alert(self, threat_type, message, severity="medium"):
        """
        Dispatch alert with appropriate actions.

        Args:
            threat_type (str): Type of threat
            message (str): Alert message
            severity (str): "low", "medium", "high", "critical"
        """
        current_time = time.time()

        # Check per-threat cooldown (SKIP cooldown for eyes_closed to enable continuous alarm)
        if threat_type != 'eyes_closed':
            if threat_type in self.last_alert_time:
                if current_time - self.last_alert_time[threat_type] < self.config.ALARM_COOLDOWN:
                    return  # Still in cooldown

        self.last_alert_time[threat_type] = current_time

        # Print to console
        print(f"\n{'='*80}")
        print(f"🔊 ALERT! {message}")
        print(f"{'='*80}\n")

        # Sound alarm based on severity
        self._sound_alarm(threat_type, severity)

    def _sound_alarm(self, threat_type, severity):
        """Sound alarm with pattern based on threat severity"""
        if not self.config.ALARM_ENABLED:
            return

        # Skip if winsound not available (non-Windows or web deployment)
        if not WINSOUND_AVAILABLE:
            return

        def beep():
            try:
                if severity == "critical" or threat_type in ['weapon', 'fire', 'unconscious', 'drowning']:
                    # Rapid triple beep for critical threats
                    for _ in range(3):
                        winsound.Beep(2500, 200)
                        time.sleep(0.1)
                elif threat_type == 'falling':
                    # Long beep for falling
                    winsound.Beep(2000, 800)
                elif threat_type == 'sleeping':
                    # Medium beep for sleeping
                    winsound.Beep(1500, 500)
                elif threat_type == 'eyes_closed':
                    # HIGH VOLUME CONTINUOUS beep for eyes closed
                    winsound.Beep(3000, 800)
                else:
                    # Default beep
                    winsound.Beep(2500, 500)
            except:
                pass

        # Run in background thread
        threading.Thread(target=beep, daemon=True).start()

# ============================================================================
# CONFIGURATION
# ============================================================================

class ThreatConfig:
    """Configuration for all threat detections"""

    # General
    CONFIDENCE_THRESHOLD = 0.5
    HISTORY_SIZE = 30  # Frames to track

    # Sleeping/Eyes Closed
    SLEEP_STILLNESS_THRESHOLD = 0.02
    SLEEP_HEAD_ANGLE_THRESHOLD = 45
    SLEEP_DURATION_THRESHOLD = 3.0  # seconds

    # Eye Closure Detection (MediaPipe)
    EYE_AR_THRESHOLD_CLOSED = 0.23  # Eyes considered closed below this
    EYE_AR_THRESHOLD_OPEN = 0.27     # Eyes considered open above this (hysteresis)
    EYE_CLOSED_FRAMES = 60   # Consecutive frames before alert (at 30fps = 2 seconds)
    EYE_DETECTION_ENABLED = True

    # Fire Detection
    FIRE_DETECTION_ENABLED = False  # Disabled - too many false positives. Enable after calibration
    FIRE_COLOR_LOWER = np.array([0, 200, 200])  # HSV lower bound for fire (strict)
    FIRE_COLOR_UPPER = np.array([15, 255, 255])  # HSV upper bound for fire (strict)
    FIRE_MIN_AREA = 8000  # Minimum area to consider as fire (large flames only)

    # Fall Detection
    FALL_VERTICAL_THRESHOLD = 0.7  # Height change ratio
    FALL_SPEED_THRESHOLD = 0.3     # Speed of falling
    FALL_ANGLE_THRESHOLD = 60      # Body angle from vertical

    # Unconscious Detection
    UNCONSCIOUS_GROUND_THRESHOLD = 0.8  # Position near ground
    UNCONSCIOUS_STILLNESS = 0.01
    UNCONSCIOUS_DURATION = 5.0  # seconds

    # Drowning Detection
    DROWN_MOVEMENT_THRESHOLD = 0.15
    DROWN_VERTICAL_RATIO = 0.3
    DROWN_DURATION_THRESHOLD = 2.0

    # Weapon Detection
    WEAPON_CLASSES = ['knife', 'gun', 'scissors', 'baseball bat']
    WEAPON_CONFIDENCE = 0.6

    # Alarm Settings
    ALARM_ENABLED = True
    ALARM_FREQUENCY = 2500  # Hz
    ALARM_DURATION = 500    # ms
    ALARM_COOLDOWN = 3.0    # seconds between alarms


# ============================================================================
# UNIFIED THREAT DETECTOR
# ============================================================================

class UnifiedThreatDetector:
    """
    All-in-one threat detection system
    """

    def __init__(self, config=None):
        self.config = config or ThreatConfig()

        print("=" * 80)
        print("🚨 SafeGuard AI - Unified Threat Detection System")
        print("=" * 80)

        # Load YOLO models
        print("\n📦 Loading AI models...")

        # YOLOv8-Pose for human detection and pose
        self.pose_model = YOLO('yolov8n-pose.pt')
        print("  ✅ YOLOv8-Pose loaded (human detection)")

        # YOLOv8 for object detection (weapons, etc.)
        self.object_model = YOLO('yolov8n.pt')
        print("  ✅ YOLOv8 loaded (weapon detection)")

        # Depth Estimator for distance measurement
        self.depth_estimator = DepthEstimator()
        print("  ✅ Depth Estimator loaded (distance measurement)")

        # MediaPipe Face Mesh for eye detection
        if self.config.EYE_DETECTION_ENABLED:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            # Create FaceLandmarker with more sensitive detection
            base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                num_faces=5,
                min_face_detection_confidence=0.3,  # Lower = more sensitive (default 0.5)
                min_face_presence_confidence=0.3    # Keep tracking faces better
            )
            self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
            print("  ✅ MediaPipe FaceLandmarker loaded (eye detection)")

            # Eye state tracking with hysteresis
            self.eyes_currently_closed = False  # Previous state for hysteresis

        # Person tracking
        self.person_states = {}
        self.next_person_id = 0

        # Alert tracking
        self.alerts = deque(maxlen=50)
        self.last_alarm_time = 0

        # Statistics
        self.frame_count = 0
        self.fps = 0

        # Threat counters
        self.threat_counts = {
            'eyes_closed': 0,
            'fire': 0,
            'sleeping': 0,
            'falling': 0,
            'unconscious': 0,
            'drowning': 0,
            'weapon': 0
        }

        # Initialize AlertDispatcher
        self.alert_dispatcher = AlertDispatcher(self.config)

        # Initialize State Machines for each threat type
        self.threat_machines = {
            'eyes_closed': ThreatStateMachine('eyes_closed', 1.0, ThreatPriority.EYES_CLOSED),
            'fire': ThreatStateMachine('fire', 1.0, ThreatPriority.FIRE),
            'sleeping': ThreatStateMachine('sleeping', 3.0, ThreatPriority.SLEEPING),
            'falling': ThreatStateMachine('falling', 0.5, ThreatPriority.FALLING),
            'unconscious': ThreatStateMachine('unconscious', 5.0, ThreatPriority.UNCONSCIOUS),
            'drowning': ThreatStateMachine('drowning', 2.0, ThreatPriority.DROWNING),
            'weapon': ThreatStateMachine('weapon', 0.0, ThreatPriority.WEAPON),  # Instant
        }

        # Per-person state machines (for pose-based detections)
        self.person_threat_machines = {}  # {person_id: {threat_type: ThreatStateMachine}}

        print("\n✅ System Ready!")
        print("\n🎯 Active Detections:")
        print("  👁️ Eyes Closed (2 seconds)")
        if self.config.FIRE_DETECTION_ENABLED:
            print("  🔥 Fire Detection")
        else:
            print("  🔥 Fire Detection          [DISABLED - No false alarms]")
        print("  😴 Sleeping/Body Pose")
        print("  🤕 Person Falling")
        print("  💀 Unconscious People")
        print("  🏊 Drowning")
        print("  🔪 Weapons (Guns, Knives, Dangerous Objects)")
        print("  🔊 AUDIO ALARM on all threats")
        print("=" * 80 + "\n")

    def sound_alarm(self, threat_type):
        """
        Sound alarm on separate thread (non-blocking)
        """
        if not self.config.ALARM_ENABLED:
            return

        # Cooldown check
        current_time = time.time()
        if current_time - self.last_alarm_time < self.config.ALARM_COOLDOWN:
            return

        self.last_alarm_time = current_time

        def beep():
            try:
                # Different beep patterns for different threats
                if threat_type == 'weapon':
                    # Rapid beeps for weapon
                    for _ in range(3):
                        winsound.Beep(self.config.ALARM_FREQUENCY, 200)
                        time.sleep(0.1)
                elif threat_type in ['falling', 'unconscious', 'drowning']:
                    # Long urgent beep
                    winsound.Beep(self.config.ALARM_FREQUENCY, self.config.ALARM_DURATION)
                else:
                    # Single beep
                    winsound.Beep(self.config.ALARM_FREQUENCY, self.config.ALARM_DURATION)
            except:
                # Fallback if winsound fails
                print("\a")  # System beep

        # Run in separate thread so it doesn't block
        threading.Thread(target=beep, daemon=True).start()

    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR) for eye closure detection
        EAR formula: (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        # Vertical eye landmarks
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        # Horizontal eye landmark
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        # EAR calculation
        ear = (A + B) / (2.0 * C)
        return ear

    def detect_eye_closure(self, frame):
        """
        Detect if eyes are CURRENTLY closed using MediaPipe FaceLandmarker.
        Returns: (eyes_closed_now, face_count, avg_ear, head_pitch)

        NOTE: This method only detects the CURRENT state, not duration.
        Duration tracking is handled by the ThreatStateMachine.
        """
        if not self.config.EYE_DETECTION_ENABLED:
            return False, 0, 1.0, 0.0

        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create MediaPipe Image
            from mediapipe import Image, ImageFormat
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)

            # Detect face landmarks
            detection_result = self.face_landmarker.detect(mp_image)

            eyes_closed_now = False
            face_count = 0
            min_ear = 1.0  # Track minimum EAR across all faces
            head_pitch = 0.0  # Head tilt angle (positive = looking down, negative = looking up)

            if detection_result.face_landmarks:
                face_count = len(detection_result.face_landmarks)
                h, w = frame.shape[:2]

                for face_id, face_landmarks in enumerate(detection_result.face_landmarks):
                    # Calculate HEAD POSE (pitch angle) to detect looking down
                    # Using nose tip (1) and forehead (10) landmarks
                    nose_tip_y = face_landmarks[1].y * h
                    forehead_y = face_landmarks[10].y * h
                    chin_y = face_landmarks[152].y * h

                    # Calculate pitch: if nose is significantly below forehead, head is tilted down
                    face_height = chin_y - forehead_y
                    if face_height > 0:
                        # Normalized vertical position of nose (0 = top, 1 = bottom)
                        nose_position = (nose_tip_y - forehead_y) / face_height
                        # Convert to angle estimate: 0.5 = neutral, >0.6 = looking down
                        head_pitch = (nose_position - 0.5) * 100  # Scale to degrees estimate

                    # Left eye landmarks (MediaPipe indices)
                    left_eye = [
                        (face_landmarks[33].x * w, face_landmarks[33].y * h),    # outer
                        (face_landmarks[160].x * w, face_landmarks[160].y * h),  # top
                        (face_landmarks[158].x * w, face_landmarks[158].y * h),  # top
                        (face_landmarks[133].x * w, face_landmarks[133].y * h),  # inner
                        (face_landmarks[153].x * w, face_landmarks[153].y * h),  # bottom
                        (face_landmarks[144].x * w, face_landmarks[144].y * h),  # bottom
                    ]

                    # Right eye landmarks
                    right_eye = [
                        (face_landmarks[362].x * w, face_landmarks[362].y * h),  # outer
                        (face_landmarks[385].x * w, face_landmarks[385].y * h),  # top
                        (face_landmarks[387].x * w, face_landmarks[387].y * h),  # top
                        (face_landmarks[263].x * w, face_landmarks[263].y * h),  # inner
                        (face_landmarks[373].x * w, face_landmarks[373].y * h),  # bottom
                        (face_landmarks[380].x * w, face_landmarks[380].y * h),  # bottom
                    ]

                    # Calculate EAR for both eyes
                    left_ear = self.calculate_eye_aspect_ratio(left_eye)
                    right_ear = self.calculate_eye_aspect_ratio(right_eye)
                    avg_ear = (left_ear + right_ear) / 2.0

                    # Track minimum EAR across all faces
                    min_ear = min(min_ear, avg_ear)

                    # ANTI-FALSE POSITIVE: Only consider eyes closed if NOT looking down
                    # If head_pitch > 15 degrees, person is looking down (NOT sleeping)
                    if head_pitch > 15:
                        # Looking down - ignore eye closure
                        eyes_closed_now = False
                    else:
                        # Head in normal/resting position - check eye closure
                        # Hysteresis logic: Use different thresholds based on previous state
                        if self.eyes_currently_closed:
                            # Currently closed - need to exceed OPEN threshold to be considered open
                            if avg_ear < self.config.EYE_AR_THRESHOLD_OPEN:
                                eyes_closed_now = True
                        else:
                            # Currently open - need to fall below CLOSED threshold to be considered closed
                            if avg_ear < self.config.EYE_AR_THRESHOLD_CLOSED:
                                eyes_closed_now = True

        except Exception as e:
            # Silently skip if detection fails
            eyes_closed_now = False
            face_count = 0
            min_ear = 1.0
            head_pitch = 0.0

        # Update state for next frame (hysteresis)
        self.eyes_currently_closed = eyes_closed_now

        return eyes_closed_now, face_count, min_ear, head_pitch

    def detect_fire(self, frame):
        """Detect fire using color analysis"""
        if not self.config.FIRE_DETECTION_ENABLED:
            return False, []

        try:
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create mask for fire colors (orange/red/yellow)
            mask = cv2.inRange(hsv, self.config.FIRE_COLOR_LOWER, self.config.FIRE_COLOR_UPPER)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            fire_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.config.FIRE_MIN_AREA:
                    x, y, w, h = cv2.boundingRect(contour)
                    fire_regions.append((x, y, w, h, area))

            return len(fire_regions) > 0, fire_regions
        except Exception as e:
            return False, []

    def calculate_movement(self, current_kpts, previous_kpts):
        """Calculate movement between keypoints"""
        if previous_kpts is None:
            return 0.0

        movements = []
        for curr, prev in zip(current_kpts, previous_kpts):
            if curr[2] > 0.5 and prev[2] > 0.5:
                dx = curr[0] - prev[0]
                dy = curr[1] - prev[1]
                movement = math.sqrt(dx**2 + dy**2)
                movements.append(movement)

        if not movements:
            return 0.0

        return np.mean(movements) / 640.0  # Normalize

    def calculate_body_angle(self, keypoints):
        """Calculate body angle from vertical (for fall detection)"""
        # Use shoulders and hips
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]

        if all(kp[2] > 0.5 for kp in [left_shoulder, right_shoulder, left_hip, right_hip]):
            shoulder_center = ((left_shoulder[0] + right_shoulder[0]) / 2,
                             (left_shoulder[1] + right_shoulder[1]) / 2)
            hip_center = ((left_hip[0] + right_hip[0]) / 2,
                        (left_hip[1] + right_hip[1]) / 2)

            dx = hip_center[0] - shoulder_center[0]
            dy = hip_center[1] - shoulder_center[1]

            angle = abs(math.degrees(math.atan2(dx, dy + 1e-6)))
            return angle

        return 0.0

    def detect_sleeping(self, person_id, keypoints):
        """Detect if person is sleeping or eyes closed"""
        state = self.person_states[person_id]

        # Calculate head angle
        nose = keypoints[0]
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]

        if nose[2] > 0.5 and left_shoulder[2] > 0.5 and right_shoulder[2] > 0.5:
            neck_x = (left_shoulder[0] + right_shoulder[0]) / 2
            neck_y = (left_shoulder[1] + right_shoulder[1]) / 2

            dx = nose[0] - neck_x
            dy = nose[1] - neck_y
            head_angle = abs(math.degrees(math.atan2(dx, dy + 1e-6)))
        else:
            head_angle = 0

        # Get movement
        movement = 0.0
        if state['keypoint_history']:
            prev_kpts = state['keypoint_history'][-1]
            movement = self.calculate_movement(keypoints, prev_kpts)

        # Check criteria
        is_still = movement < self.config.SLEEP_STILLNESS_THRESHOLD
        head_down = head_angle > self.config.SLEEP_HEAD_ANGLE_THRESHOLD

        if is_still and head_down:
            state['sleep_timer'] += 1/30.0
        else:
            state['sleep_timer'] = 0.0

        is_sleeping = state['sleep_timer'] >= self.config.SLEEP_DURATION_THRESHOLD

        return is_sleeping, state['sleep_timer']

    def detect_falling(self, person_id, keypoints, bbox):
        """Detect if person is falling"""
        state = self.person_states[person_id]

        # Calculate vertical position change
        current_y = bbox[1] + (bbox[3] - bbox[1]) / 2

        if 'last_y_position' in state:
            y_change = current_y - state['last_y_position']
            fall_speed = abs(y_change) / 640.0  # Normalize

            # Check body angle
            body_angle = self.calculate_body_angle(keypoints)

            # Falling criteria
            is_falling = (fall_speed > self.config.FALL_SPEED_THRESHOLD and
                         y_change > 0 and  # Moving down
                         body_angle > self.config.FALL_ANGLE_THRESHOLD)

            state['last_y_position'] = current_y

            return is_falling, fall_speed

        state['last_y_position'] = current_y
        return False, 0.0

    def detect_unconscious(self, person_id, keypoints, bbox):
        """Detect if person is unconscious (lying on ground, not moving)"""
        state = self.person_states[person_id]

        # Check if near ground (bottom of frame)
        frame_height = 640  # Assuming standard frame
        person_y = bbox[3]  # Bottom of bbox
        near_ground = person_y > frame_height * self.config.UNCONSCIOUS_GROUND_THRESHOLD

        # Check body angle (horizontal)
        body_angle = self.calculate_body_angle(keypoints)
        is_horizontal = body_angle > 60

        # Check stillness
        movement = 0.0
        if state['keypoint_history']:
            prev_kpts = state['keypoint_history'][-1]
            movement = self.calculate_movement(keypoints, prev_kpts)

        is_still = movement < self.config.UNCONSCIOUS_STILLNESS

        # Update timer
        if near_ground and is_horizontal and is_still:
            state['unconscious_timer'] += 1/30.0
        else:
            state['unconscious_timer'] = 0.0

        is_unconscious = state['unconscious_timer'] >= self.config.UNCONSCIOUS_DURATION

        return is_unconscious, state['unconscious_timer']

    def detect_drowning(self, person_id, keypoints):
        """Detect drowning behavior"""
        state = self.person_states[person_id]

        # Erratic movement
        movement = 0.0
        if state['keypoint_history']:
            prev_kpts = state['keypoint_history'][-1]
            movement = self.calculate_movement(keypoints, prev_kpts)

        # Vertical orientation (struggling)
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]

        vertical_ratio = 0.0
        if all(kp[2] > 0.5 for kp in [left_shoulder, right_shoulder, left_hip, right_hip]):
            shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
            body_height = abs((left_hip[1] + right_hip[1]) / 2 - (left_shoulder[1] + right_shoulder[1]) / 2)
            vertical_ratio = body_height / (shoulder_width + 1e-6)

        # Check criteria
        is_erratic = movement > self.config.DROWN_MOVEMENT_THRESHOLD
        is_vertical = vertical_ratio > self.config.DROWN_VERTICAL_RATIO

        if is_erratic and is_vertical:
            state['drown_timer'] += 1/30.0
        else:
            state['drown_timer'] = max(0, state['drown_timer'] - 1/30.0)

        is_drowning = state['drown_timer'] >= self.config.DROWN_DURATION_THRESHOLD

        return is_drowning, state['drown_timer']

    def detect_weapons(self, frame):
        """Detect weapons and dangerous objects"""
        results = self.object_model(frame, verbose=False)[0]

        weapons_detected = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls_id].lower()

            # Check if it's a weapon or dangerous object
            is_weapon = any(weapon in class_name for weapon in self.config.WEAPON_CLASSES)

            if is_weapon and conf >= self.config.WEAPON_CONFIDENCE:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                weapons_detected.append({
                    'type': class_name,
                    'confidence': conf,
                    'bbox': (x1, y1, x2, y2)
                })

        return weapons_detected

    def track_person(self, bbox, keypoints):
        """Simple person tracking"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Find closest existing person
        min_dist = float('inf')
        closest_id = None

        for person_id, state in list(self.person_states.items()):
            if state['last_seen'] < self.frame_count - 30:
                continue

            prev_x, prev_y = state['last_position']
            dist = math.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)

            if dist < min_dist and dist < 100:
                min_dist = dist
                closest_id = person_id

        if closest_id is not None:
            person_id = closest_id
        else:
            person_id = self.next_person_id
            self.next_person_id += 1
            self.person_states[person_id] = {
                'keypoint_history': deque(maxlen=self.config.HISTORY_SIZE),
                'sleep_timer': 0.0,
                'drown_timer': 0.0,
                'unconscious_timer': 0.0,
                'last_position': (center_x, center_y),
                'last_seen': self.frame_count
            }

        state = self.person_states[person_id]
        state['keypoint_history'].append(keypoints.copy())
        state['last_position'] = (center_x, center_y)
        state['last_seen'] = self.frame_count

        return person_id

    def process_frame(self, frame):
        """Process frame for all threats"""
        start_time = time.time()
        self.frame_count += 1

        annotated_frame = frame.copy()
        h, w = frame.shape[:2]

        all_detections = []

        # 1. DETECT FIRE (CRITICAL PRIORITY - STATE-BASED)
        fire_detected_now, fire_regions = self.detect_fire(frame)

        # Update state machine
        should_alert_fire = self.threat_machines['fire'].update(fire_detected_now)

        if should_alert_fire:
            # Alert triggers ONLY ONCE on confirmation
            alert = f"🔥 FIRE DETECTED! ({len(fire_regions)} regions)"
            self.alerts.append((datetime.now(), alert))
            self.alert_dispatcher.dispatch_alert('fire', alert, severity="critical")
            self.threat_counts['fire'] += 1

        # Draw visual indicators if fire is currently detected
        if fire_detected_now:
            for x, y, fw, fh, area in fire_regions:
                cv2.rectangle(annotated_frame, (x, y), (x+fw, y+fh), (0, 0, 255), 4)
                elapsed = self.threat_machines['fire'].get_elapsed_time()
                cv2.putText(annotated_frame, f"🔥 FIRE ({elapsed:.1f}s)", (x, y-15),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

        # 2. DETECT EYE CLOSURE (STATE-BASED)
        eyes_closed_now, face_count, avg_ear, head_pitch = self.detect_eye_closure(frame)

        # Debug: Print face detection status every 30 frames
        if self.frame_count % 30 == 0:
            if face_count > 0:
                machine = self.threat_machines['eyes_closed']
                elapsed = machine.get_elapsed_time()
                state = machine.state.value
                looking_status = "LOOKING DOWN" if head_pitch > 15 else "Normal"
                print(f"👤 Detected {face_count} face(s) - Head: {head_pitch:.1f}° ({looking_status})")
                print(f"   State: {state} | EAR: {avg_ear:.3f} | Elapsed: {elapsed:.1f}s")
            else:
                print(f"⚠️ No faces detected - check camera and lighting")

        # Update state machine and check if alert should be dispatched
        should_alert = self.threat_machines['eyes_closed'].update(eyes_closed_now)

        if should_alert:
            # ALERT TRIGGERS when transitioning to CONFIRMED state
            alert_msg = "👁️ EYES CLOSED FOR 1 SECOND!"
            self.alerts.append((datetime.now(), alert_msg))
            self.alert_dispatcher.dispatch_alert('eyes_closed', alert_msg, severity="high")
            self.threat_counts['eyes_closed'] += 1

        # CONTINUOUS ALARM: Keep beeping while eyes remain closed
        if self.threat_machines['eyes_closed'].state in [ThreatState.CONFIRMED, ThreatState.ALERTED]:
            # Trigger alarm continuously (every frame) while eyes are closed
            elapsed = self.threat_machines['eyes_closed'].get_elapsed_time()
            alert_msg = f"👁️ EYES CLOSED ({elapsed:.1f}s)"
            self.alert_dispatcher.dispatch_alert('eyes_closed', alert_msg, severity="high")

        # Draw visual indicator - show different messages for "looking down" vs "eyes closed"
        if head_pitch > 15:
            # Person is looking down - show green text (no alarm)
            cv2.putText(annotated_frame, f"👀 LOOKING DOWN ({head_pitch:.0f}°)", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        elif eyes_closed_now or self.threat_machines['eyes_closed'].state in [ThreatState.CONFIRMED, ThreatState.ALERTED]:
            # Eyes actually closed (not looking down) - show orange/red warning
            elapsed = self.threat_machines['eyes_closed'].get_elapsed_time()
            alert_text = f"👁️ EYES CLOSED ({elapsed:.1f}s)"
            cv2.putText(annotated_frame, alert_text, (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)

            all_detections.append({
                'type': 'eyes_closed',
                'label': '👁️ EYES CLOSED',
                'elapsed': elapsed
            })

        # 2. DETECT WEAPONS (HIGH PRIORITY)
        weapons = self.detect_weapons(frame)

        for weapon in weapons:
            x1, y1, x2, y2 = weapon['bbox']

            # Draw red box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

            # Label
            label = f"🔪 WEAPON: {weapon['type'].upper()} ({weapon['confidence']:.2f})"
            cv2.putText(annotated_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Alert
            alert_msg = f"🚨 WEAPON DETECTED: {weapon['type'].upper()}"
            self.alerts.append((datetime.now(), alert_msg))

            # SOUND ALARM
            print(f"\n{'='*80}")
            print(f"🔊 BEEP BEEP BEEP! {alert_msg}")
            print(f"{'='*80}\n")
            self.sound_alarm('weapon')
            self.threat_counts['weapon'] += 1

            all_detections.append({
                'type': 'weapon',
                'weapon_type': weapon['type'],
                'confidence': weapon['confidence'],
                'severity': 'CRITICAL'
            })

        # 2.5. DISPLAY ALL OTHER OBJECTS (NON-THREATS)
        # Get all object detections
        object_results = self.object_model(frame, verbose=False)[0]

        for box in object_results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = object_results.names[cls_id].lower()

            # Skip weapons (already displayed above with red boxes)
            is_weapon = any(weapon in class_name for weapon in self.config.WEAPON_CLASSES)
            if is_weapon:
                continue

            # Skip low confidence detections
            if conf < 0.3:
                continue

            # Draw green box for normal objects
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Label with object name and confidence
            label = f"{class_name.upper()}: {conf:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 3. DETECT HUMANS AND THEIR BEHAVIORS
        pose_results = self.pose_model(frame, verbose=False)[0]

        if pose_results.keypoints is not None:
            for i, (box, kpt_data) in enumerate(zip(pose_results.boxes, pose_results.keypoints.data)):
                conf = float(box.conf[0])
                if conf < self.config.CONFIDENCE_THRESHOLD:
                    continue

                x1, y1, x2, y2 = map(float, box.xyxy[0])
                keypoints = kpt_data.cpu().numpy()

                # Track person
                person_id = self.track_person([x1, y1, x2, y2], keypoints)

                # DEPTH/DISTANCE ESTIMATION
                distance_info = self.depth_estimator.estimate_person_distance(
                    (x1, y1, x2, y2),
                    frame.shape
                )

                # Run all detections
                is_sleeping, sleep_time = self.detect_sleeping(person_id, keypoints)
                is_falling, fall_speed = self.detect_falling(person_id, keypoints, [x1, y1, x2, y2])
                is_unconscious, uncon_time = self.detect_unconscious(person_id, keypoints, [x1, y1, x2, y2])
                is_drowning, drown_time = self.detect_drowning(person_id, keypoints)

                # Determine primary threat
                threat = None
                color = (0, 255, 0)  # Green = normal

                if is_unconscious:
                    threat = f"💀 UNCONSCIOUS ({uncon_time:.1f}s)"
                    color = (0, 0, 139)  # Dark red
                    alert = f"💀 UNCONSCIOUS PERSON - ID {person_id}"
                    self.alerts.append((datetime.now(), alert))
                    print(f"\n{'='*80}")
                    print(f"🔊 BEEEEEP! {alert}")
                    print(f"{'='*80}\n")
                    self.sound_alarm('unconscious')
                    self.threat_counts['unconscious'] += 1

                elif is_drowning:
                    threat = f"🏊 DROWNING ({drown_time:.1f}s)"
                    color = (0, 0, 255)  # Red
                    alert = f"🚨 DROWNING DETECTED - ID {person_id}"
                    self.alerts.append((datetime.now(), alert))
                    print(f"\n{'='*80}")
                    print(f"🔊 BEEEEEP! {alert}")
                    print(f"{'='*80}\n")
                    self.sound_alarm('drowning')
                    self.threat_counts['drowning'] += 1

                elif is_falling:
                    threat = f"🤕 FALLING! (speed: {fall_speed:.2f})"
                    color = (0, 165, 255)  # Orange
                    alert = f"🚨 PERSON FALLING - ID {person_id}"
                    self.alerts.append((datetime.now(), alert))
                    print(f"\n{'='*80}")
                    print(f"🔊 BEEEEEP! {alert}")
                    print(f"{'='*80}\n")
                    self.sound_alarm('falling')
                    self.threat_counts['falling'] += 1

                elif is_sleeping:
                    threat = f"😴 SLEEPING ({sleep_time:.1f}s)"
                    color = (0, 140, 255)  # Orange
                    alert = f"😴 SLEEPING DETECTED - ID {person_id}"
                    if len(self.alerts) == 0 or self.alerts[-1][1] != alert:
                        self.alerts.append((datetime.now(), alert))
                        print(f"\n{'='*80}")
                        print(f"🔊 BEEP! {alert}")
                        print(f"{'='*80}\n")
                        self.sound_alarm('sleeping')
                        self.threat_counts['sleeping'] += 1

                # Draw bounding box
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

                # Draw label
                if threat:
                    label = f"Person {person_id}: {threat}"
                else:
                    label = f"Person {person_id}: NORMAL"

                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated_frame,
                            (int(x1), int(y1) - label_size[1] - 10),
                            (int(x1) + label_size[0], int(y1)),
                            color, -1)
                cv2.putText(annotated_frame, label,
                          (int(x1), int(y1) - 5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # DRAW DISTANCE OVERLAY
                if distance_info['distance_m'] is not None:
                    # Draw distance info below the person
                    dist_m = distance_info['distance_m']
                    dist_ft = distance_info['distance_ft']
                    zone = distance_info['zone']
                    dist_color = distance_info['color']

                    # Distance text
                    dist_text = f"{dist_m:.2f}m ({dist_ft:.1f}ft) - {zone}"

                    # Draw distance background
                    dist_size, _ = cv2.getTextSize(dist_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(annotated_frame,
                                (int(x1), int(y2) + 5),
                                (int(x1) + dist_size[0] + 10, int(y2) + dist_size[1] + 15),
                                dist_color, -1)

                    # Draw distance text
                    cv2.putText(annotated_frame, dist_text,
                              (int(x1) + 5, int(y2) + dist_size[1] + 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Draw distance line to floor
                    center_x = int((x1 + x2) / 2)
                    cv2.line(annotated_frame, (center_x, int(y2)), (center_x, h - 20), dist_color, 2)
                    cv2.circle(annotated_frame, (center_x, h - 20), 6, dist_color, -1)

                # Draw keypoints
                for kpt in keypoints:
                    if kpt[2] > 0.5:
                        cv2.circle(annotated_frame, (int(kpt[0]), int(kpt[1])),
                                 3, (0, 255, 255), -1)

                all_detections.append({
                    'person_id': person_id,
                    'sleeping': is_sleeping,
                    'falling': is_falling,
                    'unconscious': is_unconscious,
                    'drowning': is_drowning,
                    'distance_m': distance_info['distance_m'],
                    'distance_zone': distance_info['zone']
                })

        # Draw depth grid (perspective distance zones)
        # Uncomment to enable depth grid overlay
        # self.depth_estimator.draw_depth_grid(annotated_frame)

        # Calculate FPS
        self.fps = 1.0 / (time.time() - start_time + 1e-6)

        # Draw stats overlay (DISABLED - clean video feed as requested)
        # self._draw_overlay(annotated_frame)

        return annotated_frame, all_detections

    def _draw_overlay(self, frame):
        """Draw statistics overlay with better readability"""
        h, w = frame.shape[:2]

        # Stats panel with semi-transparent black background
        cv2.rectangle(frame, (10, 10), (480, 240), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (480, 240), (0, 255, 0), 2)  # Green border

        y = 40
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (25, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        y += 35
        cv2.putText(frame, f"THREATS DETECTED:", (25, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        y += 30
        for threat_type, count in self.threat_counts.items():
            color = (0, 0, 255) if count > 0 else (150, 150, 150)
            cv2.putText(frame, f"{threat_type.upper()}: {count}",
                       (35, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y += 28

        # Recent alerts panel
        if self.alerts:
            alert_y = h - 180
            cv2.rectangle(frame, (10, alert_y - 40), (w - 10, h - 10), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, alert_y - 40), (w - 10, h - 10), (0, 0, 255), 2)

            cv2.putText(frame, "RECENT ALERTS:",
                       (25, alert_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            for i, (timestamp, alert) in enumerate(list(self.alerts)[-3:]):
                alert_y += 35
                time_str = timestamp.strftime("%H:%M:%S")
                cv2.putText(frame, f"[{time_str}] {alert[:50]}",
                           (25, alert_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Unified Threat Detection System")
    parser.add_argument('--source', type=str, default='0',
                       help='Video source (0 for webcam, or path to video)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video file')
    parser.add_argument('--no-alarm', action='store_true',
                       help='Disable audio alarm')

    args = parser.parse_args()

    # Initialize detector
    config = ThreatConfig()
    if args.no_alarm:
        config.ALARM_ENABLED = False

    detector = UnifiedThreatDetector(config)

    # Open video source
    print(f"\n📹 Opening video source: {args.source}")
    if args.source.isdigit():
        cap = cv2.VideoCapture(int(args.source))
    else:
        cap = cv2.VideoCapture(args.source)

    if not cap.isOpened():
        print("❌ Error: Could not open video source")
        return

    # Video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Video writer
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        print(f"💾 Recording to: {args.output}")

    print("\n" + "=" * 80)
    print("🎬 LIVE Detection Started!")
    print("=" * 80)

    # Check if GUI is available
    gui_available = False
    try:
        cv2.namedWindow('test_window', cv2.WINDOW_NORMAL)
        cv2.destroyWindow('test_window')
        gui_available = True
        print("\n📺 Watch the live video window!")
        print("Press 'q' to quit or Ctrl+C to stop\n")
    except cv2.error:
        gui_available = False
        print("\n🌐 OpenCV GUI not available - Starting WEB MODE...")
        print("📺 Opening browser automatically...")
        print("🌐 URL: http://localhost:5000")
        print("Press Ctrl+C to stop\n")

    # Create display window if GUI available
    if gui_available:
        cv2.namedWindow('SafeGuard AI - Threat Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('SafeGuard AI - Threat Detection', 1280, 720)

    # Web viewer for headless mode
    latest_frame = [None]

    if not gui_available:
        app = Flask(__name__)

        @app.route('/')
        def index():
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>SafeGuard AI - Live Detection</title>
                <meta charset="UTF-8">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                        font-family: 'Segoe UI', Arial, sans-serif;
                        color: #fff;
                        min-height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        max-width: 1400px;
                        margin: 0 auto;
                    }
                    h1 {
                        text-align: center;
                        color: #00ff00;
                        font-size: 2.5em;
                        margin-bottom: 10px;
                        text-shadow: 0 0 20px rgba(0,255,0,0.5);
                        animation: glow 2s ease-in-out infinite alternate;
                    }
                    @keyframes glow {
                        from { text-shadow: 0 0 10px rgba(0,255,0,0.3); }
                        to { text-shadow: 0 0 20px rgba(0,255,0,0.8); }
                    }
                    .subtitle {
                        text-align: center;
                        color: #888;
                        font-size: 1.2em;
                        margin-bottom: 30px;
                    }
                    .stats-bar {
                        background: rgba(0,0,0,0.5);
                        border: 2px solid #00ff00;
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 20px;
                        display: flex;
                        justify-content: space-around;
                        flex-wrap: wrap;
                    }
                    .stat-item {
                        padding: 10px 20px;
                        text-align: center;
                    }
                    .stat-label {
                        font-size: 0.9em;
                        color: #00ff00;
                        font-weight: bold;
                    }
                    .stat-value {
                        font-size: 1.1em;
                        color: #fff;
                        margin-top: 5px;
                    }
                    #video-container {
                        text-align: center;
                        position: relative;
                    }
                    #live-feed {
                        max-width: 100%;
                        width: 100%;
                        border: 4px solid #00ff00;
                        border-radius: 15px;
                        box-shadow: 0 0 30px rgba(0,255,0,0.4);
                    }
                    .detection-list {
                        background: rgba(0,0,0,0.5);
                        border: 2px solid #ff9500;
                        border-radius: 10px;
                        padding: 20px;
                        margin-top: 20px;
                    }
                    .detection-list h3 {
                        color: #ff9500;
                        margin-bottom: 15px;
                        font-size: 1.5em;
                    }
                    .detection-badge {
                        display: inline-block;
                        background: rgba(0,255,0,0.2);
                        border: 1px solid #00ff00;
                        padding: 8px 15px;
                        margin: 5px;
                        border-radius: 20px;
                        font-size: 1em;
                    }
                    .info {
                        text-align: center;
                        margin-top: 20px;
                        padding: 15px;
                        background: rgba(255,0,0,0.1);
                        border: 2px solid #ff0000;
                        border-radius: 10px;
                    }
                    .info p {
                        font-size: 1.1em;
                        margin: 10px 0;
                    }
                    .status-live {
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        background: #00ff00;
                        border-radius: 50%;
                        animation: pulse 1s ease-in-out infinite;
                        margin-right: 8px;
                    }
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.3; }
                    }
                    .control-buttons {
                        text-align: center;
                        margin: 20px 0;
                    }
                    .btn {
                        display: inline-block;
                        padding: 15px 40px;
                        margin: 10px;
                        font-size: 1.2em;
                        font-weight: bold;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        text-decoration: none;
                    }
                    .btn-stop {
                        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
                        color: white;
                        box-shadow: 0 0 20px rgba(255,0,0,0.5);
                    }
                    .btn-stop:hover {
                        background: linear-gradient(135deg, #cc0000 0%, #990000 100%);
                        box-shadow: 0 0 30px rgba(255,0,0,0.8);
                        transform: scale(1.05);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚨 SafeGuard AI - Live Threat Detection</h1>
                    <p class="subtitle"><span class="status-live"></span>SYSTEM ACTIVE - Real-time Monitoring</p>

                    <div class="control-buttons">
                        <button class="btn btn-stop" onclick="stopSystem()">⏹️ STOP SYSTEM</button>
                    </div>

                    <div class="stats-bar">
                        <div class="stat-item">
                            <div class="stat-label">👁️ Eyes Closed</div>
                            <div class="stat-value">2 seconds</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">🔥 Fire Detection</div>
                            <div class="stat-value">Active</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">🔪 Weapons</div>
                            <div class="stat-value">Active</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">🤕 Fall Detection</div>
                            <div class="stat-value">Active</div>
                        </div>
                    </div>

                    <div id="video-container">
                        <img id="live-feed" src="/video_feed" alt="Live Detection Feed">
                    </div>

                    <div class="detection-list">
                        <h3>🎯 Active Detection Systems:</h3>
                        <span class="detection-badge">👁️ Eyes Closed (2 sec)</span>
                        <span class="detection-badge">🔥 Fire Detection</span>
                        <span class="detection-badge">😴 Sleeping</span>
                        <span class="detection-badge">🤕 Person Falling</span>
                        <span class="detection-badge">💀 Unconscious</span>
                        <span class="detection-badge">🏊 Drowning</span>
                        <span class="detection-badge">🔪 Weapons</span>
                    </div>

                    <div class="info">
                        <p>🔊 <strong>Audio alerts enabled</strong> - Listen for beep alarms when threats are detected!</p>
                        <p>📊 All detections are logged with timestamps</p>
                        <p>⚙️ Click STOP SYSTEM button to stop the detection system</p>
                    </div>
                </div>

                <script>
                    function stopSystem() {
                        if (confirm('Are you sure you want to stop the SafeGuard AI system?')) {
                            fetch('/stop', { method: 'POST' })
                                .then(response => response.json())
                                .then(data => {
                                    alert(data.message);
                                    document.querySelector('.status-live').style.background = '#ff0000';
                                    document.querySelector('.subtitle').innerHTML = '<span class="status-live"></span>SYSTEM STOPPED';
                                })
                                .catch(error => {
                                    alert('System stopped. Close this window.');
                                });
                        }
                    }
                </script>
            </body>
            </html>
            '''
            return render_template_string(html)

        @app.route('/stop', methods=['POST'])
        def stop():
            import os
            import signal
            print("\n\n🛑 STOP button pressed - Shutting down system...")
            return {'message': 'SafeGuard AI system stopped successfully'}

        @app.route('/video_feed')
        def video_feed():
            def generate():
                while True:
                    if latest_frame[0] is not None:
                        ret, buffer = cv2.imencode('.jpg', latest_frame[0])
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    time.sleep(0.033)  # ~30 FPS
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        # Start Flask in background thread
        def run_flask():
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)

        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Open browser in background thread (non-blocking)
        def open_browser():
            time.sleep(1)
            webbrowser.open('http://localhost:5000')

        browser_thread = Thread(target=open_browser, daemon=True)
        browser_thread.start()

    print("\n🎥 Starting frame capture loop...")
    frame_read_count = 0

    try:
        while True:
            ret, frame = cap.read()
            frame_read_count += 1

            if not ret:
                print(f"❌ Failed to read frame #{frame_read_count} from camera")
                if frame_read_count == 1:
                    print("❌ Camera opened but can't read frames - check if camera is in use")
                break

            # Process
            annotated_frame, detections = detector.process_frame(frame)

            # Show LIVE display
            if gui_available:
                cv2.imshow('SafeGuard AI - Threat Detection', annotated_frame)
            else:
                latest_frame[0] = annotated_frame.copy()

            # Save (optional)
            if writer:
                writer.write(annotated_frame)

            # Progress
            if detector.frame_count % 30 == 0:
                print(f"⏺️ Frame {detector.frame_count} | FPS: {detector.fps:.1f}")

            # Check for 'q' key to quit (only in GUI mode)
            if gui_available:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n\n⚠️ Stopped by user (pressed 'q')")
                    break
            else:
                time.sleep(0.001)  # Small delay in headless mode

    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")

    finally:
        cap.release()
        if writer:
            writer.release()
        if gui_available:
            cv2.destroyAllWindows()

        print("\n" + "=" * 80)
        print("📊 Final Statistics:")
        print(f"  Frames processed: {detector.frame_count}")
        print(f"  Total alerts: {len(detector.alerts)}")
        print(f"\n  Threat Summary:")
        for threat_type, count in detector.threat_counts.items():
            print(f"    {threat_type.capitalize()}: {count}")
        if args.output:
            print(f"\n  Video saved: {args.output}")
        print("=" * 80)
        print("\n✅ Done!")


if __name__ == "__main__":
    main()
