# Chinglish Engine 🇨🇳↔🇬🇧

> A configurable, rule-driven engine that transforms English into **Chinese-influenced English (Chinglish)** — capturing how Chinese speakers actually think and speak.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/waterpoplarabc-coder/Chinglish-Engine)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/waterpoplarabc-coder/Chinglish-Engine)

---

## 🌟 What Is This?

Chinglish isn't "bad English" — it's **English processed through Chinese linguistic thinking**. When a Chinese speaker says:

> *"Tomorrow I want go China."*

They aren't making a grammar mistake. They're applying the Chinese sentence structure **"明天我要去中国"** (Time + Subject + Verb + Object) onto English words.

This engine **systematically reproduces that cognitive process** through 27+ linguistic rules organized in 6 layers, with **5 levels of intensity** (L1-L5) controllable by the user.

### Use Cases

- 🧪 **MT & LLM Robustness Evaluation** — Test how well machine translation and LLMs handle non-native input
- 📚 **Language Learning Research** — Study the systematic patterns of Chinese-English transfer
- 🎮 **Game/Story Localization** — Generate authentic Chinese-character dialogue
- 🤖 **Training Data Augmentation** — Create diverse Chinglish samples for model fine-tuning

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **27+ Linguistic Rules** | 6 cognitive/linguistic layers: Cognitive → Syntax → Lexical → Morphology → Rhetoric → Control |
| 🔧 **5 Intensity Levels** | L1 (subtle) → L5 (full Chinglish) with probabilistic rule activation |
| 📖 **Explainable** | Shows exactly which rules were applied and how |
| 📱 **PWA** | Install as native app on any device |
| 🌐 **Mobile Optimized** | Responsive design |
| 🔬 **Regression Test Suite** | Verify rule behavior across levels |

---

## 🚀 Quick Start

### Live Demo

👉 **[https://chinglish-generator.vercel.app](https://chinglish-generator.vercel.app)**

### Local Development

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend (in a new terminal)
cd web
npm install
npm run dev
```

Open **http://localhost:5173** (UI) or **http://localhost:8000/docs** (API docs).

---

## 🔧 Architecture

```
┌────────────────────────────────────────────────┐
│                   Rule Engine                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ L0: Cog  │  │ L1: Syn  │  │ L2: Lexical  │  │
│  │ Cause→So │  │ Time→Frt │  │ enter→input  │  │
│  │ If→Then  │  │ Topic-Abt│  │ impl→realize │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ L3: Morph│  │ L4: Rhet│  │ L5: Control  │  │
│  │ omission │  │ particle │  │ fallback     │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└────────────────────────────────────────────────┘
       ▲                                              ▲
       │  rulepacks/*.json (pack.v0.1, v0.2)         │
       │                                              │
  ┌────┴─────┐                                 ┌──────┴──────┐
  │  Backend  │  FastAPI + RewriteEngine        │   Frontend  │
  │  :8000    │  ←────────────────────────────→ │  :5173      │
  └──────────┘  /api/rewrite (JSON)             └─────────────┘
                                                    React + PWA
```

## 📝 API

```bash
curl -X POST http://localhost:8000/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I want to go to China tomorrow.",
    "lang": "en",
    "level": 3,
    "domain": "default",
    "explain": true
  }'
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | required | Input English text |
| `lang` | string | `"en"` | Language (only `en` supported) |
| `level` | int | `3` | Chinglish intensity 1-5 |
| `domain` | string | `"default"` | Domain weight profile |
| `explain` | bool | `false` | Return applied rules & steps |

### Example Response

```json
{
  "output": "Tomorrow I want go China.",
  "applied_rules": ["EN_ZH_SKELETON_REORDER_INTENT_TIME"],
  "steps": [
    {
      "rule_id": "EN_ZH_SKELETON_REORDER_INTENT_TIME",
      "before": "I want to go to China tomorrow.",
      "after": "Tomorrow I want go China."
    }
  ],
  "structure_type": "simple",
  "skeleton_template": "a"
}
```

### Level Examples

| Level | Input → Output |
|-------|----------------|
| **L1** | "I want to go to China tomorrow." → *no change* |
| **L2** | "I want to go to China tomorrow." → "In my opinion, I want to go to China tomorrow." |
| **L3** | "I want to go to China tomorrow." → "Tomorrow I want go China." |
| **L4** | "I want to go to China tomorrow." → "Tomorrow I want go China, then we can continue." |
| **L5** | "I want to go to China tomorrow." → "Actually, tomorrow I want go China, then we can continue." |

---

## 🧪 Regression Tests

```bash
cd eval
python run_regression.py
```

---

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite + PWA
- **Backend**: FastAPI + Python 3.12
- **Rules**: JSON-based rule packs (versioned, composable)
- **Deployment**: Vercel (frontend) + Render (backend)

---

## 📄 License

MIT License — free to use, modify, and share.

---

**Made with ❤️ for language geeks, NLP researchers, and curious minds worldwide.**
