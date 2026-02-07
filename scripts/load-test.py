#!/usr/bin/env python3
"""
SafeGuard AI - Load Testing Script
Simulates multiple concurrent users sending frames for detection
"""

import asyncio
import websockets
import json
import base64
import time
import random
from pathlib import Path
from typing import List
import argparse
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class TestResult:
    """Test result metrics"""
    user_id: str
    frames_sent: int
    frames_received: int
    avg_latency: float
    max_latency: float
    min_latency: float
    errors: int
    success_rate: float


class LoadTester:
    """Load testing for SafeGuard AI backend"""

    def __init__(self, backend_url: str, num_users: int = 10, frames_per_user: int = 100):
        self.backend_url = backend_url.replace("http://", "ws://").replace("https://", "wss://")
        self.num_users = num_users
        self.frames_per_user = frames_per_user
        self.results: List[TestResult] = []

        # Sample frame (1x1 black pixel JPEG)
        self.sample_frame = self._create_sample_frame()

    def _create_sample_frame(self) -> str:
        """Create a minimal valid JPEG frame for testing"""
        # Minimal JPEG base64 (1x1 black pixel)
        minimal_jpeg = (
            "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcG"
            "BwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwM"
            "DAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIA"
            "AhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEB"
            "AQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwABgA"
            "AAAAH//Z"
        )
        return f"data:image/jpeg;base64,{minimal_jpeg}"

    async def simulate_user(self, user_id: str) -> TestResult:
        """Simulate a single user sending frames"""
        frames_sent = 0
        frames_received = 0
        errors = 0
        latencies = []

        ws_url = f"{self.backend_url}/ws/detect/{user_id}"

        try:
            async with websockets.connect(ws_url) as websocket:
                print(f"✅ User {user_id} connected")

                for i in range(self.frames_per_user):
                    try:
                        # Send frame
                        start_time = time.time()

                        message = {
                            "type": "frame",
                            "frame": self.sample_frame
                        }
                        await websocket.send(json.dumps(message))
                        frames_sent += 1

                        # Receive response
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        end_time = time.time()

                        data = json.loads(response)
                        if data.get("type") == "detection_result":
                            frames_received += 1
                            latency = (end_time - start_time) * 1000  # ms
                            latencies.append(latency)

                        # Simulate realistic user behavior (3 FPS)
                        await asyncio.sleep(0.333)

                    except asyncio.TimeoutError:
                        errors += 1
                        print(f"⏱️  User {user_id} timeout on frame {i}")
                    except Exception as e:
                        errors += 1
                        print(f"❌ User {user_id} error on frame {i}: {e}")

        except Exception as e:
            print(f"❌ User {user_id} connection failed: {e}")
            errors = self.frames_per_user

        # Calculate metrics
        avg_latency = np.mean(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        success_rate = (frames_received / frames_sent * 100) if frames_sent > 0 else 0

        return TestResult(
            user_id=user_id,
            frames_sent=frames_sent,
            frames_received=frames_received,
            avg_latency=avg_latency,
            max_latency=max_latency,
            min_latency=min_latency,
            errors=errors,
            success_rate=success_rate
        )

    async def run_load_test(self):
        """Run load test with multiple concurrent users"""
        print(f"\n🚀 Starting Load Test")
        print(f"{'='*60}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Concurrent Users: {self.num_users}")
        print(f"Frames per User: {self.frames_per_user}")
        print(f"Total Frames: {self.num_users * self.frames_per_user}")
        print(f"{'='*60}\n")

        start_time = time.time()

        # Create tasks for all users
        tasks = [
            self.simulate_user(f"load_test_user_{i}")
            for i in range(self.num_users)
        ]

        # Run all users concurrently
        self.results = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # Print results
        self._print_results(duration)

    def _print_results(self, duration: float):
        """Print test results"""
        print(f"\n📊 Load Test Results")
        print(f"{'='*60}")
        print(f"Total Duration: {duration:.2f}s")
        print(f"{'='*60}\n")

        # Per-user results
        print("Per-User Metrics:")
        print(f"{'User ID':<20} {'Sent':<8} {'Received':<10} {'Success%':<10} {'Avg Latency':<15}")
        print(f"{'-'*70}")

        total_sent = 0
        total_received = 0
        total_errors = 0
        all_latencies = []

        for result in self.results:
            print(f"{result.user_id:<20} {result.frames_sent:<8} {result.frames_received:<10} "
                  f"{result.success_rate:<9.1f}% {result.avg_latency:<13.1f}ms")

            total_sent += result.frames_sent
            total_received += result.frames_received
            total_errors += result.errors
            if result.avg_latency > 0:
                all_latencies.append(result.avg_latency)

        # Aggregate metrics
        print(f"\n{'='*60}")
        print("Aggregate Metrics:")
        print(f"  Total Frames Sent: {total_sent}")
        print(f"  Total Frames Received: {total_received}")
        print(f"  Total Errors: {total_errors}")
        print(f"  Overall Success Rate: {(total_received/total_sent*100):.2f}%")
        print(f"  Average Latency: {np.mean(all_latencies):.2f}ms")
        print(f"  Median Latency: {np.median(all_latencies):.2f}ms")
        print(f"  P95 Latency: {np.percentile(all_latencies, 95):.2f}ms")
        print(f"  P99 Latency: {np.percentile(all_latencies, 99):.2f}ms")
        print(f"  Throughput: {total_received/duration:.2f} frames/second")
        print(f"{'='*60}\n")

        # Assessment
        avg_latency = np.mean(all_latencies)
        success_rate = (total_received / total_sent * 100)

        if success_rate >= 95 and avg_latency < 1000:
            print("✅ PASS - Backend performance is excellent!")
        elif success_rate >= 90 and avg_latency < 2000:
            print("⚠️  PASS - Backend performance is acceptable but could be optimized")
        else:
            print("❌ FAIL - Backend performance needs improvement")

        print(f"\n💡 Recommendations:")
        if avg_latency > 1000:
            print("  - Consider optimizing model inference time")
            print("  - Use GPU acceleration if available")
            print("  - Reduce frame size or quality")
        if success_rate < 95:
            print("  - Increase server resources")
            print("  - Implement request queuing")
            print("  - Add load balancing")


def main():
    parser = argparse.ArgumentParser(description="SafeGuard AI Load Testing")
    parser.add_argument("backend_url", help="Backend WebSocket URL (e.g., ws://localhost:8000)")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users (default: 10)")
    parser.add_argument("--frames", type=int, default=100, help="Frames per user (default: 100)")

    args = parser.parse_args()

    tester = LoadTester(
        backend_url=args.backend_url,
        num_users=args.users,
        frames_per_user=args.frames
    )

    asyncio.run(tester.run_load_test())


if __name__ == "__main__":
    main()
