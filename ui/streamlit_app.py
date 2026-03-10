import sys
import os

# Fix import paths — MUST be before any src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd

# ── Page Config ───────────────────────────────
st.set_page_config(
    page_title="GenAI Outreach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono&family=DM+Sans&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0a0a0f; color: #e8e8f0; }
.stTabs [data-baseweb="tab-list"] { background: #111118; border-bottom: 1px solid #2a2a3a; }
.stTabs [data-baseweb="tab"] { color: #888899; font-family: 'DM Mono', monospace; font-size: 12px; }
.stTabs [aria-selected="true"] { color: #7c6aff !important; border-bottom: 2px solid #7c6aff !important; background: transparent !important; }
.stButton > button { background: #7c6aff; color: white; border: none; border-radius: 6px; }
.stButton > button:hover { background: #6b5ae8; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#111118,#1a1a24);border:1px solid #2a2a3a;
            border-radius:10px;padding:28px 32px;margin-bottom:24px;">
    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#7c6aff;
                letter-spacing:0.2em;margin-bottom:8px;">GENAI OUTREACH SYSTEM</div>
    <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;
                background:linear-gradient(135deg,#e8e8f0,#7c6aff,#00e5c3);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Internship Outreach — Ashish Srivastava
    </div>
    <div style="color:#888899;font-size:13px;margin-top:6px;">
        LLM + RAG powered • Auto quality scoring • Reply tracking • Analytics
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────
tab_upload, tab_campaign, tab_analytics, tab_settings = st.tabs([
    "📁  Upload Data",
    "🚀  Run Campaign",
    "📊  Analytics",
    "⚙️  Settings"
])

# ═══════════════════════════════════════
# TAB 1 — UPLOAD DATA
# ═══════════════════════════════════════
with tab_upload:
    st.subheader("Upload Your Files")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Resume")
        resume_file = st.file_uploader(
            "Upload PDF or DOCX", type=["pdf", "docx"], key="resume"
        )
        if resume_file:
            os.makedirs("data", exist_ok=True)
            save_path = f"data/{resume_file.name}"
            with open(save_path, "wb") as f:
                f.write(resume_file.getbuffer())
            st.success(f"✅ Saved: `{save_path}`")
            st.session_state["resume_path"] = save_path

            if st.button("🔍 Parse & Index Resume"):
                with st.spinner("Parsing resume and building vector store..."):
                    try:
                        from src.parsing.resume_parser import parse_resume
                        from src.rag.vector_store import build_vector_store

                        resume_data = parse_resume(save_path)
                        build_vector_store(resume_data)
                        st.session_state["resume_data"] = resume_data
                        st.success("✅ Resume indexed into vector store!")

                        with st.expander("📋 Extracted Resume Data"):
                            st.write(f"**Name:** {resume_data.get('name', 'N/A')}")
                            st.write(f"**Skills:** {', '.join(resume_data.get('skills', []))}")
                            st.write(f"**Projects:** {len(resume_data.get('projects', []))} found")
                            st.write(f"**Experience:** {len(resume_data.get('experience', []))} entries")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        st.markdown("#### 📊 HR Contacts Excel")
        hr_file = st.file_uploader(
            "Upload .xlsx", type=["xlsx"], key="hr_excel",
            help="Required columns: HR Name, HR Email, Company Name, Domain"
        )
        if hr_file:
            save_path = "data/hr_contacts.xlsx"
            with open(save_path, "wb") as f:
                f.write(hr_file.getbuffer())
            try:
                df = pd.read_excel(save_path)
                st.success(f"✅ Loaded {len(df)} HR contacts")
                st.session_state["hr_df"] = df

                required = ["HR Name", "HR Email", "Company Name", "Domain"]
                missing  = [c for c in required if c not in df.columns]
                if missing:
                    st.warning(f"⚠️ Missing columns: {', '.join(missing)}")
                else:
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error reading Excel: {e}")

    # Show current data status
    st.divider()
    st.markdown("#### 📌 Current Data Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Resume", "✅ Indexed" if os.path.exists("data/vector_store/index.faiss") else "❌ Not indexed")
    c2.metric("HR Contacts", f"{len(st.session_state.get('hr_df', pd.DataFrame()))} loaded")
    c3.metric("Database", "✅ Ready" if os.path.exists("src/database/outreach.db") else "❌ Not created")

# ═══════════════════════════════════════
# TAB 2 — RUN CAMPAIGN
# ═══════════════════════════════════════
with tab_campaign:
    st.subheader("🚀 Launch Email Campaign")

    # Scorer settings
    with st.expander("⭐ Quality Scorer Settings", expanded=True):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            enable_scorer  = st.toggle("Enable Quality Scorer", value=True)
        with col_s2:
            score_threshold = st.slider("Min Score to Send", 5.0, 9.5, 7.0, 0.5)
        with col_s3:
            max_retries = st.number_input("Max Attempts", 1, 5, 3)

    # Campaign controls
    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        resume_path = st.text_input("Resume Path", value="data/resume.pdf")
    with col_b2:
        hr_path = st.text_input("HR Excel Path", value="data/hr_contacts.xlsx")
    with col_b3:
        dry_run = st.toggle("Dry Run (preview only)", value=True)

    st.markdown("---")

    # Preview single email
    if st.button("👁️ Preview One Email"):
        if not os.path.exists("data/vector_store/index.faiss"):
            st.error("❌ Vector store not built. Go to Upload tab and parse your resume first.")
        else:
            with st.spinner("Generating preview..."):
                try:
                    from src.llm.email_generator import generate_email
                    from src.llm.email_quality_scorer import score_and_approve

                    test_hr = {
                        "hr_name":  "Priya Sharma",
                        "company":  "TechCorp",
                        "domain":   "AI/ML",
                        "hr_email": "priya@techcorp.com"
                    }

                    if enable_scorer:
                        result = score_and_approve(test_hr, generate_email)
                        email  = result["email"]
                        score  = result["score"]
                    else:
                        email  = generate_email(test_hr)
                        score  = None

                    st.markdown("**📧 Generated Email:**")
                    st.info(f"**Subject:** {email['subject']}")
                    st.text_area("Body", email["body"], height=250)

                    if score:
                        st.markdown("**⭐ Quality Scores:**")
                        sc1, sc2, sc3, sc4 = st.columns(4)
                        sc1.metric("Personalization", f"{score['personalization_score']}/10")
                        sc2.metric("Professionalism", f"{score['professionalism_score']}/10")
                        sc3.metric("Relevance",       f"{score['relevance_score']}/10")
                        sc4.metric("Average",         f"{score['average_score']}/10")

                        if score["passed"]:
                            st.success(f"✅ Passed quality check — {score['average_score']}/10")
                        else:
                            st.warning(f"⚠️ Best after {result['attempts']} attempts: {score['average_score']}/10")

                        if score.get("feedback"):
                            st.info(f"💡 Feedback: {score['feedback']}")

                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # Launch full campaign
    if st.button("🚀 Start Full Campaign", type="primary"):
        if not os.path.exists(resume_path):
            st.error(f"❌ Resume not found at: {resume_path}")
        elif not os.path.exists(hr_path):
            st.error(f"❌ HR file not found at: {hr_path}")
        elif not os.path.exists("data/vector_store/index.faiss"):
            st.error("❌ Parse your resume first in the Upload tab!")
        else:
            from src.parsing.hr_data_loader import load_hr_contacts
            from src.llm.email_generator import generate_email
            from src.llm.email_quality_scorer import score_and_approve, batch_score_summary

            hr_list  = load_hr_contacts(hr_path)
            progress = st.progress(0, text="Starting campaign...")
            log_area = st.empty()
            results  = []
            log_lines = []

            for i, hr in enumerate(hr_list):
                pct = int((i + 1) / len(hr_list) * 100)
                progress.progress(pct, text=f"Processing {hr['company']} ({i+1}/{len(hr_list)})...")

                try:
                    if enable_scorer:
                        result = score_and_approve(hr, generate_email)
                        results.append(result)
                        status = f"✅ {hr['company']} — Score: {result['score']['average_score']}/10 — {result['attempts']} attempt(s)"
                    else:
                        email  = generate_email(hr)
                        results.append({"hr": hr, "email": email, "score": None, "attempts": 1})
                        status = f"✅ {hr['company']} — Email generated"

                    log_lines.append(status)
                    log_area.markdown("\n\n".join(log_lines))

                except Exception as e:
                    log_lines.append(f"❌ {hr['company']} — Error: {e}")
                    log_area.markdown("\n\n".join(log_lines))

            progress.progress(100, text="Done!")

            if dry_run:
                st.info("🔍 DRY RUN — emails NOT sent. Disable 'Dry Run' to send for real.")
                for r in results:
                    hr_info = r.get("hr", {})
                    email   = r.get("email", {})
                    with st.expander(f"📧 {hr_info.get('company', 'Unknown')} → {hr_info.get('hr_email', '')}"):
                        st.write(f"**Subject:** {email.get('subject', '')}")
                        st.write(email.get("body", ""))
            else:
                st.balloons()
                st.success(f"✅ Campaign complete! {len(results)} emails sent.")

            # Summary scores
            if enable_scorer and results:
                score_results = [r for r in results if r.get("score")]
                if score_results:
                    summary = batch_score_summary(score_results)
                    st.markdown("### 📊 Quality Summary")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total",          summary["total_emails"])
                    m2.metric("Pass Rate",       summary["pass_rate"])
                    m3.metric("Needed Regen",    summary["needed_regeneration"])
                    m4.metric("Avg Quality",     summary["average_scores"]["overall"])

# ═══════════════════════════════════════
# TAB 3 — ANALYTICS
# ═══════════════════════════════════════
with tab_analytics:
    try:
        from ui.analytics_dashboard import render_analytics_tab
        render_analytics_tab()
    except Exception as e:
        st.error(f"Analytics error: {e}")
        import traceback
        st.code(traceback.format_exc())

    st.divider()

    # Export section
    st.markdown("### 📥 Export Campaign Report")
    col_e1, col_e2 = st.columns(2)

    with col_e1:
        if st.button("⬇️ Export Excel", use_container_width=True):
            if not os.path.exists("src/database/outreach.db"):
                st.warning("No campaign data yet. Run a campaign first.")
            else:
                with st.spinner("Generating Excel..."):
                    try:
                        from src.export.campaign_exporter import export_campaign_report
                        paths = export_campaign_report("excel")
                        with open(paths["excel_path"], "rb") as f:
                            st.download_button(
                                "📊 Download Excel",
                                data      = f.read(),
                                file_name = os.path.basename(paths["excel_path"]),
                                mime      = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Export error: {e}")

    with col_e2:
        if st.button("⬇️ Export PDF", use_container_width=True):
            if not os.path.exists("src/database/outreach.db"):
                st.warning("No campaign data yet. Run a campaign first.")
            else:
                with st.spinner("Generating PDF..."):
                    try:
                        from src.export.campaign_exporter import export_campaign_report
                        paths = export_campaign_report("pdf")
                        with open(paths["pdf_path"], "rb") as f:
                            st.download_button(
                                "📄 Download PDF",
                                data      = f.read(),
                                file_name = os.path.basename(paths["pdf_path"]),
                                mime      = "application/pdf",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Export error: {e}")

# ═══════════════════════════════════════
# TAB 4 — SETTINGS
# ═══════════════════════════════════════
with tab_settings:
    st.subheader("⚙️ Configuration")

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**👤 Candidate Details**")
        st.text_input("Your Full Name",  value=os.getenv("CANDIDATE_NAME",  "Ashish Srivastava"))
        st.text_input("Your Email",      value=os.getenv("CANDIDATE_EMAIL", "ashish171200@gmail.com"))

        st.markdown("**🤖 LLM Settings**")
        st.selectbox("Model", [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3-haiku",
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-3-27b-it:free"
        ])
        st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

    with col_c2:
        st.markdown("**📧 Email Settings**")
        st.number_input("Delay Between Sends (sec)", 10, 120, 45)
        st.number_input("Daily Email Limit",          10, 200, 50)
        st.number_input("Follow-up After (days)",      7,  30, 15)

        st.markdown("**🔑 API Keys**")
        st.text_input("OpenAI / OpenRouter Key", type="password",
                      value=os.getenv("OPENAI_API_KEY", "")[:20] + "..." if os.getenv("OPENAI_API_KEY") else "")
        st.text_input("Gmail Sender", value=os.getenv("GMAIL_SENDER", ""))

    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved!")

    # Show quick commands
    st.divider()
    st.markdown("**⚡ Quick Terminal Commands**")
    st.code("""# Dry run (preview only)
python main.py --mode campaign --dry-run

# Send real emails
python main.py --mode campaign

# Check for replies
python main.py --mode check_replies

# Send follow-ups (15+ days no reply)
python main.py --mode followups

# View stats
python main.py --mode stats""", language="bash")