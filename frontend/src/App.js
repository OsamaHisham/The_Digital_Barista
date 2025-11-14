import './App.css';
import ChatWindow from './components/ChatWindow';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>ZUS Coffee AI Chatbot</h1>
        <p className="subtitle">Ask about products, outlets, or do calculations</p>
      </header>
      <main className="app-main">
        <ChatWindow />
      </main>
      <footer className="app-footer">
        <p>Powered by LangChain Agent | FastAPI Backend</p>
      </footer>
    </div>
  );
}

export default App;
