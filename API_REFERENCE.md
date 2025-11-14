# 📡 ZUS Coffee AI Chatbot - API Reference & Integration Guide

**Complete API specification for backend endpoints, request/response schemas, and integration examples.**

---

## 📑 Quick Reference

| Endpoint | Method | Purpose | Query Params | Auth |
|----------|--------|---------|--------------|------|
| `/` | GET | Health check | - | None |
| `/chat` | POST | Main conversation (with agent) | - | None |
| `/products` | GET | Direct RAG query | `query` | None |
| `/outlets` | GET | Direct SQL query | `query` | None |

**Base URL:** `http://localhost:8000`

---

## 🏥 1. Health Check

### Endpoint
```
GET /
```

### Purpose
Verify that the FastAPI backend is running and all systems are initialized.

### Request
```bash
curl http://localhost:8000/
```

### Response
```json
{
  "status": "ok"
}
```

### Status Code
- **200 OK** - Backend is running

### Use Case
- Verify backend availability before making requests
- Debugging connection issues
- CI/CD health checks

### Example (Python)
```python
import requests

response = requests.get("http://localhost:8000/")
if response.status_code == 200:
    print("✅ Backend is healthy")
else:
    print("❌ Backend is down")
```

---

## 💬 2. Chat Endpoint (Main Agent)

### Endpoint
```
POST /chat
```

### Purpose
Main conversation endpoint. Maintains session memory, routes to the appropriate AI tool (Calculator, RAG, or Text2SQL), and returns a formatted response.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body Schema:**
```json
{
  "session_id": "string (required)",
  "message": "string (required)"
}
```

**Parameters:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `session_id` | string | ✅ | Unique session identifier (create once per user) | `"session_1234567890_abc"` |
| `message` | string | ✅ | User's natural language input | `"What is 150 times 12?"` |

### Response

**Success Response (200 OK):**
```json
{
  "answer": "string",
  "tool_used": "string | null",
  "intermediate_steps": ["string"]
}
```

**Response Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `answer` | string | Natural language response from agent or tool | `"What is 150 times 12? is 1800"` |
| `tool_used` | string or null | Which tool was used: `"Calculator"`, `"Product RAG"`, `"Outlet Text2SQL"`, or `null` if no tool | `"Calculator"` |
| `intermediate_steps` | array | Debug/reasoning steps (for logging) | `["Planner used: Calculator"]` |

### Error Responses

**503 Service Unavailable:**
```json
{
  "detail": "LLM or Agent not initialized."
}
```
→ Cause: Backend not fully initialized, check API key and dependencies

**500 Internal Server Error:**
```json
{
  "detail": "I am very sorry, I encountered a critical error while trying to process your request. Please try again. Error: [error_details]"
}
```
→ Cause: Exception during message processing

### Examples

#### Example 1: Calculator Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "What is 500 divided by 25?"
  }'
```

**Response:**
```json
{
  "answer": "What is 500 divided by 25? is 20.0",
  "tool_used": "Calculator",
  "intermediate_steps": ["Planner used: Calculator"]
}
```

#### Example 2: Product Information (RAG)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "Tell me about the Black Sugar Latte"
  }'
```

**Response:**
```json
{
  "answer": "The Black Sugar Latte is a delicious beverage made with our signature espresso, steamed milk, and sweet brown sugar. Price: RM 8.50. It's perfect for those who enjoy a touch of sweetness in their coffee.",
  "tool_used": "Product RAG",
  "intermediate_steps": ["Planner used: Product RAG"]
}
```

#### Example 3: Outlet Yes/No Question
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "Is there an outlet in Petaling Jaya?"
  }'
```

**Response:**
```json
{
  "answer": "Yes! Which outlet are you referring to?",
  "tool_used": "Outlet Text2SQL",
  "intermediate_steps": ["Planner used: Outlet Text2SQL"]
}
```

#### Example 4: Outlet List Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "List all outlets in Kuala Lumpur"
  }'
```

