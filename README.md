# 🩹 PromptDoctor

**PromptDoctor** is a **Streamlit-based Prompt Engineering Lab** designed to help learners practice prompt engineering through **progressive, exam-style challenges** instead of just reading prompt-writing guides.

Users write prompts, test them on realistic scenarios, and receive **AI-generated structured feedback** before advancing to the next level.

---

# 🚀 Tech Stack

* 🐍 Python 3
* 🎨 Streamlit (UI)
* 🤖 OpenRouter (LLM Inference)
* 🌐 Requests (HTTP API Calls)
* 🔐 python-dotenv (.env support)

---

# ✨ Features

* 📚 Practice across **9 domains**

  * Healthcare
  * Legal
  * Finance
  * Technology
  * Marketing
  * Education
  * Environmental
  * HR
  * Customer Support
* 🎯 Complete **5 challenges** per domain
* 📈 Progress through **5 prompt engineering levels**

  * Basic
  * Structured
  * Few-shot
  * Reasoning
  * Robust
* 🤖 Execute prompts using an AI student model
* 🩺 Receive detailed feedback from an AI examiner
* ✅ Advance only after passing every grading principle

---

# ⚙️ How It Works

### 1️⃣ Write a Prompt

Choose a domain and complete the current challenge by writing your own prompt.

### 2️⃣ Run the Prompt

Your prompt is executed using the **Student Model** against a predefined sample input.

### 3️⃣ AI Evaluation

The **AI Examiner** evaluates your prompt based on the principles of the current level.

### 4️⃣ Receive Feedback

A structured JSON verdict is generated with:

* ✅ Passed principles
* ❌ Failed principles
* 💡 Suggestions for improvement

### 5️⃣ Progress

Successfully passing all principles unlocks the next level or challenge.

---

# 📂 Project Structure

```text
PromptDoctor/
│── app.py              # Streamlit UI
│── runner.py           # Executes student prompts
│── examiner.py         # AI grading system
│── levels.py           # Domains, challenges and levels
│── bg.png              # Background image
│── README.md
```

---

# 🏗️ Runtime Flow

```text
User Prompt
      │
      ▼
 Student Model
      │
      ▼
 Generated Output
      │
      ▼
 AI Examiner
      │
      ▼
 JSON Verdict
      │
      ▼
 Progress Update
```

---

# 🎓 Prompt Engineering Levels

| Level         | Focus                     |
| ------------- | ------------------------- |
| 🟢 Basic      | Clear role & instructions |
| 🔵 Structured | Output formatting & JSON  |
| 🟡 Few-shot   | Examples & consistency    |
| 🟠 Reasoning  | Multi-step reasoning      |
| 🔴 Robust     | Defensive prompting       |

---

# 🔑 Configuration

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your-openrouter-api-key
```

Both **runner.py** and **examiner.py** automatically load the API key using **python-dotenv**.

---

# ▶️ Running the Project

```bash
streamlit run app.py
```

Then open the local URL displayed in your terminal.

---

# 🛠️ Troubleshooting

If the application does not work:

* ✔️ Verify your OpenRouter API key.
* ✔️ Ensure `.env` is correctly configured.
* ✔️ Check your internet connection.
* ✔️ If grading fails, verify that the judge model returned valid JSON.

---

# 📈 Future Improvements

* 💾 Save user progress permanently
* 🏆 Leaderboards
* 📊 Progress analytics
* 🌍 More domains and challenges
* 🎨 Improved UI/UX
* 👤 User authentication

---

# 📄 License

This project was developed as a **Mini Project** for learning and practicing **Prompt Engineering** using Large Language Models.
