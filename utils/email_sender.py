import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("MAIL_SENDER")
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")


def send_email_with_report(receiver_email, report_path):

    msg = EmailMessage()

    msg["Subject"] = "Automated Attendance Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        """Dear Professor,

The attendance session has ended.

Please find the attached report.

Regards,
LPAF Attendance System
"""
    )

    with open(report_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(report_path)

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