**Response:**
```json
{
  "answer": "ZUS Coffee – Bandar Menjalara Location: 37, Jalan 3/62a, Bandar Menjalara, 52200 Kuala Lumpur\nZUS Coffee – LSH33, Sentul Location: G-11, Ground Floor, Laman Seri Harmoni (LSH33), No. 3, Jalan Batu Muda Tambahan 3\nZUS Coffee – AEON BIG Wangsa Maju Location: Lot F1.11 (First Floor), AEON BIG Wangsa Maju\nZUS Coffee – Cheras Business Centre Location: No 6 Jalan 5/101C, Cheras Business Centre\nZUS Coffee – Bandar Damai Perdana, Cheras Location: No 19G (Ground Floor), Jalan Damai Perdana\n\n(Showing first 5 results of 8.)",
  "tool_used": "Outlet Text2SQL",
  "intermediate_steps": ["Planner used: Outlet Text2SQL"]
}
```

#### Example 5: Multi-turn Conversation (Session Memory)
```bash
# Turn 1: User asks for outlets
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "Is there an outlet in Petaling Jaya?"
  }'

# Response:
# {"answer": "Yes! Which outlet are you referring to?", ...}

# Turn 2: User follows up (backend remembers context)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_session_123",
    "message": "SS 2, whats the opening time?"
  }'

# Response:
# {"answer": "The SS 2 outlet opens at 9:00 AM", ...}
```

### Python Integration Example

```python
import requests
import json

class ZUSChatbot:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.session_id = f"session_{int(time.time())}"
    
    def chat(self, message):
        """Send a message and get response from chatbot"""
        url = f"{self.backend_url}/chat"
        payload = {
            "session_id": self.session_id,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend"}
        except Exception as e:
            return {"error": str(e)}

# Usage
bot = ZUSChatbot()

# Calculator
result = bot.chat("What is 150 times 12?")
print(result["answer"])  # "What is 150 times 12? is 1800"

# Product info
result = bot.chat("Tell me about espresso")
print(result["answer"])  # "Espresso is..."

# Outlet query
result = bot.chat("Is there an outlet in Shah Alam?")
print(result["answer"])  # "Yes! Which outlet are you referring to?"
```

### JavaScript/Fetch Integration

```javascript
class ZUSChatbot {
  constructor(backendUrl = "http://localhost:8000") {
    this.backendUrl = backendUrl;
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async chat(message) {
    const url = `${this.backendUrl}/chat`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          message: message
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  }
}

// Usage
const bot = new ZUSChatbot();

// Send message
const result = await bot.chat("What is 150 times 12?");
console.log(result.answer);  // "What is 150 times 12? is 1800"
```

---

## 🛍️ 3. Products Endpoint (Direct RAG)

### Endpoint
```
GET /products
```

### Purpose
Direct query to the product knowledge base using Retrieval-Augmented Generation (RAG). Bypasses agent planning and goes directly to RAG tool.

### Request

**Query Parameters:**

| Param | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `query` | string | ✅ | Natural language product question | `"What is the price of espresso?"` |

**Examples:**
```
GET /products?query=What%20is%20the%20price%20of%20the%20OG%20Cup%202.0?
GET /products?query=Tell%20me%20about%20espresso
GET /products?query=What%20products%20do%20you%20have?
```

### Response

**Success Response (200 OK):**
```json
{
  "summary": "string",
  "retrieved_sources": ["string"]
}
```

**Response Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `summary` | string | AI-generated summary based on FAISS retrieval | `"The OG Cup 2.0 is our signature reusable cup, made from durable stainless steel. Price: RM 25.00"` |
| `retrieved_sources` | array | Source files/metadata | `["products.json"]` |

### Error Responses

**422 Unprocessable Entity (Missing query):**
```json
{
  "detail": [
    {
      "loc": ["query_params", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Server-side RAG models not loaded. Check API key and FAISS index."
}
```

**500 Server Error:**
```json
{
  "detail": "Error retrieving product information: [error_details]"
}
```

### Examples

#### Example: Direct Product Query
```bash
curl "http://localhost:8000/products?query=What%20is%20the%20price%20of%20espresso?"
```

