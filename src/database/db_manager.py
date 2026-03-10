from src.database.models import SessionLocal, HRContact, EmailCampaign, FollowUp, init_db
from datetime import datetime, timedelta


class DBManager:
    def __init__(self):
        init_db()
        self.session = SessionLocal()

    # ── HR Contacts ───────────────────────────────

    def add_hr_contact(self, hr: dict) -> HRContact:
        """Add HR contact if not exists. Returns contact object."""
        existing = self.session.query(HRContact).filter_by(
            hr_email=hr["hr_email"]
        ).first()
        if existing:
            return existing

        contact = HRContact(
            hr_name  = hr.get("hr_name", ""),
            hr_email = hr.get("hr_email", ""),
            company  = hr.get("company", ""),
            domain   = hr.get("domain", ""),
            website  = hr.get("website", ""),
        )
        self.session.add(contact)
        self.session.commit()
        return contact

    # ── Email Campaigns ───────────────────────────

    def log_sent_email(self, hr: dict, email_data: dict,
                       msg_id: str, thread_id: str = None,
                       score_data: dict = None) -> EmailCampaign:
        """
        Log a sent email to the database.
        Args:
            hr         : HR contact dict
            email_data : {"subject", "body", "retrieved_context"(optional)}
            msg_id     : Gmail message ID
            thread_id  : Gmail thread ID (for reply tracking)
            score_data : Quality scorer result dict (optional)
        """
        contact = self.add_hr_contact(hr)

        campaign = EmailCampaign(
            hr_id                 = contact.id,
            subject               = email_data.get("subject", ""),
            body                  = email_data.get("body", ""),
            rag_context           = email_data.get("retrieved_context", ""),
            gmail_msg_id          = msg_id,
            thread_id             = thread_id or "",
            status                = "pending",
            quality_score         = score_data["average_score"]        if score_data else 0.0,
            personalization_score = score_data["personalization_score"] if score_data else 0,
            professionalism_score = score_data["professionalism_score"] if score_data else 0,
            relevance_score       = score_data["relevance_score"]       if score_data else 0,
            attempts              = score_data.get("attempts", 1)       if score_data else 1,
        )
        self.session.add(campaign)
        self.session.commit()
        print(f"   💾 Logged to DB: {hr['company']} (id={campaign.id})")
        return campaign

    def update_status(self, campaign_id: int, status: str):
        """Update campaign status. Sets replied_at if status is 'replied'."""
        c = self.session.query(EmailCampaign).filter_by(id=campaign_id).first()
        if c:
            c.status = status
            if status == "replied":
                c.replied_at = datetime.utcnow()
            self.session.commit()

    # ── Reply Monitoring ──────────────────────────

    def get_pending_emails(self) -> list:
        """Return all emails still awaiting a reply."""
        campaigns = self.session.query(EmailCampaign).filter(
            EmailCampaign.status.in_(["pending", "sent"])
        ).all()

        result = []
        for c in campaigns:
            hr = self.session.query(HRContact).filter_by(id=c.hr_id).first()
            result.append({
                "id":        c.id,
                "thread_id": c.thread_id,
                "hr_email":  hr.hr_email  if hr else "",
                "hr_name":   hr.hr_name   if hr else "",
                "company":   hr.company   if hr else "",
                "subject":   c.subject,
                "sent_at":   c.sent_at,
            })
        return result

    def get_overdue_emails(self, days: int = 15) -> list:
        """Return pending emails older than `days` days — need follow-up."""
        cutoff    = datetime.utcnow() - timedelta(days=days)
        campaigns = self.session.query(EmailCampaign).filter(
            EmailCampaign.status == "pending",
            EmailCampaign.sent_at <= cutoff
        ).all()

        result = []
        for c in campaigns:
            hr = self.session.query(HRContact).filter_by(id=c.hr_id).first()
            result.append({
                "id":               c.id,
                "hr_email":         hr.hr_email  if hr else "",
                "hr_name":          hr.hr_name   if hr else "",
                "company":          hr.company   if hr else "",
                "subject":          c.subject,
                "sent_at":          str(c.sent_at),
                "original_subject": c.subject,
            })
        return result

    # ── Follow-ups ────────────────────────────────

    def log_followup(self, record: dict, followup_data: dict, msg_id: str):
        """Log a follow-up email and update campaign status."""
        fu = FollowUp(
            campaign_id  = record["id"],
            subject      = followup_data["subject"],
            body         = followup_data["body"],
            gmail_msg_id = msg_id,
        )
        self.session.add(fu)
        self.update_status(record["id"], "followup_sent")
        self.session.commit()
        print(f"   💾 Follow-up logged for campaign id={record['id']}")

    # ── Stats for Dashboard ───────────────────────

    def get_campaign_stats(self) -> dict:
        """Quick stats summary for Streamlit dashboard."""
        total     = self.session.query(EmailCampaign).count()
        replied   = self.session.query(EmailCampaign).filter_by(status="replied").count()
        pending   = self.session.query(EmailCampaign).filter_by(status="pending").count()
        followups = self.session.query(EmailCampaign).filter_by(status="followup_sent").count()

        return {
            "total":      total,
            "replied":    replied,
            "pending":    pending,
            "followups":  followups,
            "reply_rate": round(replied / total * 100, 1) if total > 0 else 0,
        }