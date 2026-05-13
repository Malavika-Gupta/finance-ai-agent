from datetime import datetime


def mock_send_email(to_email, email_response):

    print("\n==============================")
    print("MOCK EMAIL SENT")
    print("==============================")

    print(f"To: {to_email}")
    print(f"Subject: {email_response.subject}")
    print(f"Time: {datetime.now()}")

    return {
        "status": "SUCCESS",
        "delivery_mode": "DRY_RUN"
    }