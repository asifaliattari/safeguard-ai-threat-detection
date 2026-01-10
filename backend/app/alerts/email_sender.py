"""
Email Alert Sender
Sends email notifications for critical detections
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, Optional
from datetime import datetime


class EmailSender:
    """Gmail SMTP email sender"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL") or self.smtp_user

        if not self.smtp_user or not self.smtp_password:
            print("⚠️  WARNING: Email credentials not set. Email alerts disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✅ Email alerts enabled ({self.smtp_user})")

    async def send_detection_alert(
        self,
        to_email: str,
        detection: Dict,
        diagnosis: Optional[Dict] = None
    ) -> bool:
        """
        Send detection alert email

        Args:
            to_email: Recipient email
            detection: Detection dict
            diagnosis: Optional Claude diagnosis

        Returns:
            True if sent successfully
        """

        if not self.enabled:
            print("Email not configured, skipping alert")
            return False

        try:
            # Build email content
            severity = diagnosis['severity'] if diagnosis else 'unknown'
            message_text = diagnosis['message'] if diagnosis else f"{detection['type']} detected"

            severity_emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '⚡',
                'low': 'ℹ️'
            }.get(severity, '⚠️')

            subject = f"{severity_emoji} SafeGuard AI Alert: {detection['type'].upper()}"

            # HTML email body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #ef4444; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .footer {{ background: #374151; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
        .alert-box {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 15px 0; }}
        .info-row {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #374151; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{severity_emoji} SafeGuard AI Security Alert</h1>
        </div>

        <div class="content">
            <div class="alert-box">
                <h2 style="margin-top: 0;">⚠️ {detection['type'].upper()} DETECTED</h2>
                <p style="font-size: 16px; margin: 10px 0;">{message_text}</p>
            </div>

            <div class="info-row">
                <span class="label">Severity:</span>
                <span style="color: #ef4444; font-weight: bold; text-transform: uppercase;">{severity}</span>
            </div>

            <div class="info-row">
                <span class="label">Confidence:</span>
                <span>{detection['confidence']*100:.1f}%</span>
            </div>

            <div class="info-row">
                <span class="label">Time:</span>
                <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>

            <div class="info-row">
                <span class="label">Object Type:</span>
                <span>{detection['type']}</span>
            </div>

            {f'<div class="info-row"><span class="label">AI Analysis:</span><br/><span>{diagnosis.get("reasoning", "N/A")}</span></div>' if diagnosis else ''}

            <p style="margin-top: 20px; padding: 15px; background: #dbeafe; border-radius: 6px;">
                <strong>Recommended Action:</strong><br/>
                {'Immediate attention required. Verify the situation and take appropriate action.' if diagnosis and diagnosis.get('should_alert') else 'Monitor the situation. This may be a routine detection.'}
            </p>
        </div>

        <div class="footer">
            <p>SafeGuard AI - Real-time Video Threat Detection</p>
            <p style="margin-top: 5px; opacity: 0.8;">This is an automated alert from your AI safety monitoring system</p>
        </div>
    </div>
</body>
</html>
"""

            # Plain text version
            text_body = f"""
SafeGuard AI Security Alert

{severity_emoji} {detection['type'].upper()} DETECTED

{message_text}

Details:
- Severity: {severity.upper()}
- Confidence: {detection['confidence']*100:.1f}%
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Object Type: {detection['type']}

This is an automated alert from SafeGuard AI.
"""

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=10
            )

            print(f"✅ Email alert sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


# Global instance
_email_sender = None


def get_email_sender() -> EmailSender:
    """Get or create global email sender"""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