**Response:**
```json
{
  "summary": "Our espresso shot is made from freshly roasted beans using our signature extraction process. Price: RM 5.50 for a single shot, RM 9.00 for a double shot.",
  "retrieved_sources": ["products.json"]
}
```

### Python Integration

```python
import requests

response = requests.get("http://localhost:8000/products", params={
    "query": "What is the price of the Black Sugar Latte?"
})

if response.status_code == 200:
    data = response.json()
    print("Summary:", data["summary"])
    print("Sources:", data["retrieved_sources"])
else:
    print("Error:", response.json())
```

---

## 📍 4. Outlets Endpoint (Direct Text2SQL)

### Endpoint
```
GET /outlets
```

### Purpose
Direct query to the outlets database using natural language. Text2SQL agent converts natural language to SQL, executes on SQLite, and returns results.

### Request

**Query Parameters:**

| Param | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `query` | string | ✅ | Natural language outlet question | `"Which outlets are in Shah Alam?"` |

**Examples:**
```
GET /outlets?query=Which%20outlets%20are%20in%20Shah%20Alam?
GET /outlets?query=Find%20outlets%20with%20dine-in%20service
GET /outlets?query=List%20all%20outlets
```

### Response

**Success Response (200 OK):**
```json
{
  "query_result": "string",
  "intermediate_steps": ["string"]
}
```

**Response Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `query_result` | string | Query results from SQLite | `"ZUS Coffee – Shah Alam Location: Lot 10.01..."` |
| `intermediate_steps` | array | Debug info about SQL generation | `["Text2SQL Agent ran on SQLDatabase tool..."]` |

### Error Responses

**422 Unprocessable Entity (Missing query):**
```json
{
  "detail": [
    {
      "loc": ["query_params", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Server-side Text2SQL agent not loaded. Check DB file or API key."
}
```

**500 Server Error:**
```json
{
  "detail": "Text2SQL Agent Error: [error_details]"
}
```

### Examples

#### Example 1: Find Outlets in Location
```bash
curl "http://localhost:8000/outlets?query=Which%20outlets%20are%20in%20Kuala%20Lumpur?"
```

**Response:**
```json
{
  "query_result": "1. Name: ZUS Coffee – Bandar Menjalara Location: 37, Jalan 3/62a...",
  "intermediate_steps": ["Text2SQL Agent ran on SQLDatabase tool..."]
}
```

#### Example 2: Find All Outlets
```bash
curl "http://localhost:8000/outlets?query=List%20all%20outlets"
```

**Response:**
```json
{
  "query_result": "1. Name: ZUS Coffee – ... 2. Name: ZUS Coffee – ... [72 total outlets]",
  "intermediate_steps": ["Text2SQL Agent ran on SQLDatabase tool..."]
}
```

### Python Integration

```python
import requests

response = requests.get("http://localhost:8000/outlets", params={
    "query": "Which outlets are in Shah Alam?"
})

if response.status_code == 200:
    data = response.json()
    print("Results:", data["query_result"])
else:
    print("Error:", response.json())
```

---

## 📊 Comparison: When to Use Each Endpoint

| Use Case | Endpoint | Reason |
|----------|----------|--------|
| Main chat interface | `/chat` | Full context, agent decides best tool |
| Quick product lookup | `/products` | Direct RAG, faster |
| Quick outlet lookup | `/outlets` | Direct SQL, faster |
| Bot conversation with memory | `/chat` | Session maintained |
| Programmatic product search | `/products` | Simple, no session needed |
| Programmatic outlet search | `/outlets` | Simple, no session needed |
| Health check | `/` | Minimal overhead |

---

## 🔌 Integration Patterns

### Pattern 1: Full Conversation Bot

```javascript
class ChatbotUI {
  constructor() {
    this.sessionId = generateSessionId();
  }

  async sendMessage(userMessage) {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: this.sessionId,
        message: userMessage
      })
    });

    const data = await response.json();
    
    // Display bot response with tool badge
    displayMessage(data.answer, data.tool_used);
    
    // Save to localStorage
    saveToHistory({ user: userMessage, bot: data.answer, tool: data.tool_used });
  }
}
```

