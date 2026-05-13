from app.config import SEND_MODE
from app.sender import mock_send_email
from app.real_sender import send_real_email


def dispatch_email(to_email, email_response):

    if SEND_MODE == "SMTP":

        return send_real_email(
            to_email=to_email,
            email_response=email_response
        )

    else:

        return mock_send_email(
            to_email=to_email,
            email_response=email_response
        )