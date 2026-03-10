import base64, time, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]


def get_gmail_service():
    """Authenticate and return Gmail API service. Auto-refreshes token."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    # Full re-auth if no valid creds
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def build_message(to, subject, body, resume_path=None):
    """Build MIME email with optional resume attachment."""
    msg = MIMEMultipart()
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(resume_path)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email_with_log(to, subject, body, resume_path=None):
    """
    Send one email via Gmail API.
    Returns (message_id, thread_id) — both needed for reply tracking.
    """
    service = get_gmail_service()
    message = build_message(to, subject, body, resume_path)
    sent    = service.users().messages().send(userId="me", body=message).execute()

    msg_id    = sent["id"]
    thread_id = sent["threadId"]   # ← critical for reply detection
    return msg_id, thread_id


def send_campaign(hr_list, email_list, resume_path, db_manager):
    """
    Legacy send function — loops through HR list and sends emails.
    Used if calling directly without pipeline.py.
    """
    for i, (hr, email_data) in enumerate(zip(hr_list, email_list)):
        try:
            msg_id, thread_id = send_email_with_log(
                to=hr["hr_email"],
                subject=email_data["subject"],
                body=email_data["body"],
                resume_path=resume_path
            )
            db_manager.log_sent_email(hr, email_data, msg_id, thread_id)
            print(f"✅ Sent to {hr['hr_name']} at {hr['company']}")

            if i < len(hr_list) - 1:
                print(f"   ⏳ Waiting 45s...")
                time.sleep(45)

        except Exception as e:
            print(f"❌ Failed for {hr['company']}: {e}")