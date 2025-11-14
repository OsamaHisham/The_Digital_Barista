import './Message.css';

const Message = ({ message }) => {
  const isUser = message.type === 'user';
  const isThinking = message.isThinking;

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'} ${isThinking ? 'thinking' : ''}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <p>{message.content}</p>
        {message.timestamp && (
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};

export default Message;
