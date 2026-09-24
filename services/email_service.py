import os
import requests


def send_email(to_email, subject, html_body, text_body=None):
    key = (os.getenv("BREVO_API_KEY") or "").strip()
    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    sender_name = os.getenv("BREVO_SENDER_NAME", "AI Skill Gap Analyzer")
    reply_to_email = os.getenv("BREVO_REPLY_TO_EMAIL")

    if not key or not sender_email:
        return False, "BREVO_API_KEY and BREVO_SENDER_EMAIL are required"

    parameters = {
        "htmlContent": html_body,
        "subject": subject,
        "to": [{"email": to_email}],
        "sender": {"email": sender_email, "name": sender_name},
    }
    if reply_to_email:
        parameters["replyTo"] = {"email": reply_to_email, "name": sender_name}

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": key,
                "Content-Type": "application/json",
            },
            json=parameters,
            timeout=20,
        )

        if response.status_code in (200, 201):
            data = response.json()
            return True, data.get("messageId") or data.get("id") or "sent"

        try:
            error = response.json().get("message", response.text[:200])
        except ValueError:
            error = response.text[:200]
        return False, f"Brevo {response.status_code}: {error}"
    except Exception as exc:
        return False, str(exc)
