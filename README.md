# PromptDoctor

PromptDoctor is a **Streamlit prompt engineering lab** built to help learners practice prompt engineering through **progressive, exam-style challenges** rather than just reading prompt-writing guides.

Users write prompts, test them on realistic scenarios, and receive **structured AI feedback** (per-principle) before advancing.

---

## Tech stack

- **Python 3**
- **Streamlit** (UI)
- **OpenRouter** for LLM inference (runner + judge)
- **requests** (HTTP calls to OpenRouter)
- **python-dotenv** (`.env` support)

---

## What it does

PromptDoctor runs your prompt against a level’s **sample input** using the “student model”, then grades it with an **AI examiner** using level-based principles.

---

## Features

- Select a **domain** (Healthcare, Legal, Finance, Technology, Marketing, Education, Environmental, HR, Customer Support)
- Complete **5 challenges** per domain
- For each challenge, progress through **5 levels** (Basic → Robust)
- Your prompt is run against the level’s **sample input**
- An AI **examiner** grades your prompt and returns structured feedback as JSON
- You can only advance when you **pass all principles** for the current level

---

## How the app works (runtime flow)

### 1) UI + state (`app.py`)
- Users choose a domain from a dropdown.
- For a selected domain, the app loads the current challenge + level from `levels.py`.
- The prompt editor is shown with:
  - Level description + task
  - Sample input and expected output hints (via expanders)
  - “What the Examiner Checks” principles
- On submit:
  1. `run_prompt()` is called to execute the student prompt on the sample input.
  2. If no error, `grade_prompt()` is called to grade the student prompt.
  3. The verdict is rendered in the “Examiner Verdict” panel.
  4. If verdict is `pass`, the level is marked cleared and you can go to the next level/challenge.

Key note: progress is tracked in **`st.session_state`** (in-memory for the running server session).

### 2) Run the student prompt (`runner.py`)
- Uses OpenRouter with:
  - `STUDENT_MODEL = "openai/gpt-4o-mini"`
- Supports a `{input}` placeholder in the student prompt:
  - If `{input}` exists, it replaces it with the level’s sample input.
  - Otherwise, the student prompt is used as the **system** message and the sample input is sent as the **user** message.
- Returns the model’s text output.

### 3) Grade the prompt (`examiner.py`)
- Uses OpenRouter with:
  - `JUDGE_MODEL = "openai/gpt-4o-mini"` (pinned for consistent grading)
- Builds a large system prompt containing:
  - Domain name + level name
  - The **principles** for that level (from `levels.py`)
  - The sample input, expected output, example output
  - The student prompt and the student model output
- The judge is instructed to:
  - Reason internally in `<reasoning>...</reasoning>`
  - Output **ONLY raw JSON** matching an expected schema
- `examiner.py` attempts multiple strategies to extract JSON from the judge response.
- Enforcement rule: verdict is **`pass` only if all principles have `pass: true`**.

---

## Project structure

- `app.py`
  - Streamlit UI, styling, and orchestration
  - Manages session state and renders verdict + progress

- `runner.py`
  - Calls OpenRouter to run the student prompt against the level sample input

- `examiner.py`
  - Calls OpenRouter to grade the student prompt against level principles
  - Extracts and validates JSON verdicts

- `levels.py`
  - All domain/challenge/level definitions
  - `DOMAINS`: domain descriptions
  - `LEVEL_TEMPLATES`: common level principles + wording
  - `CHALLENGES`: per-domain 5 challenges, each with per-level sample input, expected output, and sometimes example output

- `bg.png`
  - Background image used in the UI

---

## Configuration

The app requires an OpenRouter API key.

1. Create a `.env` file in the project root.
2. Set:

```env
OPENROUTER_API_KEY=your-openrouter-api-key
```

Both `runner.py` and `examiner.py` read `OPENROUTER_API_KEY` via `dotenv`.

---

## Levels (what changes as you progress)

Each level corresponds to a prompt-writing technique and a set of principles the examiner checks:

1. **Basic**: Clear role + complete instruction + on-task conciseness
2. **Structured**: Explicit output format + valid JSON + field completeness
3. **Few-shot**: Relevant worked examples + coverage of tricky cases + consistency
4. **Reasoning**: Step-by-step reasoning + correct multi-step handling
5. **Robust**: Defensive handling (injection guard, noise tolerance, scope control)

---

## How to run

From the project directory:

```bash
streamlit run app.py
```

Then open the shown local URL in your browser.

---

## Development notes / troubleshooting

- If grading returns an `error` verdict, check:
  - Your `.env` `OPENROUTER_API_KEY`
  - Whether the judge response contained valid JSON
- If the run step returns an `ERROR: OPENROUTER_API_KEY not set...`, your key is missing.

---

## Extending the lab

To add a new domain or challenge:
- Edit `levels.py`:
  - Add to `DOMAINS`
  - Add a 5-item list under `CHALLENGES["Your Domain"]`
  - Provide per-level `sample_input`, `output_expectation`, and optional `example_output`
- No changes should be required in `app.py` unless you want UI adjustments.

