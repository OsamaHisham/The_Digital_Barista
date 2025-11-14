import { useEffect, useRef, useState } from 'react';
import './ChatWindow.css';
import Message from './Message';
import ToolBadge from './ToolBadge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const STORAGE_KEY = 'zus_chat_history';
const SESSION_KEY = 'zus_session_id';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [lastToolUsed, setLastToolUsed] = useState(null);
  const messagesEndRef = useRef(null);

  // Initialize session and load history on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem(SESSION_KEY);
    const newSessionId = savedSessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    localStorage.setItem(SESSION_KEY, newSessionId);

    // Load chat history from localStorage
    const savedHistory = localStorage.getItem(STORAGE_KEY);
    if (savedHistory) {
      try {
        setMessages(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to load chat history:', e);
      }
    }
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  const handleReset = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(SESSION_KEY);
      setLastToolUsed(null);
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      localStorage.setItem(SESSION_KEY, newSessionId);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    // Check for /reset command
    if (inputValue.trim().toLowerCase() === '/reset') {
      handleReset();
      setInputValue('');
      return;
    }

    const userMessage = inputValue.trim();
    if (!userMessage) return;

    // Add user message to chat
    const newUserMessage = {
      id: `msg_${Date.now()}_user`,
      type: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');
    setIsLoading(true);
    setLastToolUsed(null);

    // Add "thinking" message
    const thinkingMessage = {
      id: `msg_${Date.now()}_thinking`,
      type: 'bot',
      content: 'Bot is thinking...',
      isThinking: true,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    try {
      // Call backend API with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout

      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMessage,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Remove thinking message and add bot response
      setMessages((prev) =>
        prev
          .filter((msg) => !msg.isThinking)
          .concat([
            {
              id: `msg_${Date.now()}_bot`,
              type: 'bot',
              content: data.answer,
              toolUsed: data.tool_used,
              timestamp: new Date().toISOString(),
            },
          ])
      );

      setLastToolUsed(data.tool_used);
    } catch (error) {
      console.error('Error calling backend:', error);

      let errorMessage = 'Error: Failed to reach backend';
      
      if (error.name === 'AbortError') {
        errorMessage = 'Error: Request timeout (backend took too long to respond)';
      } else if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = `Error: Cannot connect to backend at ${BACKEND_URL}. Is the server running?`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }

      // Replace thinking message with error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.isThinking
            ? {
                ...msg,
                content: errorMessage,
                isThinking: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>Chat with ZUS Assistant</h2>
        <button className="reset-btn" onClick={handleReset} title="Clear chat history">
          Clear History
        </button>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>No messages yet. Start by asking me something!</p>
            <div className="suggestions">
              <p className="suggestions-title">Try asking:</p>
              <ul>
                <li>What is 150 times 12?</li>
                <li>Tell me about the Black Sugar Latte</li>
                <li>List outlets in Kuala Lumpur</li>
              </ul>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} className={`message-wrapper message-${msg.type}`}>
                {msg.toolUsed && !msg.isThinking && (
                  <ToolBadge tool={msg.toolUsed} />
                )}
                <Message message={msg} />
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <form className="message-form" onSubmit={handleSendMessage}>
        <textarea
          className="message-input"
          placeholder="Type your message... (or /reset to clear history)"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage(e);
            }
          }}
          disabled={isLoading}
          rows="3"
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      <div className="chat-info">
        <p className="session-id">Session ID: {sessionId.substring(0, 20)}...</p>
      </div>
    </div>
  );
};

export default ChatWindow;
