import fitz
import os
import json
import re
from docx import Document
from dotenv import load_dotenv
load_dotenv()


def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "".join([page.get_text("text") for page in doc]).strip()


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_resume_sections_local(raw_text: str) -> dict:
    """
    Extract resume sections using regex/heuristics.
    No LLM needed — works offline, zero API cost, zero rate limits.
    """
    text = raw_text
    lines = text.split("\n")

    # ── Name ──────────────────────────────────────────
    name = ""
    for line in lines[:10]:
        line = line.strip()
        if line and len(line.split()) in [2, 3, 4] and not any(c.isdigit() for c in line):
            if not any(kw in line.lower() for kw in ["resume", "cv", "email", "phone", "address"]):
                name = line
                break

    # ── Email ─────────────────────────────────────────
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else ""

    # ── Phone ─────────────────────────────────────────
    phone_match = re.search(r'(\+?\d[\d\s\-().]{8,15}\d)', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # ── Skills ────────────────────────────────────────
    skill_keywords = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "LLM",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV",
        "Data Structures", "Algorithms", "SQL", "MySQL", "PostgreSQL", "MongoDB",
        "React", "Node.js", "FastAPI", "Flask", "Django", "REST API",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "Linux",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
        "FAISS", "LangChain", "RAG", "Streamlit",
        "Satellite Data", "Remote Sensing", "Threshold-based Filtering",
        "Data Analysis", "Data Science", "Statistics", "Research"
    ]
    skills = [s for s in skill_keywords if s.lower() in text.lower()]

    # ── Projects ──────────────────────────────────────
    projects = []
    in_projects = False
    proj_lines = []
    for line in lines:
        ll = line.lower().strip()
        if any(m in ll for m in ["project", "projects"]) and len(line.strip()) < 30:
            in_projects = True
            continue
        if in_projects:
            if any(s in ll for s in ["experience", "education", "achievement", "certification", "skill"]) and len(line.strip()) < 30:
                break
            if line.strip():
                proj_lines.append(line.strip())

    current = []
    for line in proj_lines[:20]:
        if line and (line[0].isupper() or line.startswith(("-", "•", "●"))):
            if current:
                projects.append({"name": current[0].strip("•-–● "), "tech_stack": "", "description": " ".join(current[1:])[:200]})
            current = [line]
        else:
            current.append(line)
    if current:
        projects.append({"name": current[0].strip("•-–● "), "tech_stack": "", "description": " ".join(current[1:])[:200]})

    # ── Education ─────────────────────────────────────
    education = []
    edu_kw = ["b.tech", "btech", "b.e", "m.tech", "bachelor", "master", "b.sc", "m.sc", "phd", "university", "college", "institute", "iit", "nit"]
    for line in lines:
        if any(k in line.lower() for k in edu_kw) and len(line.strip()) > 5:
            education.append({"degree": line.strip()[:100], "institution": "", "year": ""})
            if len(education) >= 3:
                break

    # ── Experience ────────────────────────────────────
    experience = []
    exp_kw = ["intern", "engineer", "developer", "analyst", "researcher", "assistant", "trainee"]
    for line in lines:
        if any(k in line.lower() for k in exp_kw) and len(line.strip()) > 10:
            experience.append({"role": line.strip()[:100], "company": "", "duration": "", "description": ""})
            if len(experience) >= 5:
                break

    return {
        "name":         name or os.getenv("CANDIDATE_NAME", "Ashish Srivastava"),
        "email":        email or os.getenv("CANDIDATE_EMAIL", "ashish171200@gmail.com"),
        "phone":        phone,
        "skills":       skills if skills else ["Python", "Machine Learning"],
        "education":    education,
        "experience":   experience,
        "projects":     projects if projects else [{"name": "Project", "tech_stack": "", "description": ""}],
        "achievements": []
    }


def parse_resume(path: str) -> dict:
    if path.endswith(".pdf"):
        raw = extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        raw = extract_text_from_docx(path)
    else:
        raise ValueError("Use PDF or DOCX only.")

    sections = extract_resume_sections_local(raw)
    sections["raw_text"] = raw
    return sections