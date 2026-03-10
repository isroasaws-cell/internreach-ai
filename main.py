import argparse
from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="GenAI Internship Outreach System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--mode",
        choices=["campaign", "check_replies", "followups", "stats"],
        default="campaign",
        help=(
            "campaign      → Generate + send outreach emails\n"
            "check_replies → Poll Gmail for replies\n"
            "followups     → Send follow-ups to non-replies (15+ days)\n"
            "stats         → Show campaign stats in terminal"
        )
    )
    parser.add_argument("--resume",    default="data/resume.pdf",
                        help="Path to resume PDF or DOCX")
    parser.add_argument("--hr",        default="data/hr_contacts.xlsx",
                        help="Path to HR contacts Excel file")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Preview emails without sending")
    parser.add_argument("--no-scorer", action="store_true",
                        help="Skip quality scorer (faster, less API calls)")
    args = parser.parse_args()

    # ── Campaign Mode ─────────────────────────────
    if args.mode == "campaign":
        from src.pipeline import run_pipeline
        run_pipeline(
            resume_path    = args.resume,
            hr_path        = args.hr,
            dry_run        = args.dry_run,
            enable_scorer  = not args.no_scorer
        )

    # ── Check Replies Mode ────────────────────────
    elif args.mode == "check_replies":
        print("📬 Checking Gmail for replies...")
        from src.email.reply_monitor import check_replies
        from src.database.db_manager import DBManager
        db = DBManager()
        check_replies(db)
        print("✅ Reply check complete.")

    # ── Follow-up Mode ────────────────────────────
    elif args.mode == "followups":
        print("🔄 Checking for overdue emails and sending follow-ups...")
        from src.email.reply_monitor import check_and_send_followups
        from src.database.db_manager import DBManager
        db = DBManager()
        check_and_send_followups(db)
        print("✅ Follow-up check complete.")

    # ── Stats Mode ────────────────────────────────
    elif args.mode == "stats":
        from src.database.db_manager import DBManager
        db    = DBManager()
        stats = db.get_campaign_stats()
        print("\n" + "=" * 40)
        print("   📊 Campaign Stats")
        print("=" * 40)
        print(f"   Total Sent    : {stats['total']}")
        print(f"   Replied       : {stats['replied']}")
        print(f"   Pending       : {stats['pending']}")
        print(f"   Follow-ups    : {stats['followups']}")
        print(f"   Reply Rate    : {stats['reply_rate']}%")
        print("=" * 40)
        print("\n   Run 'streamlit run ui/streamlit_app.py' for full dashboard")


if __name__ == "__main__":
    main()