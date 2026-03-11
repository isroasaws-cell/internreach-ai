import os
import json
import time
from openai import OpenAI
from src.rag.vector_store import retrieve_relevant_chunks
from dotenv import load_dotenv
load_dotenv()

# ── Client Setup ──────────────────────────────
client = OpenAI(
    api_key  = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

# ── Config ────────────────────────────────────
MODEL           = os.getenv("LLM_MODEL",       "meta-llama/llama-3.3-70b-instruct:free")
CANDIDATE_NAME  = os.getenv("CANDIDATE_NAME",  "Ashish Srivastava")
CANDIDATE_EMAIL = os.getenv("CANDIDATE_EMAIL", "ashish171200@gmail.com")


def generate_email(hr: dict, extra_instruction: str = "") -> dict:
    """
    Generate a personalized internship email using RAG context.
    Includes retry logic for rate limits and empty responses.
    """
    global MODEL  # ← declared at TOP of function, before any use

    # RAG — get relevant resume chunks
    query   = f"skills and projects relevant to {hr['domain']} internship at {hr['company']}"
    context = retrieve_relevant_chunks(query, k=3)

    prompt = f"""You are a professional email writer helping {CANDIDATE_NAME} apply for internships.

CANDIDATE DETAILS (use these exactly, never use placeholders):
- Full Name : {CANDIDATE_NAME}
- Email     : {CANDIDATE_EMAIL}

HR INFORMATION:
- HR Name   : {hr['hr_name']}
- Company   : {hr['company']}
- Domain    : {hr['domain']}

RELEVANT RESUME CONTEXT (reference these specifically):
{context}

{extra_instruction}

INSTRUCTIONS:
1. Write a personalized internship request email FROM {CANDIDATE_NAME} TO {hr['hr_name']}
2. ALWAYS sign as "{CANDIDATE_NAME}" — NEVER write [Your Name] or any placeholder
3. Mention at least 1-2 specific skills or projects from the resume context
4. Explain why {CANDIDATE_NAME} is interested in {hr['company']} and {hr['domain']}
5. Keep it 150-200 words, professional but warm tone
6. End with a clear call to action

Return ONLY valid JSON with exactly these two keys:
{{"subject": "email subject here", "body": "full email body here"}}"""

    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model           = MODEL,
                messages        = [{"role": "user", "content": prompt}],
                response_format = {"type": "json_object"},
                temperature     = 0.7,
                max_tokens      = 600
            )

            # Safely get content — handle NoneType
            if not response or not response.choices or len(response.choices) == 0:
                print(f"   ⚠️  No choices in response, retrying ({attempt}/{max_attempts})...")
                time.sleep(30)
                continue

            message = response.choices[0].message
            if not message or not message.content:
                print(f"   ⚠️  Empty message, retrying ({attempt}/{max_attempts})...")
                time.sleep(30)
                continue

            content = message.content.strip()

            # Strip markdown fences if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            if not content:
                print(f"   ⚠️  Empty content after stripping, retrying...")
                time.sleep(30)
                continue

            result = json.loads(content)

            # Validate keys
            if "subject" not in result or "body" not in result:
                print(f"   ⚠️  Missing subject/body, retrying...")
                time.sleep(10)
                continue

            # Fix any remaining placeholders
            result["body"]    = result["body"].replace("[Your Name]", CANDIDATE_NAME)
            result["subject"] = result["subject"].replace("[Your Name]", CANDIDATE_NAME)

            result["retrieved_context"] = context
            return result

        except Exception as e:
            error_str = str(e)

            if "429" in error_str:
                wait_time = attempt * 30  # 30s, 60s, 90s, 120s
                print(f"   ⚠️  Rate limited. Waiting {wait_time}s... ({attempt}/{max_attempts})")
                time.sleep(wait_time)
                continue

            elif "404" in error_str:
                print(f"   ❌ Model '{MODEL}' blocked. Switching to fallback...")
                MODEL = "mistralai/mistral-7b-instruct:free"
                time.sleep(10)
                continue

            elif "NoneType" in error_str or "subscriptable" in error_str:
                print(f"   ⚠️  Empty response (NoneType). Waiting 30s... ({attempt}/{max_attempts})")
                time.sleep(30)
                continue

            elif "JSONDecodeError" in error_str or "json" in error_str.lower():
                print(f"   ⚠️  JSON parse error, retrying...")
                time.sleep(10)
                continue

            else:
                print(f"   ❌ Unexpected error: {error_str}")
                raise Exception(f"LLM error: {error_str}")

    raise Exception(f"Failed after {max_attempts} attempts for {hr['company']}")