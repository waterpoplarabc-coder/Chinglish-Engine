# Chinglish Generator

Transform English into Chinese-style English - Learn how Chinese people really think and speak!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/chinglish-generator)

## 🌟 Features

- 🎯 **27 Linguistic Rules**: Systematic transformation from English to Chinglish
- 📱 **PWA Support**: Install as native app on iOS/Android
- 🌐 **Mobile Optimized**: Responsive design for all screen sizes
- 🔧 **Configurable**: 5 levels of Chinglish intensity (L1-L5)
- 📖 **Explainable**: See which rules were applied

## 🚀 Quick Start

### Live Demo
Visit: [https://chinglish-generator.vercel.app](https://chinglish-generator.vercel.app)

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd web
npm install
npm run dev
```

## 📱 Install as App

1. Visit the website on your phone
2. Tap "Share" → "Add to Home Screen"
3. Use like a native app!

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite + PWA
- **Backend**: FastAPI + Python 3.12
- **Deployment**: Vercel (frontend) + Render (backend)

## 📊 Example

**Input**: "I want to go to China tomorrow."

**Output (L3)**: "Tomorrow I want go China."

**Applied Rules**:
- Time-first ordering
- Article omission
- Simplified verb tense

## 📝 API Usage

```bash
curl -X POST https://chinglish-api.onrender.com/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I want to go to China tomorrow.",
    "lang": "en",
    "level": 3,
    "domain": "default"
  }'
```

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new Chinglish rules
- Improve mobile experience
- Add more languages
- Report bugs

## 📄 License

MIT License - feel free to use for any purpose!

---

**Made with ❤️ for language enthusiasts worldwide**
