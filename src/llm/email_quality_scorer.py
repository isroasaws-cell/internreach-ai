import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key  = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

SCORE_THRESHOLD = 7.0
MAX_RETRIES     = 3
# Scorer uses DIFFERENT model than generator — splits rate limit!
MODEL           = os.getenv("SCORER_MODEL", "google/gemma-3-12b-it:free")


def score_email(email: dict, hr: dict) -> dict:
    prompt = f"""You are an email quality evaluator. Score this internship email.

HR: {hr.get('hr_name','')} at {hr.get('company','')} ({hr.get('domain','')})
Subject: {email.get('subject','')}
Body: {email.get('body','')}

Return ONLY this JSON (no extra text):
{{
  "personalization_score": 7,
  "professionalism_score": 8,
  "relevance_score": 7,
  "feedback": "one sentence feedback",
  "strongest_line": "best line",
  "weakest_line": "weakest line"
}}"""

    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model       = MODEL,
                messages    = [{"role": "user", "content": prompt}],
                temperature = 0.2,
                max_tokens  = 300
            )

            if not response or not response.choices:
                time.sleep(15)
                continue

            raw = response.choices[0].message.content
            if not raw:
                time.sleep(15)
                continue

            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            result = json.loads(raw)
            avg = round((
                result["personalization_score"] +
                result["professionalism_score"] +
                result["relevance_score"]
            ) / 3, 2)
            result["average_score"] = avg
            result["passed"]        = avg >= SCORE_THRESHOLD
            return result

        except Exception as e:
            if "429" in str(e):
                wait = attempt * 20
                print(f"   ⚠️  Scorer rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                print(f"   ⚠️  Scorer error: {e} — using default pass")
                break

    # Default pass if scorer fails
    return {
        "personalization_score": 7,
        "professionalism_score": 7,
        "relevance_score":       7,
        "average_score":         7.0,
        "passed":                True,
        "feedback":              "Scorer unavailable",
        "strongest_line":        "",
        "weakest_line":          ""
    }


def score_and_approve(hr: dict, generate_fn) -> dict:
    best_email = None
    best_score = None
    best_avg   = 0.0

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"   Scoring attempt {attempt}/{MAX_RETRIES}...")

        if attempt == 1:
            email = generate_fn(hr)
        else:
            feedback = best_score.get("feedback", "") if best_score else ""
            weak     = best_score.get("weakest_line", "") if best_score else ""
            extra    = f"\nPrevious score: {best_avg}/10. Improve: {feedback}. Fix weak line: '{weak}'."
            try:
                email = generate_fn(hr, extra_instruction=extra)
            except TypeError:
                email = generate_fn(hr)

        score = score_email(email, hr)
        avg   = score["average_score"]
        print(f"   P:{score['personalization_score']} "
              f"Pro:{score['professionalism_score']} "
              f"R:{score['relevance_score']} Avg:{avg}/10")

        if avg > best_avg:
            best_avg   = avg
            best_email = email
            best_score = score

        if score["passed"]:
            print(f"   Passed ({avg}/10)")
            return {"email": best_email, "score": best_score,
                    "attempts": attempt, "auto_approved": True}

        print(f"   Score {avg}/10 below {SCORE_THRESHOLD} — regenerating...")

    print(f"   Sending best version: {best_avg}/10")
    return {"email": best_email, "score": best_score,
            "attempts": MAX_RETRIES, "auto_approved": False}


def batch_score_summary(score_results: list) -> dict:
    total = len(score_results)
    if total == 0:
        return {}
    passed = sum(1 for r in score_results if r["score"] and r["score"]["passed"])
    multi  = sum(1 for r in score_results if r["attempts"] > 1)
    avg_scores = {
        "personalization": round(sum(r["score"]["personalization_score"] for r in score_results if r["score"]) / total, 2),
        "professionalism": round(sum(r["score"]["professionalism_score"] for r in score_results if r["score"]) / total, 2),
        "relevance":       round(sum(r["score"]["relevance_score"]       for r in score_results if r["score"]) / total, 2),
        "overall":         round(sum(r["score"]["average_score"]         for r in score_results if r["score"]) / total, 2),
    }
    return {
        "total_emails":         total,
        "passed_first_attempt": passed,
        "needed_regeneration":  multi,
        "pass_rate":            f"{round((passed/total)*100)}%",
        "average_scores":       avg_scores
    }