import './ToolBadge.css';

const ToolBadge = ({ tool }) => {
  if (!tool) return null;

  const getToolIcon = (toolName) => {
    switch (toolName) {
      case 'Calculator':
        return '🧮';
      case 'Product RAG':
        return '📦';
      case 'Outlet Text2SQL':
        return '📍';
      default:
        return '🔧';
    }
  };

  const getToolColor = (toolName) => {
    switch (toolName) {
      case 'Calculator':
        return 'calculator';
      case 'Product RAG':
        return 'rag';
      case 'Outlet Text2SQL':
        return 'sql';
      default:
        return 'default';
    }
  };

  return (
    <div className={`tool-badge badge-${getToolColor(tool)}`}>
      <span className="tool-icon">{getToolIcon(tool)}</span>
      <span className="tool-name">{tool}</span>
    </div>
  );
};

export default ToolBadge;
