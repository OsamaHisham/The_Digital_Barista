import ast
import os
import re
from typing import Dict, List, Optional, Sequence

import requests
import sqlalchemy
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
# 💡 MEMORY & AGENT IMPORTS
from langchain.agents import create_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
# --- LangChain Imports (v0.2+ Compliant) ---
from langchain_core.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                                    PromptTemplate)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel

# -------------------------------------------


# --- Configuration & Global Objects ---
app = FastAPI(
    title="Mindhive AI Assessment API",
    description="API for RAG and Text2SQL endpoints.",
    version="1.0.0"
)

# Add CORS middleware to allow React frontend to communicate with backend
app.add_middleware(
    allow_origins=[
        "http://localhost:3000",      # React dev server (Windows/Mac/Linux)
        "http://127.0.0.1:3000",      # React dev server (IP format)
        "http://localhost:8000",      # Same origin (for testing)
        "http://127.0.0.1:8000",      # Same origin (IP format)
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],              # Allow all headers
)

INDEX_PATH = "faiss_index"
SQL_DB_FILE = "outlets.db"
llm: Optional[ChatOpenAI] = None
embeddings: Optional[OpenAIEmbeddings] = None

# 💡 Memory Store: Dictionary to hold chat history objects
session_store: Dict[str, List[BaseMessage]] = {} 


try:
    # LLM Initialization
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", request_timeout=20)
    embeddings = OpenAIEmbeddings()
    print("[OK] LLM and embeddings loaded successfully.")
except Exception as e:
    print(f"[ERROR] Error initializing OpenAI: {e}") 