### Pattern 2: Quick Lookup Service

```python
class QuickLookup:
  def get_product_info(self, product_name):
    """Quick product lookup"""
    response = requests.get("http://localhost:8000/products", 
      params={"query": product_name})
    return response.json()["summary"]

  def find_outlets(self, location):
    """Quick outlet lookup"""
    response = requests.get("http://localhost:8000/outlets",
      params={"query": f"Find outlets in {location}"})
    return response.json()["query_result"]
```

### Pattern 3: Multi-turn Conversation with Context

```javascript
class ContextualChat {
  constructor() {
    this.sessionId = `session_${Date.now()}`;
    this.context = [];
  }

  async ask(question) {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      body: JSON.stringify({
        session_id: this.sessionId,
        message: question
      })
    });

    const data = await response.json();
    this.context.push({
      user: question,
      bot: data.answer,
      tool: data.tool_used
    });
    
    return data.answer;
  }

  // Multi-turn example:
  // User: "Is there an outlet in Petaling Jaya?"
  // Bot: "Yes! Which outlet are you referring to?"
  // User: "SS 2, whats the opening time?"
  // Bot: (remembers context) "The SS 2 outlet opens at 9:00 AM"
}
```

---

## 📈 API Performance Characteristics

| Endpoint | Avg Response Time | Backend Processing |
|----------|-------------------|-------------------|
| `/` (health) | ~5ms | Instant |
| `/products` | 2-4s | FAISS search + LLM |
| `/outlets` | 3-5s | SQL generation + execution |
| `/chat` (simple) | 2-3s | Direct tool call |
| `/chat` (complex) | 5-10s | Agent planning + tool |

**Note:** Times depend on OpenAI API latency and database size.

---

## ⚠️ Error Handling Best Practices

### Always Check Status Codes

```python
try:
  response = requests.post("http://localhost:8000/chat",
    json={"session_id": sid, "message": msg},
    timeout=30
  )
  response.raise_for_status()
  data = response.json()
  
except requests.exceptions.Timeout:
  print("Backend took too long (>30s)")
  
except requests.exceptions.ConnectionError:
  print("Cannot connect to backend - is it running?")
  
except requests.exceptions.HTTPError:
  print(f"HTTP {response.status_code}: {response.json()['detail']}")
```

### Retry Strategy

```python
import time

def chat_with_retry(session_id, message, max_retries=3):
  for attempt in range(max_retries):
    try:
      response = requests.post(
        "http://localhost:8000/chat",
        json={"session_id": session_id, "message": message},
        timeout=30
      )
      response.raise_for_status()
      return response.json()
    except requests.exceptions.RequestException as e:
      if attempt < max_retries - 1:
        time.sleep(2 ** attempt)  # Exponential backoff
      else:
        raise
```

---

## 📝 Logging & Monitoring

### Log Interesting Events

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

response = chat_with_retry(session_id, message)

if response.get("tool_used"):
  logger.info(f"Tool used: {response['tool_used']}")
  
logger.debug(f"Intermediate steps: {response['intermediate_steps']}")
```

---

## 🧪 Testing API Endpoints

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Calculator via chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"What is 10+5?"}'

# Product query
curl "http://localhost:8000/products?query=espresso"

# Outlet query
curl "http://localhost:8000/outlets?query=outlets%20in%20KL"
```

### Using Postman

1. Import collection from API spec
2. Set base URL to `http://localhost:8000`
3. Create requests for each endpoint
4. Test with different parameters

---

## 🚀 Deployment Notes

### Production Considerations

1. **CORS:** Already configured for `localhost:3000`
   - Update for production domain
   
2. **Session Storage:** Currently in-memory
   - Consider Redis for distributed deployments
   
3. **Rate Limiting:** Not implemented
   - Add rate limiter for public APIs
   
4. **Authentication:** Not implemented
   - Add API key validation for security

---

**API Documentation Version:** 1.0
**Last Updated:** November 14, 2025
**Status:**  Active
