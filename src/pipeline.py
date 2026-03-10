import os
import time
from src.parsing.resume_parser import parse_resume
from src.parsing.hr_data_loader import load_hr_contacts
from src.rag.vector_store import build_vector_store, load_vector_store
from src.llm.email_generator import generate_email
from src.llm.email_quality_scorer import score_and_approve
from src.database.db_manager import DBManager
from dotenv import load_dotenv
load_dotenv()

# Wait between generating each email — prevents rate limiting on free models
GENERATION_DELAY = int(os.getenv("GENERATION_DELAY", "15"))  # seconds


def run_pipeline(
    resume_path   = "data/resume.pdf",
    hr_path       = "data/hr_contacts.xlsx",
    dry_run       = False,
    enable_scorer = True
):
    print("=" * 50)
    print("   GenAI Internship Outreach Pipeline")
    print("=" * 50)

    db = DBManager()

    # ── Step 1: Parse Resume ──────────────────
    print("\n📄 Step 1: Parsing resume...")
    resume_data = parse_resume(resume_path)
    print(f"   ✅ Name   : {resume_data.get('name', 'N/A')}")
    print(f"   ✅ Skills : {resume_data.get('skills', [])[:5]}")
    print(f"   ✅ Projects: {len(resume_data.get('projects', []))} found")

    # ── Step 2: Build Vector Store ────────────
    print("\n🧮 Step 2: Building vector store...")
    if not os.path.exists("data/vector_store/index.faiss"):
        build_vector_store(resume_data)
        print("   ✅ Vector store built and saved.")
    else:
        print("   ✅ Vector store already exists, skipping.")

    # ── Step 3: Load HR Contacts ──────────────
    print("\n📊 Step 3: Loading HR contacts...")
    hr_list = load_hr_contacts(hr_path)
    print(f"   ✅ Loaded {len(hr_list)} HR contacts")

    # ── Step 4: Generate + Score Emails ──────
    print(f"\n✉️  Step 4: Generating emails for {len(hr_list)} HRs...")
    print(f"   ℹ️  Using {GENERATION_DELAY}s delay between emails to avoid rate limits\n")

    results = []

    for i, hr in enumerate(hr_list, 1):
        print(f"  [{i}/{len(hr_list)}] {hr['company']} — {hr['domain']}")

        try:
            if enable_scorer:
                result = score_and_approve(hr, generate_email)
                email  = result["email"]
                score  = result["score"]
                print(f"   📧 Subject : {email['subject']}")
                print(f"   ⭐ Score   : {score['average_score']}/10 "
                      f"({'✅ Passed' if score['passed'] else '⚠️ Best attempt'})"
                      f" — {result['attempts']} attempt(s)")
            else:
                email  = generate_email(hr)
                result = {"email": email, "score": None, "attempts": 1}
                print(f"   📧 Subject : {email['subject']}")

            results.append({
                "hr":       hr,
                "email":    email,
                "score":    result.get("score"),
                "attempts": result.get("attempts", 1)
            })

        except Exception as e:
            print(f"   ❌ Error for {hr['company']}: {e}")
            continue

        # Wait between emails to avoid rate limiting
        if i < len(hr_list):
            print(f"   ⏳ Waiting {GENERATION_DELAY}s before next email...")
            time.sleep(GENERATION_DELAY)

    if not results:
        print("\n❌ No emails generated. Check your API key and model settings.")
        return []

    # ── Step 5: Dry Run Preview ───────────────
    if dry_run:
        print("\n" + "=" * 50)
        print("   DRY RUN — Emails NOT sent. Preview below:")
        print("=" * 50)
        for r in results:
            print(f"\n🏢 {r['hr']['company']} → {r['hr']['hr_email']}")
            print(f"   Subject : {r['email']['subject']}")
            print(f"   Preview : {r['email']['body'][:120]}...")
            if r["score"]:
                print(f"   Score   : {r['score']['average_score']}/10")
        print("\n✅ Dry run complete. Use without --dry-run to actually send.")
        return results

    # ── Step 5 (real): Send Emails ────────────
    print(f"\n📤 Step 5: Sending {len(results)} emails...")
    from src.email.gmail_client import send_email_with_log

    sent_count  = 0
    error_count = 0

    for i, r in enumerate(results):
        hr         = r["hr"]
        email_data = r["email"]
        score_data = r["score"]

        try:
            msg_id, thread_id = send_email_with_log(
                to          = hr["hr_email"],
                subject     = email_data["subject"],
                body        = email_data["body"],
                resume_path = resume_path
            )

            db.log_sent_email(hr, email_data, msg_id, thread_id, score_data)

            sent_count += 1
            print(f"   ✅ [{i+1}/{len(results)}] Sent to {hr['hr_name']} at {hr['company']}")

            # Wait between sends (anti-spam)
            if i < len(results) - 1:
                print(f"   ⏳ Waiting 45s before next send...")
                time.sleep(45)

        except Exception as e:
            error_count += 1
            print(f"   ❌ Failed to send to {hr['company']}: {e}")
            continue

    # ── Summary ───────────────────────────────
    print("\n" + "=" * 50)
    print("   Pipeline Complete!")
    print("=" * 50)
    print(f"   ✅ Sent    : {sent_count}")
    print(f"   ❌ Errors  : {error_count}")
    print(f"\n   Next steps:")
    print(f"   → Check replies  : python main.py --mode check_replies")
    print(f"   → Send followups : python main.py --mode followups")
    print(f"   → Dashboard      : streamlit run ui/streamlit_app.py")

    return results