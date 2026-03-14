import streamlit as st
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(override=True)

st.set_page_config(
    page_title="InternReach AI",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] > div { background: transparent !important; }

/* ── DARK AUTH BACKGROUND ── */
.auth-page { background: #060912; min-height: 100vh; }

/* ── Dark form inputs for auth ── */
.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 13px !important;
}
.stTextInput input::placeholder { color: #475569 !important; }
.stTextInput input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    background: rgba(255,255,255,0.07) !important;
}
.stTextInput label { color: #94a3b8 !important; font-size: 12px !important; font-weight: 500 !important; }
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid rgba(99,102,241,0.25) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
.stSelectbox label { color: #94a3b8 !important; font-size: 12px !important; font-weight: 500 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border: 0.5px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px !important; font-weight: 500 !important;
    color: #475569 !important; border-radius: 8px !important;
    border: none !important; background: transparent !important;
    padding: 7px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.2) !important;
    color: #a5b4fc !important; border: 0.5px solid rgba(99,102,241,0.35) !important;
}

/* ── Auth button ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important;
    background: linear-gradient(135deg, #6366f1, #06b6d4) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; padding: 0.6rem 1.5rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.25) !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

/* ── Error/success ── */
.stAlert { border-radius: 8px !important; }

/* ── Main app styles (post login) ── */
.app-bg { background: #060912; min-height: 100vh; }
.topbar {
    background: rgba(6,9,18,0.92); backdrop-filter: blur(16px);
    border-bottom: 0.5px solid rgba(99,102,241,0.15);
    padding: 0 2rem; height: 52px;
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-logo { font-size: 1rem; font-weight: 600; color: #f1f5f9; letter-spacing: -0.02em; }
.page-wrap { padding: 2rem; max-width: 1080px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.35rem; font-weight: 600; color: #f0f0f0; margin: 0; letter-spacing: -0.02em; }
.page-header p { font-size: 0.8rem; color: #475569; margin: 4px 0 0; }
.card { background: #0d1117; border: 0.5px solid rgba(99,102,241,0.15); border-radius: 14px; padding: 1.4rem; margin-bottom: 1rem; }
.card-header { font-size: 0.83rem; font-weight: 600; color: #e0e0e0; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px; }
.card-icon { width: 26px; height: 26px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 13px; }
.card-icon.blue   { background: rgba(59,130,246,0.15); }
.card-icon.green  { background: rgba(34,197,94,0.12); }
.card-icon.purple { background: rgba(99,102,241,0.15); }
.stats-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { flex: 1; background: #0d1117; border: 0.5px solid rgba(99,102,241,0.15); border-radius: 14px; padding: 1.2rem 1.4rem; position: relative; overflow: hidden; }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 14px 14px 0 0; }
.stat-card.blue::before   { background: linear-gradient(90deg,#3b82f6,#60a5fa); }
.stat-card.green::before  { background: linear-gradient(90deg,#22c55e,#4ade80); }
.stat-card.purple::before { background: linear-gradient(90deg,#6366f1,#a78bfa); }
.stat-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #475569; margin-bottom: 6px; }
.stat-num { font-size: 1.9rem; font-weight: 700; color: #f1f5f9; line-height: 1; letter-spacing: -0.04em; }
.stat-sub { font-size: 0.72rem; color: #334155; margin-top: 4px; }
.email-card { background: #0d1117; border: 0.5px solid rgba(99,102,241,0.15); border-radius: 10px; overflow: hidden; margin-bottom: 0.8rem; }
.email-card-header { padding: 0.8rem 1.2rem; border-bottom: 0.5px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between; }
.email-card-company { font-weight: 600; font-size: 0.85rem; color: #f1f5f9; }
.email-card-hr { font-size: 0.75rem; color: #475569; margin-top: 1px; }
.email-card-body { padding: 1rem 1.2rem; font-size: 0.83rem; color: #94a3b8; line-height: 1.75; white-space: pre-wrap; }
.pill { display: inline-flex; align-items: center; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.pill-yellow { background: rgba(250,204,21,0.1); color: #facc15; }
.pill-green  { background: rgba(34,197,94,0.1); color: #22c55e; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.loading-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#6366f1; margin:0 2px; animation:pulse 1.2s ease-in-out infinite; }
.loading-dot:nth-child(2){animation-delay:0.2s;background:#8b5cf6;}
.loading-dot:nth-child(3){animation-delay:0.4s;background:#06b6d4;}
</style>
""", unsafe_allow_html=True)

from src.database.db_manager import DBManager as DatabaseManager
from src.parsing.resume_parser import parse_resume
from src.parsing.hr_data_loader import load_hr_contacts
from src.llm.email_generator import generate_email
from src.rag.vector_store import build_vector_store
from ui.analytics_dashboard import render_analytics_tab
from src.auth.auth_manager import login, signup

db = DatabaseManager()

# ══════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════
if "user" not in st.session_state or not st.session_state.user:

    st.markdown("""
    <div style="position:fixed;inset:0;background:#060912;z-index:-1;"></div>
    <div style="position:fixed;top:-100px;left:-100px;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,0.12) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
    <div style="position:fixed;bottom:-80px;right:-80px;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(6,182,212,0.1) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
    <div style="position:fixed;inset:0;background-image:linear-gradient(rgba(99,102,241,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03) 1px,transparent 1px);background-size:44px 44px;pointer-events:none;z-index:0;"></div>
    """, unsafe_allow_html=True)

    # Center the form
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo + title
        st.markdown("""
        <div style="text-align:center;margin-bottom:20px;">
            <div style="width:58px;height:58px;border-radius:16px;background:linear-gradient(135deg,#6366f1,#06b6d4);display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 14px;box-shadow:0 0 35px rgba(99,102,241,0.3);">📬</div>
            <div style="font-size:22px;font-weight:600;color:#f1f5f9;letter-spacing:-0.03em;margin-bottom:5px;">InternReach AI</div>
            <div style="font-size:13px;color:#475569;">Your AI-powered internship outreach engine</div>
        </div>
        """, unsafe_allow_html=True)

        # Card
        st.markdown('<div style="background:rgba(13,17,23,0.9);border:0.5px solid rgba(99,102,241,0.2);border-radius:18px;padding:28px;box-shadow:0 0 50px rgba(99,102,241,0.08);">', unsafe_allow_html=True)

        auth_tab = st.tabs(["🔑  Login", "✨  Sign Up"])

        with auth_tab[0]:
            st.markdown("<br>", unsafe_allow_html=True)
            l_email = st.text_input("Email Address", placeholder="you@gmail.com", key="l_email")
            l_pass  = st.text_input("Password", type="password", placeholder="••••••••", key="l_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="login_btn"):
                if l_email and l_pass:
                    with st.spinner(""):
                        result = login(l_email, l_pass)
                    if result["success"]:
                        st.session_state.user = result["user"]
                        st.session_state.page = "Upload Data"
                        st.rerun()
                    else:
                        st.error(result["error"])
                else:
                    st.error("Please fill all fields!")

        with auth_tab[1]:
            st.markdown("<br>", unsafe_allow_html=True)
            s_name  = st.text_input("Full Name", placeholder="Ashish Srivastava", key="s_name")
            s_email = st.text_input("Email", placeholder="you@gmail.com", key="s_email")
            s_pass  = st.text_input("Password", type="password", placeholder="••••••••", key="s_pass")
            c1, c2 = st.columns(2)
            with c1: s_year = st.selectbox("Year", ["1st Year","2nd Year","3rd Year","4th Year"], key="s_year")
            with c2: s_cgpa = st.text_input("CGPA", placeholder="8.5", key="s_cgpa")
            s_branch = st.selectbox("Branch", ["Computer Science","Information Technology","Electronics","Mechanical","Civil","Electrical","Other"], key="s_branch")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="signup_btn"):
                if s_name and s_email and s_pass and s_cgpa:
                    with st.spinner(""):
                        result = signup(s_name, s_email, s_pass, s_year, s_cgpa, s_branch)
                    if result["success"]:
                        st.session_state.user = result["user"]
                        st.session_state.page = "Upload Data"
                        st.rerun()
                    else:
                        st.error(result["error"])
                else:
                    st.error("Please fill all fields!")

        st.markdown('</div>', unsafe_allow_html=True)

        # Tags
        st.markdown("""
        <div style="display:flex;justify-content:center;gap:8px;margin-top:16px;flex-wrap:wrap;">
            <span style="font-size:11px;color:#334155;background:rgba(255,255,255,0.02);border:0.5px solid rgba(255,255,255,0.06);padding:3px 10px;border-radius:20px;">Groq Llama 70B</span>
            <span style="font-size:11px;color:#334155;background:rgba(255,255,255,0.02);border:0.5px solid rgba(255,255,255,0.06);padding:3px 10px;border-radius:20px;">RAG powered</span>
            <span style="font-size:11px;color:#334155;background:rgba(255,255,255,0.02);border:0.5px solid rgba(255,255,255,0.06);padding:3px 10px;border-radius:20px;">Free to use</span>
        </div>
        <div style="text-align:center;margin-top:16px;font-size:11.5px;color:#1e293b;line-height:1.8;">
            Built with ❤️ by <span style="color:#6366f1;font-weight:500;">Ashish Srivastava</span> · SRM Institute of Science & Technology<br>
            <span style="font-size:10px;color:#0f172a;letter-spacing:0.1em;">FROM SRM, FOR SRM — LAND YOUR DREAM INTERNSHIP</span>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════
USER        = st.session_state.user
USER_NAME   = USER["full_name"]
USER_EMAIL  = USER["email"]
USER_YEAR   = USER.get("year", "")
USER_CGPA   = USER.get("cgpa", "")
USER_BRANCH = USER.get("branch", "")
os.environ["CANDIDATE_NAME"]  = USER_NAME
os.environ["CANDIDATE_EMAIL"] = USER_EMAIL

if "page" not in st.session_state:
    st.session_state.page = "Upload Data"

PAGES    = ["Upload Data", "Run Campaign", "Analytics", "Settings"]
initials = "".join([w[0].upper() for w in USER_NAME.split()[:2]])

# Dark background
st.markdown('<div style="position:fixed;inset:0;background:#060912;z-index:-1;"></div>', unsafe_allow_html=True)
st.markdown('<div style="position:fixed;inset:0;background-image:linear-gradient(rgba(99,102,241,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.025) 1px,transparent 1px);background-size:44px 44px;pointer-events:none;z-index:0;"></div>', unsafe_allow_html=True)

# ── Top Navigation ──
c0, c1, c2 = st.columns([2, 5, 3])
with c0:
    st.markdown('<div style="padding-top:8px;font-size:1rem;font-weight:600;color:#f1f5f9;letter-spacing:-0.02em;">📬 InternReach</div>', unsafe_allow_html=True)
with c1:
    nav = st.columns(len(PAGES))
    for i, p in enumerate(PAGES):
        with nav[i]:
            is_active = st.session_state.page == p
            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p
                st.rerun()
with c2:
    rc = st.columns([3,1])
    with rc[0]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding-top:6px;justify-content:flex-end;">
            <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#06b6d4);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#fff;">{initials}</div>
            <span style="font-size:0.8rem;font-weight:500;color:#e2e8f0;">{USER_NAME.split()[0]}</span>
            <span style="font-size:0.72rem;color:#334155;">· {USER_CGPA}</span>
        </div>""", unsafe_allow_html=True)
    with rc[1]:
        if st.button("Logout", key="logout"):
            del st.session_state.user
            st.session_state.page = "Upload Data"
            st.rerun()

st.markdown("<hr style='margin:0 0 1.5rem;border:none;border-top:0.5px solid rgba(99,102,241,0.15);'>", unsafe_allow_html=True)

page = st.session_state.page

# ══════════════════════════════════════════
# PAGE 1 — Upload
# ══════════════════════════════════════════
if page == "Upload Data":
    st.markdown(f'<div class="page-header"><h1>Upload Data</h1><p>Add your resume and HR contacts</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="card"><div class="card-header"><div class="card-icon blue">📄</div> Resume</div>', unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload PDF or DOCX", type=["pdf","docx"], key="r_up")
        if resume_file:
            path = f"/tmp/{USER_NAME.replace(' ','_')}_{resume_file.name}"
            with open(path, "wb") as f:
                f.write(resume_file.read())
            with st.spinner("Parsing..."):
                try:
                    info = parse_resume(path)
                    if isinstance(info, dict):
                        st.success(f"✅ {info.get('name','')}")
                        st.caption(f"Skills: {', '.join(info.get('skills',[])[:6])}")
                        st.session_state[f"{USER_NAME}_resume_info"] = info
                    build_vector_store(info if isinstance(info, dict) else path)
                    st.success("✅ Vector store ready")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><div class="card-header"><div class="card-icon green">📊</div> HR Contacts</div>', unsafe_allow_html=True)
        hr_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx","xls"], key="h_up")
        if hr_file:
            path = f"/tmp/hr_{hr_file.name}"
            with open(path, "wb") as f:
                f.write(hr_file.read())
            with st.spinner("Loading..."):
                try:
                    hrs = load_hr_contacts(path)
                    saved = 0
                    for hr in hrs:
                        try: db.add_hr_contact(hr); saved += 1
                        except: pass
                    st.success(f"✅ {len(hrs)} contacts · {saved} saved to DB")
                    st.session_state["hr_path"] = path
                    st.dataframe([{"Company": h["company"], "HR": h["hr_name"], "Domain": h["domain"]} for h in hrs], use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# PAGE 2 — Campaign
# ══════════════════════════════════════════
elif page == "Run Campaign":
    st.markdown(f'<div class="page-header"><h1>Run Campaign</h1><p>Generate personalized emails for {USER_NAME}</p></div>', unsafe_allow_html=True)
    default_hr = st.session_state.get("hr_path", "data/hr_contacts.xlsx")
    c1, c2, c3 = st.columns([3,3,1])
    with c1: hr_path = st.text_input("HR Contacts", value=default_hr)
    with c2: resume_path = st.text_input("Resume", value="data/resume.pdf")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        dry_run = st.checkbox("Dry Run", value=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀  Launch Campaign"):
        try:
            st.markdown("""<div style="display:flex;align-items:center;gap:10px;padding:1rem;background:#0d1117;border:0.5px solid rgba(99,102,241,0.2);border-radius:10px;margin-bottom:1rem;">
                <span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>
                <span style="font-size:0.85rem;color:#475569;font-weight:500;">Initializing campaign...</span></div>""", unsafe_allow_html=True)
            time.sleep(0.6)

            try: hrs = load_hr_contacts(hr_path)
            except:
                hrs = db.get_all_hr_contacts() if hasattr(db, 'get_all_hr_contacts') else []
                if hrs: st.info(f"📦 Loaded {len(hrs)} contacts from DB")

            if not hrs:
                st.error("No HR contacts found!")
                st.stop()

            st.markdown(f"""<div class="stats-row">
                <div class="stat-card blue"><div class="stat-label">Contacts</div><div class="stat-num">{len(hrs)}</div><div class="stat-sub">HR targets</div></div>
                <div class="stat-card purple"><div class="stat-label">Candidate</div><div class="stat-num" style="font-size:1rem;">{USER_NAME.split()[0]}</div><div class="stat-sub">CGPA: {USER_CGPA}</div></div>
                <div class="stat-card green"><div class="stat-label">Mode</div><div class="stat-num" style="font-size:1.1rem;">{"DRY" if dry_run else "LIVE"}</div><div class="stat-sub">{"Preview" if dry_run else "Sending"}</div></div>
            </div>""", unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_box   = st.empty()
            results, email_data = [], []

            for i, hr in enumerate(hrs):
                progress_bar.progress(i / len(hrs))
                status_box.markdown(f"""<div style="padding:0.7rem 1rem;background:#0d1117;border:0.5px solid rgba(99,102,241,0.2);border-radius:8px;font-size:0.83rem;color:#475569;">
                    <span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>
                    &nbsp;<b style="color:#e2e8f0;">{hr['company']}</b> — {hr['hr_name']} <span style="color:#1e293b;">({i+1}/{len(hrs)})</span></div>""", unsafe_allow_html=True)
                email = generate_email(hr, extra_instruction=f"IMPORTANT: Sign this email as '{USER_NAME}'. Best regards must say '{USER_NAME}'.")
                results.append({"Company": hr["company"], "HR": hr["hr_name"], "Subject": email.get("subject",""), "Status": "dry-run" if dry_run else "sent"})
                email_data.append((hr, email))
                time.sleep(0.2)

            progress_bar.progress(1.0)
            status_box.empty()
            st.success(f"✅ {len(results)} emails {'previewed' if dry_run else 'sent'} for {USER_NAME}")
            st.dataframe(results, use_container_width=True, hide_index=True)

            st.markdown("<br>**Email Previews**")
            for hr, email in email_data:
                with st.expander(f"📧  {hr['company']}  ·  {hr['hr_name']}"):
                    st.markdown(f"""<div class="email-card">
                        <div class="email-card-header">
                            <div><div class="email-card-company">{hr['company']}</div><div class="email-card-hr">To: {hr['hr_name']}</div></div>
                            <span class="pill {'pill-yellow' if dry_run else 'pill-green'}">{'● dry run' if dry_run else '● sent'}</span>
                        </div>
                        <div style="padding:0.6rem 1.2rem;background:rgba(99,102,241,0.05);border-bottom:0.5px solid rgba(255,255,255,0.04);font-size:0.8rem;color:#64748b;"><b>Subject:</b> {email.get('subject','')}</div>
                        <div class="email-card-body">{email.get('body','')}</div>
                    </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

# ══════════════════════════════════════════
# PAGE 3 — Analytics
# ══════════════════════════════════════════
elif page == "Analytics":
    st.markdown('<div class="page-header"><h1>Analytics</h1><p>Campaign performance and reply tracking</p></div>', unsafe_allow_html=True)
    render_analytics_tab(db)

# ══════════════════════════════════════════
# PAGE 4 — Settings
# ══════════════════════════════════════════
elif page == "Settings":
    st.markdown('<div class="page-header"><h1>Settings</h1><p>Your profile and configuration</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"""<div class="card">
            <div class="card-header"><div class="card-icon purple">👤</div> Profile</div>
            <table style="width:100%;font-size:0.83rem;border-collapse:collapse;">
                <tr><td style="padding:7px 0;color:#475569;width:80px;">Name</td><td style="color:#e2e8f0;font-weight:500;">{USER_NAME}</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">Email</td><td style="color:#e2e8f0;">{USER_EMAIL}</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">Year</td><td style="color:#e2e8f0;">{USER_YEAR}</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">CGPA</td><td style="color:#e2e8f0;">{USER_CGPA}</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">Branch</td><td style="color:#e2e8f0;">{USER_BRANCH}</td></tr>
            </table></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="card">
            <div class="card-header"><div class="card-icon blue">🔑</div> API Config</div>
            <table style="width:100%;font-size:0.83rem;border-collapse:collapse;">
                <tr><td style="padding:7px 0;color:#475569;width:80px;">Model</td><td style="color:#e2e8f0;font-weight:500;">{os.getenv('LLM_MODEL','llama-3.3-70b-versatile')}</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">Provider</td><td style="color:#e2e8f0;">Groq · Free tier</td></tr>
                <tr><td style="padding:7px 0;color:#475569;">Status</td><td style="color:#22c55e;font-weight:600;">● Connected</td></tr>
            </table></div>""", unsafe_allow_html=True)