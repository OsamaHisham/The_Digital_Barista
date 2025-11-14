# 🤖 ZUS Coffee AI Chatbot - Complete Setup & Architecture Guide

**A full-stack AI chatbot application built with React, FastAPI, LangChain, and OpenAI that handles product queries (RAG), outlet searches (Text2SQL), and calculations.**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Setup Instructions](#setup-instructions)
5. [API Specification](#api-specification)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [Key Features & Flows](#key-features--flows)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 14+
- OpenAI API key
- Ports 8000 & 3000 available

### 1️⃣ Backend (Terminal 1)
```bash
cd "C:\Users\..\TheDigital_Barista"

# Set API key (Windows)
setx OPENAI_API_KEY "your-api-key-here"

# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py
```

**Expected output:**
```
[OK] LLM and embeddings loaded successfully.
[OK] FAISS index loaded from faiss_index.
[OK] Text2SQL agent initialized for outlets.db.
Starting FastAPI server at http://localhost:8000
```

### 2️⃣ Frontend (Terminal 2)
```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm start
```

**Browser automatically opens:**
```
http://localhost:3000
```

### 3️⃣ Test It Out
- Query: `"What is 150 times 12?"`
- Expected: `"What is 150 times 12? is 1800"`

---

## 🏗️ System Architecture

### High-Level Design

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ZUS Coffee AI Chatbot                         │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
          ┌──────▼────────┐  ┌───▼──────┐  ┌────▼──────────┐
          │ React Frontend│  │ FastAPI  │  │  LangChain    │
          │ (Port 3000)   │  │Backend   │  │   Agent       │
          │               │  │(Port8000)│  │ (GPT-3.5)     │
          └──────┬────────┘  └───┬──────┘  └────┬──────────┘
                 │               │              │
                 │   HTTP/JSON   │              │
                 └───────────────┼──────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
          ┌─────────▼──┐  ┌──────▼────┐  ┌───▼───────┐
          │ RAG Tool   │  │ SQL Tool   │  │ Calculator│
          │ (FAISS)    │  │ (SQLite)   │  │ (Python)  │
          │ Embeddings │  │ Agents     │  │ Safe eval │
          └────────────┘  └────────────┘  └───────────┘
                    │            │
          ┌─────────▼──────────┬─▼──────────┐
          │                    │            │
      ┌───▼──────┐      ┌──────▼────┐  ┌───▼────────┐
      │products  │      │ outlets   │  │ (Memory)   │
      │.json     │      │ .db       │  │ Session    │
      │(FAISS)   │      │ (SQLite)  │  │ Store      │
      └──────────┘      └───────────┘  └────────────┘
```

### Data Flow: User Message → Response

```
1. USER SENDS MESSAGE
   └─> "Is there an outlet in Petaling Jaya?"
       │
2. REACT FRONTEND
   └─> POST /chat {session_id, message}
       │
3. FASTAPI BACKEND
   └─> Receives request
       ├─> Stores HumanMessage in session_store
       └─> Invokes LangChain agent
           │
4. AGENT PLANNING & EXECUTION
   └─> Analyzes message context
       ├─> Detects: "outlet query (yes/no question)"
       ├─> Decides: Use query_outlets_db tool
       │
5. TOOL EXECUTION
   └─> query_outlets_db("Is there an outlet in Petaling Jaya?")
       ├─> SQL Agent queries outlets.db
       ├─> Returns: [Outlet data for Petaling Jaya]
       │
6. POST-PROCESSING (Backend Smart Logic)
   └─> Detects yes/no outlet question pattern
       ├─> Extracts location: "Petaling Jaya"
       ├─> Checks if outlets exist: YES
       └─> Formats answer: "Yes! Which outlet are you referring to?"
           │
7. RESPONSE TO FRONTEND
   └─> ChatResponse {
         answer: "Yes! Which outlet are you referring to?",
         tool_used: "Outlet Text2SQL",
         intermediate_steps: [...]
       }
       │
8. FRONTEND RENDERING
   └─> Displays message with "Outlet Text2SQL" badge
       └─> Stores in localStorage
```

### Key Trade-offs & Design Decisions

| Decision | Trade-off | Rationale |
|----------|-----------|-----------|
| **In-Memory Session Store** | Not persistent across server restarts | Fast, simple, sufficient for single-user testing |
| **FAISS Vector Store** | Requires manual re-indexing | Fast retrieval, suitable for small product catalog |
| **SQLite Database** | Not production-scale | Simple, file-based, no server setup needed |
| **GPT-3.5-turbo** | Limited context window | Fast, cheap, good for conversational tasks |
| **Post-processing Logic in Backend** | Duplicate work vs. pure agent | Ensures consistent, user-friendly responses |
| **localStorage for Frontend** | Data cleared on cache clear | No backend database needed, good for demo |

---

## 📁 Project Structure

```
The_Digital_Barista/

🔧 BACKEND (FastAPI + LangChain)
├── main.py                    ⭐ FastAPI server - all endpoints
├── setup_db.py                Setup database & embeddings
├── ingest.py                  Data ingestion utilities
├── test_api.py                Backend unit tests
├── scrape_products.py         Product scraper
├── scrape_outlets.py          Outlet scraper
├── requirements.txt           ✨ Python dependencies (NEW)
├── .env                       Environment variables (git ignored)
├── .gitignore
├── outlets.json               Outlet data (72+ locations)
├── products.json              Product catalog
├── outlets.db                 SQLite database
└── faiss_index/
    └── index.faiss            Product embeddings

💻 frontend/ (React)
├── package.json               NPM dependencies
├── .env                       Environment config
├── .gitignore
├── public/
│   └── index.html             React root
└── src/
    ├── index.js               Entry point
    ├── index.css              Global styles
    ├── App.js                 Main component
    ├── App.css
    └── components/
        ├── ChatWindow.js      Chat (localStorage, error handling)
        ├── ChatWindow.css
        ├── Message.js         Message display
        ├── Message.css
        ├── ToolBadge.js       Tool visualization
        └── ToolBadge.css

📚 DOCUMENTATION
├── README.md                  Entry point & quick links
├── QUICK_START_CARD.md        5-minute launch guide
├── README_COMPLETE.md         This file (full guide)
├── API_REFERENCE.md           API endpoints & examples
└── DEPLOYMENT_READY.md        Deployment checklist

virtualEnv/                    Python env (not committed)
└── [Python packages]
```

---

## 🔧 Setup Instructions

### Step 1: Environment Setup

**Windows Command Prompt:**
```cmd
# Create project directory (if not exists)
cd ""C:\Users\..\The_Digital_Barista""

# Set OpenAI API key globally
setx OPENAI_API_KEY "sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# Verify it's set
echo %OPENAI_API_KEY%
```

### Step 2: Backend Setup

```cmd
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify database & FAISS index exist
python setup_db.py

# Expected output:
# [OK] Database initialized from outlets.json
# [OK] FAISS index created from products.json
```

**If setup_db.py fails:**
```cmd
# Manually create FAISS index and database
python
>>> from ingest import create_faiss_index, setup_database
>>> create_faiss_index()
>>> setup_database()
>>> exit()
```

### Step 3: Frontend Setup

```cmd
cd frontend

# 1. Install Node dependencies
npm install

# 2. Verify .env file
type .env
# Should show: REACT_APP_BACKEND_URL=http://localhost:8000

# If .env is missing, create it:
# (Windows - using PowerShell or create manually in editor)
```

### Step 4: Run Backend & Frontend

**Terminal 1 - Backend:**
```cmd
cd "C:\Users\..\The_Digital_Barista"
python main.py
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm start
```

**Browser opens automatically:**
```
http://localhost:3000
```

---

## 📡 API Specification

### 🏥 1. Health Check Endpoint

**Endpoint:** `GET /`

**Description:** Verify backend is running

**Request:**
```http
GET http://localhost:8000/
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Code:** `200 OK`

---

### 💬 2. Chat Endpoint (Main Conversation)

**Endpoint:** `POST /chat`

**Description:** Main chat endpoint. Maintains session memory, routes to appropriate tool, and returns formatted response.

**Request Body:**
```json
{
  "session_id": "session_1234567890_abc123def",
  "message": "What is 150 times 12?"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | ✅ Yes | Unique identifier for conversation session |
| `message` | string | ✅ Yes | User's natural language message |

**Response Body:**
```json
{
  "answer": "What is 150 times 12? is 1800",
  "tool_used": "Calculator",
  "intermediate_steps": [
    "Planner used: Calculator"
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Natural language response from agent/tool |
| `tool_used` | string \| null | Tool that was used: "Calculator", "Product RAG", "Outlet Text2SQL", or null |
| `intermediate_steps` | array | Debug info about agent's reasoning |

**Example Requests & Responses:**

**Example 1: Calculator Query**
```json
Request:
{
  "session_id": "user_session_123",
  "message": "What is 500 divided by 25?"
}

Response:
{
  "answer": "What is 500 divided by 25? is 20.0",
  "tool_used": "Calculator",
  "intermediate_steps": ["Planner used: Calculator"]
}
```

**Example 2: Product RAG Query**
```json
Request:
{
  "session_id": "user_session_123",
  "message": "Tell me about the Black Sugar Latte"
}

Response:
{
  "answer": "The Black Sugar Latte is a delicious beverage made with our signature espresso, steamed milk, and sweet brown sugar. Price: RM 8.50",
  "tool_used": "Product RAG",
  "intermediate_steps": ["Planner used: Product RAG"]
}
```

**Example 3: Outlet Yes/No Question**
```json
Request:
{
  "session_id": "user_session_123",
  "message": "Is there an outlet in Petaling Jaya?"
}

Response:
{
  "answer": "Yes! Which outlet are you referring to?",
  "tool_used": "Outlet Text2SQL",
  "intermediate_steps": ["Planner used: Outlet Text2SQL"]
}
```

**Example 4: Outlet List Query**
```json
Request:
{
  "session_id": "user_session_123",
  "message": "List all outlets in Kuala Lumpur"
}

Response:
{
  "answer": "ZUS Coffee – Bandar Menjalara Location: 37, Jalan 3/62a, Bandar Menjalara\nZUS Coffee – LSH33, Sentul Location: G-11, Ground Floor, Laman Seri Harmoni\nZUS Coffee – AEON BIG Wangsa Maju Location: Lot F1.11 (First Floor), AEON BIG...\n\n(Showing first 5 results of 8.)",
  "tool_used": "Outlet Text2SQL",
  "intermediate_steps": ["Planner used: Outlet Text2SQL"]
}
```

**Status Codes:**
| Code | Meaning | Example |
|------|---------|---------|
| `200` | Success | Normal response with answer |
| `503` | Service Unavailable | LLM not initialized, FAISS/DB not loaded |
| `500` | Server Error | Exception during processing |

---

### 🛍️ 3. Product Query Endpoint (Direct RAG)

**Endpoint:** `GET /products`

**Description:** Direct query to product knowledge base (RAG). Bypasses agent planning.

**Query Parameters:**
```http
GET http://localhost:8000/products?query=What%20is%20the%20price%20of%20the%20OG%20Cup%202.0?
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ Yes | Natural language product question |

**Response Body:**
```json
{
  "summary": "The OG Cup 2.0 is our signature reusable cup, made from durable stainless steel. Price: RM 25.00",
  "retrieved_sources": [
    "products.json"
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | AI-generated summary based on retrieved documents |
| `retrieved_sources` | array | Source files/metadata for retrieved products |

**Example Queries:**
```
GET /products?query=Tell%20me%20about%20espresso
GET /products?query=What%20products%20do%20you%20have?
GET /products?query=Price%20of%20cold%20brew?
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| `200` | Success |
| `422` | Missing required `query` parameter |
| `503` | RAG models not loaded (check API key & FAISS index) |
| `500` | Server error |

---

### 📍 4. Outlets Query Endpoint (Direct Text2SQL)

**Endpoint:** `GET /outlets`

**Description:** Direct query to outlets database using natural language. Converts to SQL and returns results.

**Query Parameters:**
```http
GET http://localhost:8000/outlets?query=Which%20outlets%20are%20in%20Shah%20Alam?
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ Yes | Natural language outlet question |

**Response Body:**
```json
{
  "query_result": "ZUS Coffee – Shah Alam Location: Lot 10.01...",
  "intermediate_steps": [
    "Text2SQL Agent ran on SQLDatabase tool to generate and execute an SQL query."
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `query_result` | string | Raw or formatted query results |
| `intermediate_steps` | array | Debug info about SQL generation |

**Example Queries:**
```
GET /outlets?query=Find%20outlets%20in%20Kuala%20Lumpur
GET /outlets?query=Which%20outlets%20have%20dine-in%20service?
GET /outlets?query=List%20all%20outlets
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| `200` | Success |
| `422` | Missing required `query` parameter |
| `503` | Text2SQL agent not loaded (check outlets.db) |
| `500` | SQL execution error |

---

## 🎨 Frontend Architecture

### Component Hierarchy

```
App
└── ChatWindow
    ├── Header (Chat Title + Clear History Button)
    ├── MessagesContainer
    │   ├── Message (bot, tool badge)
    │   ├── Message (user)
    │   └── ToolBadge (if tool was used)
    └── InputForm
        ├── Textarea (message input)
        └── Send Button
```

### Component Details

#### **App.js**
- Main React component
- Wraps ChatWindow
- Handles global styling

#### **ChatWindow.js**
- **State:**
  - `messages`: Array of message objects
  - `inputValue`: Current input text
  - `isLoading`: Sending/waiting state
  - `sessionId`: Unique session identifier
  - `lastToolUsed`: Last tool used (for display)

- **Key Functions:**
  - `handleSendMessage()`: Posts message to `/chat`, handles response
  - `handleReset()`: Clears localStorage, resets session
  - Auto-scroll to latest message

- **Features:**
  - Timeout: 30-second request timeout
  - Error handling: Clear error messages
  - localStorage persistence: Auto-saves history
  - `/reset` command: Clear chat history

#### **Message.js**
- Displays individual message
- Shows timestamp
- Different styling for user vs. bot

#### **ToolBadge.js**
- Shows which tool was used
- Visual indicators:
  - 🧮 Calculator
  - 📦 Product RAG
  - 📍 Outlet Text2SQL

### Data Flow in Frontend

```
User Types Message
       │
       ▼
handleSendMessage()
       │
       ├─> Check for /reset command
       │   └─> Clear history, new session
       │
       ├─> Validate input (not empty)
       │   └─> Add user message to state
       │
       ├─> Add "thinking" indicator message
       │   └─> Display in chat window
       │
       ├─> POST to /chat endpoint
       │   │
       │   ├─> AbortController timeout (30s)
       │   └─> Send: {session_id, message}
       │
       ├─> Receive response: {answer, tool_used}
       │   │
       │   ├─> Remove "thinking" message
       │   └─> Add bot response with tool badge
       │
       ├─> Save to localStorage
       │   └─> localStorage[STORAGE_KEY] = messages
       │
       └─> Display in ChatWindow

Error Handling:
  ├─> Timeout: "Request timeout (backend took too long)"
  ├─> Connection: "Cannot connect to backend at URL"
  └─> Other: "Error: [specific error message]"
```

### localStorage Schema

**Key:** `zus_chat_history`

**Value:**
```json
[
  {
    "id": "msg_1234567890_user",
    "type": "user",
    "content": "What is 150 times 12?",
    "timestamp": "2025-11-14T12:00:00Z"
  },
  {
    "id": "msg_1234567891_bot",
    "type": "bot",
    "content": "What is 150 times 12? is 1800",
    "toolUsed": "Calculator",
    "timestamp": "2025-11-14T12:00:05Z"
  }
]
```

**Key:** `zus_session_id`

**Value:**
```
session_1731608400123_abc123def
```

---

## ⚙️ Backend Architecture

### FastAPI Application Structure

```python
main.py
│
├── [IMPORTS & CONFIG]
│   ├── FastAPI, HTTPException, Query
│   ├── LangChain: create_agent, create_sql_agent
│   ├── OpenAI: ChatOpenAI, OpenAIEmbeddings
│   └── Pydantic: BaseModel for validation
│
├── [GLOBALS & INITIALIZATION]
│   ├── app = FastAPI(...)
│   ├── CORS middleware setup
│   ├── llm = ChatOpenAI()
│   ├── embeddings = OpenAIEmbeddings()
│   ├── retriever = FAISS.load_local()
│   ├── sql_agent = create_sql_agent()
│   └── session_store: Dict[str, List[BaseMessage]]
│
├── [AGENT TOOLS]
│   ├── safe_eval() → validates math expressions
│   ├── calculate() → executes math
│   ├── _retrieve_product_info() → calls RAG
│   ├── query_products_kb() → RAG tool
│   ├── _query_outlet_info() → calls SQL agent
│   └── query_outlets_db() → SQL tool
│
├── [API ENDPOINTS]
│   ├── GET  /                 (health check)
│   ├── GET  /products         (direct RAG query)
│   ├── GET  /outlets          (direct SQL query)
│   └── POST /chat             (main agent endpoint)
│
└── [MAIN]
    └── uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Tool Execution Flow

#### Tool 1: Calculator
```python
calculate(expression: str) -> str
├─> safe_eval(expression)
│   └─> eval() with restricted namespace (no builtins)
├─> Return: "Calculation result: {result}"
└─> Post-process: Extract numeric result
    └─> Format: "{user_question} is {result}"
```

**Examples:**
- Input: `"What is 150 * 12?"`
- Tool receives: `"150 * 12"`
- Output: `"What is 150 * 12? is 1800"`

#### Tool 2: Product RAG (Retrieval-Augmented Generation)
```python
query_products_kb(query: str) -> str
├─> _retrieve_product_info(query)
│   ├─> retriever.invoke(query)
│   │   └─> FAISS search (k=3 documents)
│   ├─> Concatenate top-3 documents
│   └─> LLM summarizes with prompt
├─> Return: "[PRODUCT INFORMATION RETRIEVED]\nProduct Information: {summary}"
└─> Post-process: Strip wrapper markers
    └─> Return cleaned summary
```

**FAISS Index:**
- Created from `products.json`
- Vector embeddings from OpenAI
- Retrieves top-3 most similar products
- LLM summarizes retrieved documents

**Example:**
- Input: `"Tell me about espresso"`
- FAISS retrieves: 3 espresso-related products
- LLM summarizes: "Espresso is a concentrated coffee shot..."
- Output: Clean summary

#### Tool 3: Outlet Text2SQL
```python
query_outlets_db(query: str) -> str
├─> _query_outlet_info(query)
│   ├─> sql_agent.invoke({input: query})
│   │   ├─> SQL Agent analyzes query
│   │   ├─> Generates SQL
│   │   └─> Executes on outlets.db
│   └─> Extract output
├─> Return: "[OUTLET DATABASE QUERY EXECUTED]\nOutlet Query Result: {result}"
└─> Post-process:
    ├─> Detect yes/no question pattern
    ├─> If yes/no: Return "Yes! Which outlet..." or "No, we don't have..."
    └─> If list: Parse & format outlets on separate lines
```

**Outlet Formatting Logic:**
- Detect question type (yes/no vs. list)
- Parse outlet data using regex patterns
- Limit to 5 results max
- Display each outlet on own line

**Example:**
- Input: `"Is there an outlet in Petaling Jaya?"`
- SQL returns: outlet data for Petaling Jaya
- Detection: yes/no question → outlets found
- Output: `"Yes! Which outlet are you referring to?"`

### Session Memory System

```python
session_store: Dict[str, List[BaseMessage]]
│
├─ session_id_1: [
│   HumanMessage(content="What is 150 * 12?"),
│   AIMessage(content="What is 150 * 12? is 1800"),
│   HumanMessage(content="SS2, whats the opening time?"),
│   AIMessage(content="The SS2 outlet opens at 9:00 AM...")
│ ]
│
└─ session_id_2: [...]
```

**Memory Lifespan:**
- Created: When user first sends message
- Updated: Every user/bot message pair
- Persisted: In-memory (server only)
- Cleared: On server restart

**Multi-turn Conversation Example:**
```
Turn 1:
  User: "List outlets in Petaling Jaya"
  Bot: "Yes! Which outlet are you referring to?"
  
Turn 2:
  User: "SS 2, whats the opening time?"
  Bot: (remembers from Turn 1 context)
       "The SS 2 outlet opens at 9:00 AM..."
       
Turn 3:
  User: "What products do you have there?"
  Bot: (still remembers Petaling Jaya context)
       "We have espresso, lattes, cold brew..."
```

### Post-Processing Logic

After tool execution, responses are cleaned up:

```python
_sanitize_tool_output(raw: str) -> str
├─> Remove wrapper markers:
│   ├─> [PRODUCT INFORMATION RETRIEVED]
│   ├─> Product Information:
│   ├─> [OUTLET DATABASE QUERY EXECUTED]
│   └─> Outlet Query Result:
│
├─> Remove polite prefixes:
│   ├─> "I apologize for the inconvenience. "
│   ├─> "I am sorry, "
│   └─> "Sorry, "
│
└─> Return: Clean output
```

**Calculator Post-Processing:**
```
Tool output: "Calculation result: 1800"
Last user message: "What is 150 * 12?"
Result: Extract numeric value (1800)
Format: "{user_message} is {result}"
Final: "What is 150 * 12? is 1800"
```

**Outlet Post-Processing:**
```
Tool output: "ZUS Coffee – Bandar Menjalara ... ZUS Coffee – LSH33..."
Question type: Detect if yes/no or list
If yes/no: "Yes! Which outlet are you referring to?"
If list: Parse, split, format each outlet on own line
```

---

## 🎯 Key Features & Flows

### Flow 1: Calculator Conversation
```
User Input: "What is 150 times 12?"
    │
    ▼
Backend Analysis:
  - Detects math question
  - Routes to Calculate tool
    │
    ▼
Tool Execution:
  - parse: 150 * 12
  - safe_eval: 1800
    │
    ▼
Post-Processing:
  - Extract numeric: 1800
  - Format: "What is 150 times 12? is 1800"
    │
    ▼
Response:
{
  answer: "What is 150 times 12? is 1800",
  tool_used: "Calculator",
  intermediate_steps: ["Planner used: Calculator"]
}
```

### Flow 2: Product Information (RAG)
```
User Input: "Tell me about the Black Sugar Latte"
    │
    ▼
Backend Analysis:
  - Detects product query
  - Routes to Product RAG tool
    │
    ▼
Tool Execution:
  - FAISS search: Find similar products (k=3)
  - LLM summarizes: Creates friendly description
    │
    ▼
Post-Processing:
  - Remove wrapper markers
  - Remove apology phrases
    │
    ▼
Response:
{
  answer: "The Black Sugar Latte is... [detailed description]",
  tool_used: "Product RAG",
  intermediate_steps: ["Planner used: Product RAG"]
}
```

### Flow 3: Outlet Yes/No Question
```
User Input: "Is there an outlet in Petaling Jaya?"
    │
    ▼
Backend Analysis:
  - Detects YES/NO pattern: "Is there an outlet in X?"
  - Routes to Outlet Text2SQL tool
    │
    ▼
Tool Execution:
  - SQL Agent generates: SELECT * FROM outlets WHERE location LIKE '%Petaling Jaya%'
  - Query executes: Returns outlet data
    │
    ▼
Post-Processing:
  - Detect question type: yes/no
  - Check results: outlets found = YES
  - Extract location: "Petaling Jaya"
  - Format: "Yes! Which outlet are you referring to?"
    │
    ▼
Response:
{
  answer: "Yes! Which outlet are you referring to?",
  tool_used: "Outlet Text2SQL",
  intermediate_steps: ["Planner used: Outlet Text2SQL"]
}
```

### Flow 4: Outlet List Request
```
User Input: "List outlets in Kuala Lumpur"
    │
    ▼
Backend Analysis:
  - Detects list request
  - Routes to Outlet Text2SQL tool
    │
    ▼
Tool Execution:
  - SQL Agent generates query
  - Returns: 8+ outlets in KL
    │
    ▼
Post-Processing:
  - Detect question type: LIST (not yes/no)
  - Parse outlet data using regex
  - Extract name + location for each
  - Format on separate lines
  - Limit to 5 results, note remaining
    │
    ▼
Response:
{
  answer: "ZUS Coffee – Bandar Menjalara Location: 37, Jalan 3/62a...\n
           ZUS Coffee – LSH33 Location: G-11, Ground Floor...\n
           ...\n(Showing first 5 results of 8.)",
  tool_used: "Outlet Text2SQL",
  intermediate_steps: ["Planner used: Outlet Text2SQL"]
}
```

### Flow 5: Multi-Turn Context Memory
```
Turn 1:
  User: "Is there an outlet in Petaling Jaya?"
  Bot: "Yes! Which outlet are you referring to?"
  ├─ Store in session_store[session_id]
  │
Turn 2:
  User: "SS 2, whats the opening time?"
  Bot: (Agent has full conversation context)
       "The SS2 outlet in Petaling Jaya opens at 9:00 AM"
  ├─ Store in session_store[session_id]
  │
Turn 3:
  User: "give me the FULL information on the LSH33 outlet"
  Bot: (Agent still remembers Petaling Jaya context)
       "ZUS Coffee – LSH33, Sentul Location: G-11, Ground Floor, 
        Laman Seri Harmoni (LSH33), No. 3, Jalan Batu Muda Tambahan 3, 
        Sentul, 51100 Kuala Lumpur, Wilayah Persekutuan Kuala Lumpur 
        Services: Dine-in, Takeaway"
```

---

## 🧪 Testing

### Automated Backend Tests

**Run all tests:**
```bash
pytest test_api.py -v
```

**Test Coverage:**
1. ✅ Health check
2. ✅ Products endpoint
3. ✅ Outlets endpoint
4. ✅ Calculator tool
5. ✅ Product RAG tool
6. ✅ Outlet Text2SQL tool
7. ✅ Session memory retention
8. ✅ Error handling & robustness

### Manual Frontend Tests

**Test Calculator:**
```
Query: "What is 150 times 12?"
Expected: "What is 150 times 12? is 1800"
Badge: Calculator
```

**Test Product RAG:**
```
Query: "Tell me about the Black Sugar Latte"
Expected: Product description, no wrapper text
Badge: Product RAG
```

**Test Outlets - Yes/No:**
```
Query: "Is there an outlet in Petaling Jaya?"
Expected: "Yes! Which outlet are you referring to?"
Badge: Outlet Text2SQL
```

**Test Outlets - List:**
```
Query: "List outlets in Kuala Lumpur"
Expected: Each outlet on separate line, up to 5 shown
Badge: Outlet Text2SQL
```

**Test Memory:**
```
Turn 1: "Is there an outlet in Petaling Jaya?"
Turn 2: "SS 2, whats the opening time?"
Expected: Bot remembers context from Turn 1
```

**Test /reset Command:**
```
Type: /reset
Expected: Chat history cleared, new session ID
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue:** `[ERROR] Error initializing OpenAI: Connection error`

**Solution:**
```bash
# 1. Verify API key is set
echo %OPENAI_API_KEY%

# 2. Test OpenAI connection
python -c "from openai import OpenAI; print('OK')"

# 3. If fails, reset API key
setx OPENAI_API_KEY "sk-xxxxxxxxxxxxxxxx"

# 4. Restart terminal & run main.py
```

**Issue:** `[WARN] FAISS index not found at faiss_index.`

**Solution:**
```bash
# Regenerate FAISS index
python setup_db.py

# Or manually:
python
>>> from ingest import create_faiss_index
>>> create_faiss_index()
>>> exit()
```

**Issue:** `[WARN] outlets.db not found`

**Solution:**
```bash
# Regenerate database
python setup_db.py

# Or manually:
python
>>> from ingest import setup_database
>>> setup_database()
>>> exit()
```

### Frontend Issues

**Issue:** `Error: Cannot connect to backend at http://localhost:8000`

**Solution:**
1. Verify backend is running: `python main.py`
2. Check port 8000 is open: `netstat -an | findstr :8000` (Windows)
3. Verify .env file: `cd frontend && type .env`
4. Restart React: Ctrl+C, then `npm start`

**Issue:** Messages are truncated or cut off

**Solution:**
- This was fixed in recent update
- Make sure main.py is latest version
- Clear browser cache: Ctrl+Shift+Delete

**Issue:** /reset command doesn't work

**Solution:**
```
1. Type exactly: /reset (lowercase)
2. Press Enter
3. Click "Clear History" button if above doesn't work
```

---

## 📚 Documentation Map

```
Start Here?
    │
    ├─ "I want it running NOW"
    │   └─> QUICK_START_CARD.md (5 min)
    │
    ├─ "I want full understanding"
    │   └─> README_COMPLETE.md (this file, 20 min)
    │
    ├─ "I want detailed setup"
    │   └─> SETUP_GUIDE.md (30 min)
    │
    ├─ "I want to test everything"
    │   └─> TESTING_CHECKLIST.md (30 min)
    │
    ├─ "Something's broken"
    │   └─> Troubleshooting section above
    │
    └─ "I want API reference"
        └─> API Specification section above
```

---

## 🎓 Summary

**What You Have:**
- ✅ Full-stack AI chatbot (React + FastAPI + LangChain)
- ✅ Three AI tools: Calculator, Product RAG, Outlet Text2SQL
- ✅ Session memory (multi-turn conversations)
- ✅ Persistent chat history (localStorage)
- ✅ Smart response formatting
- ✅ Comprehensive documentation

**Key Technologies:**
- Backend: Python, FastAPI, LangChain, OpenAI GPT-3.5
- Frontend: React 18, JavaScript, CSS
- Data: FAISS (embeddings), SQLite (database)
- Memory: In-memory session store, browser localStorage

**Quick Test:**
```bash
# Terminal 1
python main.py

# Terminal 2
cd frontend && npm start

# Browser
http://localhost:3000

# Try: "What is 150 times 12?"
```

---

**Documentation Created:** November 14, 2025
**Last Updated:** November 14, 2025
**Status:**  Production Ready for Testing
