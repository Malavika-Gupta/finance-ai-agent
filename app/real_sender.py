import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")


def send_real_email(to_email, email_response):

    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    # Create email message
    msg = MIMEText(email_response.body)

    msg["Subject"] = email_response.subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        # Login
        server.login(sender_email, app_password)

        # Send email
        server.send_message(msg)

        server.quit()

        print(f"\nREAL EMAIL SENT TO {to_email}")

        return {
            "status": "SUCCESS",
            "delivery_mode": "SMTP"
        }

    except Exception as e:

        print("\nEMAIL SEND FAILED")
        print(e)

        return {
            "status": "FAILED",
            "delivery_mode": "SMTP"
        }