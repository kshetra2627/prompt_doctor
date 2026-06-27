"""Examiner — the prompt that grades prompts. You build this."""

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Pin a capable judge model so grading stays consistent
JUDGE_MODEL = "openai/gpt-4o-mini"

EXAMINER_SYSTEM_TEMPLATE = """
You are the Examiner: a supportive, encouraging prompt-engineering coach.

DOMAIN: {domain_name}
LEVEL {level}: {level_name}

Grade STUDENT_PROMPT for this domain and level.
Judge ONLY these principles for this level:

{principles_text}

The student's prompt was used to process this SAMPLE INPUT:
---BEGIN SAMPLE INPUT---
{sample_input}
---END SAMPLE INPUT---

The EXPECTED OUTPUT for this level is:
---BEGIN EXPECTED OUTPUT---
{output_expectation}
---END EXPECTED OUTPUT---

A concrete EXAMPLE of what a passing output looks like for this level:
---BEGIN EXAMPLE OUTPUT---
{example_output}
---END EXAMPLE OUTPUT---

The model's actual output (produced by running the student's prompt on the sample input) was:
---BEGIN MODEL OUTPUT---
{model_output}
---END MODEL OUTPUT---

Obey these rules:
1. Be GENEROUS and ENCOURAGING. The student is learning. If the prompt shows a reasonable attempt at following the principles, mark them as PASS.
2. Judge against the principles in your OWN words — be specific. Don't just restate the principle.
3. For ANY failed principles, you may quote a weak phrase or name what's missing, but keep feedback constructive.
4. NEVER write or rewrite the student's prompt. Suggest improvements without giving exact fixes.
5. Compare the actual model output against the example output to assess quality, but be reasonable — exact matches aren't required.
6. CRITICAL: Set verdict to "pass" ONLY if ALL principles have "pass": true. If even one principle fails, set verdict to "revise".
7. Reason step by step inside <reasoning></reasoning> tags, THEN output ONLY the JSON verdict.

STUDENT_PROMPT:
---BEGIN STUDENT PROMPT---
{student_prompt}
---END STUDENT PROMPT---

CRITICAL: After your <reasoning> section, output ONLY a raw JSON object. No markdown code blocks, no backticks, no "```json" or "```" markers around the JSON. Just start with {{ and end with }}. The JSON must match this exact schema:
{{
  "level": {level},
  "principles": [
    {{
      "name": "principle_name",
      "label": "Principle Label",
      "pass": true,
      "weakness": "",
      "question": ""
    }}
  ],
  "ran_ok": true,
  "verdict": "pass" or "revise"
}}
"""


def grade_prompt(
    domain_name: str,
    level_num: int,
    level_name: str,
    principles_text: str,
    output_expectation: str,
    example_output: str,
    student_prompt: str,
    sample_input: str,
    model_output: str,
) -> dict:
    """
    Send the examiner system prompt to the judge model and parse the JSON verdict.
    Returns a dict with keys: level, principles, ran_ok, verdict.
    Falls back to a default "error" verdict if parsing fails.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key-here":
        return {
            "level": level_num,
            "principles": [
                {
                    "name": "api_key",
                    "pass": False,
                    "weakness": "No API key configured in .env",
                    "question": "Have you added your OpenRouter API key to the .env file?",
                }
            ],
            "ran_ok": False,
            "verdict": "error",
        }

    system_prompt = EXAMINER_SYSTEM_TEMPLATE.format(
        domain_name=domain_name,
        level=level_num,
        level_name=level_name,
        principles_text=principles_text,
        output_expectation=output_expectation,
        example_output=example_output,
        student_prompt=student_prompt,
        sample_input=sample_input,
        model_output=model_output,
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Please grade the student's prompt for {domain_name} Level {level_num} ({level_name}).",
            },
        ],
        "temperature": 0.1,  # Low temp for consistent grading
        "max_tokens": 2048,
    }

    try:
        response = requests.post(
            OPENROUTER_URL, headers=headers, json=payload, timeout=120
        )
        response.raise_for_status()
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]

        # Extract JSON from the response
        verdict = _extract_json(raw_content)

        # Validate and enforce all-pass rule
        if verdict and "principles" in verdict and "verdict" in verdict:
            verdict["level"] = level_num
            if "ran_ok" not in verdict:
                verdict["ran_ok"] = True
            # Enforce that verdict is "pass" only if all principles are passing
            if verdict.get("verdict") == "pass":
                all_pass = all(p.get("pass", False) for p in verdict.get("principles", []))
                if not all_pass:
                    verdict["verdict"] = "revise"
            return verdict

        # Fallback: parse failed — include raw response for debugging
        return _fallback_verdict(level_num, raw_content)

    except Exception as e:
        return _fallback_verdict(level_num, f"Error during grading: {str(e)}")


def _extract_json(text: str) -> dict | None:
    """Extract JSON from text using multiple strategies."""
    if not text:
        return None

    # Strategy 1: Find JSON inside markdown code blocks (```json ... ``` or ``` ... ```)
    patterns = [
        r"```(?:json)?\s*\n?(\{.*?\})\n?\s*```",  # ```json ... ```
        r"```(?:json)?\s*(\{.*?\})\s*```",          # ```json{...}```
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

    # Strategy 2: Find JSON after </reasoning> tag
    match = re.search(r"</reasoning>\s*(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find the outermost JSON object (from first { to last })
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        candidate = text[brace_start : brace_end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try to fix common JSON issues and parse again
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        candidate = text[brace_start : brace_end + 1]
        try:
            fixed = re.sub(r"'([^']+)'", r'"\1"', candidate)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    return None


def _fallback_verdict(level_num: int, raw_text: str) -> dict:
    """Return a safe fallback verdict when parsing fails, including raw response."""
    return {
        "level": level_num,
        "principles": [
            {
                "name": "parsing",
                "pass": False,
                "weakness": "Could not parse the examiner's verdict. The judge model returned unexpected output.",
                "question": "Check the raw response below — the model may have returned malformed JSON.",
            }
        ],
        "ran_ok": False,
        "verdict": "error",
        "raw_response": raw_text[:1000] if raw_text else "No response",
    }