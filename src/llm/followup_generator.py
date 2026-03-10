import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

MODEL = "openai/gpt-4o-mini"

def generate_followup(record):
    prompt = f"""
Write a short professional follow-up email (80-100 words max).

Context:
- Original sent to: {record['hr_name']} at {record['company']}
- Sent on: {record['sent_at']}
- Original subject: {record['subject']}

Rules:
1. Reference the previous email politely
2. Express continued interest without being pushy
3. Ask if there is any update on internship opportunities
4. Warm, professional tone

Return ONLY JSON: {{"subject": "Re: {record['subject']}", "body": "..."}}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.6
    )
    return json.loads(response.choices[0].message.content)