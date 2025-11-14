# 🤖 ZUS Coffee AI Chatbot

An intelligent FastAPI + React chatbot that answers questions about ZUS Coffee products and outlets using AI agents, RAG, and Text2SQL.

## ⚡ Quick Links

| Need | Resource | Time |
|------|----------|------|
| **Get it running** | [`QUICK_START_CARD.md`](QUICK_START_CARD.md) | 5 min |
| **Full setup guide** | [`README_COMPLETE.md`](README_COMPLETE.md) | 30 min |
| **API reference** | [`API_REFERENCE.md`](API_REFERENCE.md) | 10 min |
| **Frontend details** | [`frontend/README.md`](frontend/README.md) | 10 min |

---

## 🚀 Quick Start (3 Steps)

### Terminal 1: Start Backend

```bash
python main.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Start Frontend

```bash
cd frontend
npm install  # (only first time)
npm start
```

Wait for: Browser opens to <http://localhost:3000>

### Testing: Send a Message

Try these queries:

1. **Calculator**: "What is 150 times 12?"
2. **Product RAG**: "Tell me about the Black Sugar Latte"
3. **Outlets**: "Is there an outlet in Petaling Jaya?"

---

## 📚 Documentation

### Core Files

- **README_COMPLETE.md** - Comprehensive guide (architecture, setup, testing, troubleshooting)
- **QUICK_START_CARD.md** - 5-minute launch guide
- **API_REFERENCE.md** - Full API specification with examples
- **frontend/README.md** - React component architecture

### What Each Section Covers

| Document | Covers | Use When |
|----------|--------|----------|
| QUICK_START_CARD.md | Launch, quick tests | Starting fresh |
| README_COMPLETE.md | Full architecture, setup, testing, troubleshooting | Need detailed info |
| API_REFERENCE.md | All endpoints, request/response schemas, examples | Building integrations |
| frontend/README.md | React components, features, project structure | Frontend development |

---

## ✅ Checklist: Are You Ready?

**Before Running:**

- [ ] Python 3.9+ installed
- [ ] Node.js 14+ installed
- [ ] OpenAI API key in environment
- [ ] Two terminal windows open

**After Running Backend:**

- [ ] No errors in backend terminal
- [ ] Server says "Uvicorn running on <http://0.0.0.0:8000>"

**After Running Frontend:**

- [ ] No errors in frontend terminal
- [ ] Browser opens to <http://localhost:3000>
- [ ] Chat window is visible

**First Test:**

- [ ] Send: "What is 150 times 12?"
- [ ] See: "What is 150 times 12? is 1800"
- [ ] Tool badge appears: "Calculator"

---

## 🔧 Key Features

- **Multi-turn conversations** with session memory
- **Three intelligent tools**: Calculator, Product RAG, Outlet Text2SQL
- **Tool visualization** with colored badges
- **Persistent chat history** via localStorage
- **Error recovery** with clear messages
- **Responsive design** (desktop, tablet, mobile)

---

## 🆘 Troubleshooting

**Backend won't start?**
→ See `README_COMPLETE.md` → Troubleshooting

**Frontend won't compile?**
→ See `README_COMPLETE.md` → Troubleshooting

**Chat not responding?**
→ Check backend terminal for errors
→ Check browser console (F12)
→ Verify REACT_APP_BACKEND_URL in `frontend/.env`

**Specific error?**
→ Search `README_COMPLETE.md` for your error message

---

## 📊 System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.9+ |
| Node.js | 14+ |
| npm | 6+ |
| RAM | 4GB minimum |
| OpenAI API | Valid key required |

---

## 🚀 Next Steps

1. **Start both servers** (see Quick Start above)
2. **Test all three flows** (calculator, product, outlets)
3. **Read README_COMPLETE.md** for architecture details
4. **Check API_REFERENCE.md** for integration details

---

**Status**: ✅ Ready for Deployment
**Last Updated**: November 14, 2025
