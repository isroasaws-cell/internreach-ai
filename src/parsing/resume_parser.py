import fitz
import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

MODEL = "openai/gpt-4o-mini"

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "".join([page.get_text("text") for page in doc]).strip()

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_resume_sections(raw_text):
    prompt = f"""
You are a resume parser. Extract structured data from this resume.
Return ONLY a JSON object with these keys:
- name, email, phone
- skills (list of strings)
- education (list of dicts: degree, institution, year)
- experience (list of dicts: role, company, duration, description)
- projects (list of dicts: name, tech_stack, description)
- achievements (list of strings)

Resume text:
{raw_text[:4000]}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def parse_resume(path):
    if path.endswith(".pdf"):
        raw = extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        raw = extract_text_from_docx(path)
    else:
        raise ValueError("Use PDF or DOCX only.")
    sections = extract_resume_sections(raw)
    sections["raw_text"] = raw
    return sections