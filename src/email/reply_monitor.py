from src.email.gmail_client import get_gmail_service

def check_replies(db_manager):
    service = get_gmail_service()
    pending = db_manager.get_pending_emails()
    for record in pending:
        if not record.get("thread_id"):
            continue
        try:
            thread = service.users().threads().get(
                userId="me", id=record["thread_id"]
            ).execute()
            if len(thread["messages"]) > 1:
                db_manager.update_status(record["id"], "replied")
                print(f"Reply detected from {record['hr_email']}")
        except Exception as e:
            print(f"Error checking thread: {e}")

def check_and_send_followups(db_manager, resume_path=None):
    from src.llm.followup_generator import generate_followup
    from src.email.gmail_client import send_email
    overdue = db_manager.get_overdue_emails(days=15)
    for record in overdue:
        try:
            followup = generate_followup(record)
            msg_id = send_email(
                to=record["hr_email"],
                subject=followup["subject"],
                body=followup["body"]
            )
            db_manager.log_followup(record, followup, msg_id)
            print(f"Follow-up sent to {record['hr_name']} at {record['company']}")
        except Exception as e:
            print(f"Error sending follow-up: {e}")