# Load FAISS vector store
retriever = None
try:
    if os.path.exists(INDEX_PATH) and embeddings:
        db_rag = FAISS.load_local(
            INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        retriever = db_rag.as_retriever(search_kwargs={"k": 3})
        print(f"[OK] FAISS index loaded from {INDEX_PATH}.")
    else:
        print(f"[WARN] FAISS index not found at {INDEX_PATH}.")
except Exception as e:
    print(f"[ERROR] Error loading FAISS index: {e}")

# Initialize Text2SQL Agent
sql_agent = None
try:
    if os.path.exists(SQL_DB_FILE) and llm:
        db_sql = SQLDatabase.from_uri(f"sqlite:///{SQL_DB_FILE}")

        sql_agent = create_sql_agent(
            llm=llm,
            db=db_sql,
            agent_type="openai-tools",
            verbose=False 
        )
        print(f"[OK] Text2SQL agent initialized for outlets.db.")
    else:
        print(f"[WARN] {SQL_DB_FILE} not found or LLM not loaded. Cannot initialize Text2SQL agent.")
except Exception as e:
    print(f"[ERROR] Error initializing Text2SQL agent: {e}")
    sql_agent = None


# --- Pydantic Models ---
class ProductQueryResponse(BaseModel):
    summary: str
    retrieved_sources: List[str]

class OutletQueryResponse(BaseModel):
    query_result: str
    intermediate_steps: List[str]

class ChatMessage(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    tool_used: Optional[str] = None
    intermediate_steps: Optional[List[str]] = None

# --- AGENT TOOLS ---
def safe_eval(expression: str):
    """Safely evaluate a mathematical expression without arbitrary code execution."""
    # Restrict to a safe namespace with only math operations
    safe_dict = {
        '__builtins__': {},
        'abs': abs,
        'round': round,
        'pow': pow,
    }
    try:
        result = eval(expression, safe_dict)
        return result
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

@tool
def calculate(expression: str) -> str:
    """Performs a simple mathematical calculation using an expression string (e.g., '10 * 5')."""
    try:
        result = safe_eval(expression)
        return f"Calculation result: {result}"
    except ValueError as e:
        return f"Sorry, the expression contains unsafe or invalid operations. Please provide a simple math expression."
    except Exception as e:
        return f"Sorry, I could not calculate the expression '{expression}'. Error: {e}"

# Helper function for product retrieval (called directly by agent, not via HTTP)
def _retrieve_product_info(query: str) -> str:
    """Internal helper to retrieve product info directly."""
    if not retriever or not llm:
        return "Product knowledge base not available."
    
    try:
        retrieved_docs = retriever.invoke(query)
        
        if not retrieved_docs:
            return "I am sorry, but I cannot find this product in the knowledge base."

        concatenated_docs = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        prompt_template = """User Question: {query}

Product Information:
{text}

Instructions: Based ONLY on the 'Product Information' provided, answer the User Question. 
If the information is COMPLETELY insufficient or irrelevant, your **ENTIRE** response MUST be the exact sentence: 
"I am sorry, but I cannot find this product in the knowledge base." 
Do not hallucinate or attempt to write a summary if the data is missing.

CONCISE AND FRIENDLY SUMMARY:"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        summarize_chain = prompt | llm 
        
        summary_result = summarize_chain.invoke(
            {
                "query": query,
                "text": concatenated_docs
            }
        )
        
        return summary_result.content
    except Exception as e:
        return f"Error retrieving product information: {e}"

@tool
def query_products_kb(query: str) -> str:
    """A tool for retrieving information about ZUS products from the knowledge base."""
    summary = _retrieve_product_info(query)
    # Format with a marker that should survive agent processing
    return f"[PRODUCT INFORMATION RETRIEVED]\nProduct Information: {summary}"

# Helper function for outlet query (called directly by agent, not via HTTP)
def _query_outlet_info(query: str) -> str:
    """Internal helper to query outlets directly."""
    if not sql_agent:
        return "Outlet database not available."
    
    try:
        result = sql_agent.invoke({"input": query})
        final_answer = result.get('output', 'Error: Agent failed to generate output.')
        return final_answer
    except Exception as e:
        return f"Error querying outlets: {e}"

@tool
def query_outlets_db(query: str) -> str:
    """A tool for querying the ZUS outlets database using natural language."""
    result = _query_outlet_info(query)
    # Format with a marker that should survive agent processing
    return f"[OUTLET DATABASE QUERY EXECUTED]\nOutlet Query Result: {result}"

# --- AGENT INITIALIZATION & PLANNER ---

AGENT_TOOLS = [calculate, query_products_kb, query_outlets_db]

# 💡 FIX 1: Simplify SYSTEM_INSTRUCTION. The create_agent function will automatically
# append the tool details to this instruction for OpenAI-based models.
SYSTEM_INSTRUCTION = """You are a friendly and helpful ZUS Coffee assistant. Your goal is to manage conversations, answer product questions, outlet queries, and respond to simple arithmetic requests. Use your tools when appropriate.

IMPORTANT OUTLET QUERY RULES:
- If a user asks a YES/NO question about outlet existence (e.g., "Is there an outlet in X?"), FIRST answer the question directly:
  * If outlets exist in that location: Reply "Yes! Which outlet are you referring to?" 
  * If no outlets exist: Reply "No, we currently don't have outlets in [location]."
- Only list detailed outlet information if the user asks for a list (e.g., "List outlets in X" or "Show me outlets").
- Keep responses concise and natural."""


def initialize_planner(llm, tools):
    """Initializes the base Agent (The Planner/Controller)."""
    
    # create_agent returns a compiled StateGraph that expects {"messages": [...]}
    agent_chain = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_INSTRUCTION
    )
    
    return agent_chain


# Initialize the agent once outside the request loop
if llm:
    planner_executor = initialize_planner(llm=llm, tools=AGENT_TOOLS)
else:
    planner_executor = None


# --- API Endpoints (omitted for brevity) ---
@app.get(
    "/products",
    response_model=ProductQueryResponse,
    summary="Query the ZUS Product Knowledge Base (RAG)"
)
async def query_products(
    query: str = Query(..., description="User's natural language question about products")
):
    if not retriever or not llm:
        raise HTTPException(
            status_code=503, 
            detail="Server-side RAG models not loaded. Check API key and FAISS index."
        )

    try:
        retrieved_docs = retriever.invoke(query)
        
        if not retrieved_docs:
            return ProductQueryResponse(
                summary="I am sorry, but I cannot find this product in the knowledge base.",
                retrieved_sources=[]
            )

        ai_summary = _retrieve_product_info(query)
        source_names = [doc.metadata.get("source", "Unknown") for doc in retrieved_docs]

        return ProductQueryResponse(
            summary=ai_summary,
            retrieved_sources=source_names
        )

    except Exception as e:
        print(f"Error during /products query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/outlets",
    response_model=OutletQueryResponse,
    summary="Query the ZUS Outlets SQL Database (Text2SQL)"
)
async def query_outlets(
    query: str = Query(..., description="User's natural language question about outlets (location, hours, services)")
):
    if not sql_agent:
        raise HTTPException(
            status_code=503, 
            detail="Server-side Text2SQL agent not loaded. Check DB file or API key."
        )

    try:
        final_answer = _query_outlet_info(query)
        intermediate_steps_placeholder = ["Text2SQL Agent ran on SQLDatabase tool to generate and execute an SQL query."]

        return OutletQueryResponse(
            query_result=final_answer,
            intermediate_steps=intermediate_steps_placeholder
        )

    except Exception as e:
        print(f"Error during /outlets query: {e}")
        raise HTTPException(status_code=500, detail=f"Text2SQL Agent Error: {e}")


@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="Main Chat Endpoint (Agent, Memory, and Planning)"
)
async def chat_endpoint(
    data: ChatMessage
):
    if not llm or not planner_executor:
        raise HTTPException(status_code=503, detail="LLM or Agent not initialized.")

    try:
        # Initialize session history if needed
        if data.session_id not in session_store:
            session_store[data.session_id] = []
        
        # Add the user message to history
        session_store[data.session_id].append(HumanMessage(content=data.message))
        
        # Invoke the agent with the correct input format: {"messages": [...]}
        result = planner_executor.invoke(
            {
                "messages": session_store[data.session_id]
            }
        )
        
        # Extract the final answer from the messages list
        if isinstance(result, dict) and "messages" in result:
            final_messages = result["messages"]
        else:
            final_messages = result
        
        # Get the last AI message
        answer = None
        for message in reversed(final_messages):
            if isinstance(message, AIMessage):
                answer = message.content
                break
        
        if answer is None:
            answer = "I encountered an error processing your request."
        
        # Add the AI response to history for the next turn
        session_store[data.session_id].append(AIMessage(content=answer))

        # Detect which tool was used by examining ToolMessages in the conversation
        tool_used = None
        tool_output = None
        
        # Look for ToolMessage objects that indicate which tool was called
        for message in final_messages:
            if hasattr(message, 'name'):  # ToolMessage has a 'name' attribute
                tool_name = getattr(message, 'name', '')
                if tool_name:  # Ensure tool_name is not empty
                    tool_name_lower = tool_name.lower()
                    if 'calculate' in tool_name_lower:
                        tool_used = "Calculator"
                        tool_output = getattr(message, 'content', None)
                    elif 'product' in tool_name_lower:
                        tool_used = "Product RAG"
                        tool_output = getattr(message, 'content', None)
                    elif 'outlet' in tool_name_lower:
                        tool_used = "Outlet Text2SQL"
                        tool_output = getattr(message, 'content', None)
        
        # If a tool was used and we have its output, prefer returning a sanitized tool output
        def _sanitize_tool_output(raw: Optional[str]) -> str:
            if raw is None:
                return ""
            s = str(raw)
            # Remove wrapper markers like [PRODUCT INFORMATION RETRIEVED] and labels
            s = s.replace('[PRODUCT INFORMATION RETRIEVED]', '')
            s = s.replace('Product Information:', '')
            s = s.replace('[OUTLET DATABASE QUERY EXECUTED]', '')
            s = s.replace('Outlet Query Result:', '')
            s = s.replace('Calculation result:', '')
            # Remove common polite prefixes the model might add
            for prefix in [
                'I apologize for the inconvenience. ',
                'I apologize for the inconvenience.',
                'I am sorry, ',
                'I am very sorry, ',
                'I apologize for the inconvenience. Let me calculate that for you. ',
                'I apologize for the inconvenience. Let me calculate that for you.',
                'Apologies — ',
                'Sorry, ',
                '\n',
            ]:
                if s.startswith(prefix):
                    s = s[len(prefix):]
            return s.strip()

        if tool_used and tool_output:
            tool_output_str = _sanitize_tool_output(getattr(tool_output, 'content', tool_output))

            # Detect if the user is asking a yes/no question about outlets
            is_yes_no_outlet_question = False
            if tool_used == 'Outlet Text2SQL' and data.message:
                msg_lower = data.message.lower()
                # Check if it's a yes/no question: "Is there...", "Are there...", "Do you have..."
                if re.match(r'^(is|are|do you)\s+(there\s+)?an?\s+(outlet|location)', msg_lower):
                    is_yes_no_outlet_question = True

            # If calculator, prefer a natural short sentence using the user's last message
            if tool_used == 'Calculator':
                # Find last human message in the session (it was appended before invoking the agent)
                last_human = None
                try:
                    history = session_store.get(data.session_id, [])
                    # Find last HumanMessage from the end
                    for m in reversed(history):
                        if isinstance(m, HumanMessage):
                            last_human = m
                            break
                except Exception:
                    last_human = None

                # Extract numeric result if present
                num_match = re.search(r"[-+]?\d+(?:\.\d+)?", tool_output_str)

                if num_match:
                    result_text = num_match.group(0)
                    if last_human and last_human.content:
                        answer = f"{last_human.content.strip()} is {result_text}"
                    else:
                        answer = result_text
                else:
                    # No clear numeric result — return the tool message as-is (it's likely an error/refusal)
                    answer = tool_output_str

            else:
                # For Product RAG and Outlet Text2SQL, return only the cleaned content
                if tool_used == 'Outlet Text2SQL':
                    # Check if this is a yes/no question
                    if is_yes_no_outlet_question:
                        # Extract location name from user message
                        location = None
                        msg_lower = data.message.lower()
                        # Try to extract location after "in" keyword
                        in_match = re.search(r'\bin\s+([^?]+)', msg_lower)
                        if in_match:
                            location = in_match.group(1).strip()
                        
                        # Check if tool output indicates outlets were found
                        has_outlets = (
                            "outlet" in tool_output_str.lower() and 
                            len(tool_output_str) > 20 and
                            "no matching" not in tool_output_str.lower() and
                            "no outlets" not in tool_output_str.lower() and
                            "error" not in tool_output_str.lower()
                        )
                        
                        if has_outlets:
                            answer = "Yes! Which outlet are you referring to?"
                        else:
                            if location:
                                answer = f"No, we currently don't have outlets in {location}."
                            else:
                                answer = "No, we don't have outlets at that location."
                    else:
                        # User asked for a list - format the outlets nicely
                        # The raw SQL output may look like:
                        # "ZUS Coffee – Bandar Menjalara ZUS Coffee – LSH33, Sentul ..."
                        # OR "Outlet Name: X Location: Y\n1. Name: ... Location: ..."
                        
                        outlets = []
                        
                        # Strategy 1: Split by "Outlet Name:" with Location info
                        if 'Outlet Name:' in tool_output_str:
                            # Match patterns like "Outlet Name: ... Location: ..."
                            outlet_pattern = r'Outlet Name:\s*([^L]*?)(?=Outlet Name:|$)'
                            matches = re.findall(outlet_pattern, tool_output_str, re.DOTALL)
                            outlets = [m.strip() for m in matches if m.strip()]
                        
                        # Strategy 2: Split by "Name:" keyword
                        if len(outlets) == 0 and 'Name:' in tool_output_str:
                            name_pattern = r'Name:\s*([^N]*?)(?=Name:|$)'
                            matches = re.findall(name_pattern, tool_output_str, re.DOTALL)
                            outlets = [m.strip() for m in matches if m.strip()]
                        
                        # Strategy 3: Split by "ZUS Coffee –" (common outlet name pattern)
                        if len(outlets) == 0 and 'ZUS Coffee' in tool_output_str:
                            zus_pattern = r'(ZUS Coffee[^Z]*?)(?=ZUS Coffee|$)'
                            matches = re.findall(zus_pattern, tool_output_str)
                            outlets = [m.strip() for m in matches if m.strip()]
                        
                        # Strategy 4: Split by numbered list (1. 2. 3. etc)
                        if len(outlets) == 0:
                            numbered = re.split(r'\n\s*\d+\.\s+', tool_output_str)
                            if len(numbered) > 1:
                                for item in numbered[1:]:
                                    outlet_text = item.strip()
                                    if outlet_text:
                                        outlets.append(outlet_text)
                        
                        if len(outlets) > 0:
                            # Format each outlet nicely - each on its own line
                            max_show = 5
                            shown = outlets[:max_show]
                            
                            formatted_outlets = []
                            for outlet in shown:
                                # Extract the first meaningful line/sentence from each outlet
                                # Remove excessive newlines and clean up
                                lines = outlet.split('\n')
                                clean_lines = [line.strip() for line in lines if line.strip()]
                                
                                # Combine first few lines but keep it on one line per outlet
                                if len(clean_lines) > 0:
                                    # Take up to 2 lines (Name/Info + Location)
                                    outlet_summary = ' '.join(clean_lines[:2])
                                    formatted_outlets.append(outlet_summary)
                            
                            # Join each outlet on a separate line
                            formatted = "\n".join(formatted_outlets)
                            if len(outlets) > max_show:
                                formatted += f"\n\n(Showing first {max_show} results of {len(outlets)}.)"
                            answer = formatted
                        else:
                            # Fallback if no outlets found
                            answer = tool_output_str
                else:
                    answer = tool_output_str

        # If we didn't detect a tool via ToolMessage, do a light heuristic on the agent answer
        if not tool_used:
            answer_lower = answer.lower() if answer else ""
            if "calculation result" in answer_lower or re.search(r"\b\d{2,}\b", answer_lower):
                tool_used = "Calculator"
            elif "product information" in answer_lower or "product" in answer_lower:
                tool_used = "Product RAG"
            elif "outlet query result" in answer_lower or "outlet" in answer_lower or "outlets" in answer_lower:
                tool_used = "Outlet Text2SQL"
        
        return ChatResponse(
            answer=answer,
            tool_used=tool_used,
            intermediate_steps=[f"Planner used: {tool_used}"] if tool_used else ["Planner responded directly."]
        )

    except Exception as e:
        print(f"[ERROR] Error during /chat processing: {e}")
        # Return a clearer error response if the LLM call fails
        return ChatResponse(
             answer=f"I am very sorry, I encountered a critical error while trying to process your request. Please try again. Error: {e}",
             tool_used="Error Handler"
        )


@app.get("/", summary="Health Check")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("Starting FastAPI server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
