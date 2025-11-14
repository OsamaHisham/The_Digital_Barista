# ZUS Coffee AI Chatbot Frontend

React-based frontend for the ZUS Coffee AI Chatbot, featuring a modern chat interface with tool visualization and persistent chat history.

## Features

- **Chat Interface**: Clean, responsive chat window with user and bot messages
- **Tool Visualization**: Displays which tool was used (Calculator, Product RAG, Outlet Text2SQL) with visual badges
- **Session Management**: Unique session IDs for each user
- **Persistent History**: Chat history saved to browser localStorage
- **Reset Command**: Type `/reset` to clear chat history
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Thinking Indicator**: Shows "Bot is thinking..." while waiting for response

## Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML file
├── src/
│   ├── components/
│   │   ├── ChatWindow.js   # Main chat component
│   │   ├── ChatWindow.css
│   │   ├── Message.js      # Individual message component
│   │   ├── Message.css
│   │   ├── ToolBadge.js    # Tool usage badge component
│   │   └── ToolBadge.css
│   ├── App.js              # Main app component
│   ├── App.css
│   ├── index.js            # React entry point
│   └── index.css
├── package.json
├── .env                    # Environment variables
└── .gitignore
```

## Installation & Setup

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation Steps

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Configure the backend URL in `.env`:

   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

3. Start the development server:

   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Available Scripts

- `npm start` - Run development server (port 3000)
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (irreversible)

## Features in Detail

### Chat Interface

- Send messages via text input
- Use Shift+Enter for newline, Enter to send
- Auto-scroll to latest messages
- Timestamps on each message

### Tool Badges

- **Calculator** (🧮): Shows when math calculations are performed
- **Product RAG** (📦): Shows when product information is retrieved
- **Outlet Text2SQL** (📍): Shows when outlet/database queries are made

### Session Management

- Each session gets a unique ID
- Session ID persists across page reloads
- Useful for server-side logging and memory

### Storage

- All chat messages stored in `localStorage`
- History persists across browser sessions
- `/reset` command clears history

### Responsive Design

- Mobile-optimized interface
- Touch-friendly buttons
- Adaptive layout for different screen sizes

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_BACKEND_URL` | <http://localhost:8000> | Backend API URL |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Backend Connection Error

- Ensure backend is running on `http://localhost:8000`
- Check `.env` file has correct `REACT_APP_BACKEND_URL`
- Check browser console for CORS errors

### Chat History Not Persisting

- Clear browser localStorage: `localStorage.clear()`
- Check that localStorage is enabled in browser

### Build Issues

- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Try `npm cache clean --force`

## Development Notes

### Architecture

- Functional components with React Hooks
- State management with `useState`, `useEffect`, `useRef`
- Local storage for persistence
- CSS for styling (no external UI library)

### Key Components

1. **ChatWindow**: Main container, manages state and API calls
2. **Message**: Renders individual messages
3. **ToolBadge**: Displays tool usage indicators

### API Integration

- Fetch API for HTTP requests
- JSON request/response format
- 30-second timeout for responses

## License

MIT
