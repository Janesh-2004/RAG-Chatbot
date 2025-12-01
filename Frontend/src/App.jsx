import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUploader from './Components/Fileuploader';
import ChatWindow from './Components/Chatwindow';
import './index.css';

/**
 * Main App component for RAG Chatbot
 */
function App() {
  // Load conversations from localStorage or use default
  const [conversations, setConversations] = useState(() => {
    const saved = localStorage.getItem('rag_conversations');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved conversations:', e);
      }
    }
    return [{ 
      id: `chat_${Date.now()}`, 
      title: 'New Chat',
      name: 'default',  // Chat name for index
      hasDocuments: false,
      messages: []  // Store chat history
    }];
  });
  
  const [activeConversationId, setActiveConversationId] = useState(() => {
    const saved = localStorage.getItem('rag_active_chat');
    return saved || conversations[0].id;
  });

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('rag_conversations', JSON.stringify(conversations));
  }, [conversations]);

  // Save active conversation ID
  useEffect(() => {
    localStorage.setItem('rag_active_chat', activeConversationId);
  }, [activeConversationId]);

  const activeConversation = conversations.find(c => c.id === activeConversationId);

  const createConversation = () => {
    // Prompt for chat name
    const chatName = prompt('Enter a name for this chat:');
    
    if (!chatName || !chatName.trim()) {
      alert('Chat name is required!');
      return;
    }
    
    // Validate chat name (basic sanitization)
    const sanitizedName = chatName.trim().replace(/[^a-zA-Z0-9\s\-_]/g, '');
    
    if (!sanitizedName) {
      alert('Invalid chat name. Please use letters, numbers, spaces, hyphens, or underscores.');
      return;
    }
    
    const newConv = {
      id: `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: sanitizedName,
      name: sanitizedName,  // Used for Azure index creation
      hasDocuments: false,
      messages: []
    };
    setConversations([...conversations, newConv]);
    setActiveConversationId(newConv.id);
  };

  const deleteConversation = (id) => {
    if (conversations.length === 1) {
      alert('Cannot delete the last conversation');
      return;
    }
    const filtered = conversations.filter(c => c.id !== id);
    setConversations(filtered);
    if (activeConversationId === id) {
      setActiveConversationId(filtered[0].id);
    }
  };

  const handleUploadSuccess = (data) => {
    setConversations(conversations.map(c =>
      c.id === activeConversationId
        ? { ...c, hasDocuments: true }
        : c
    ));
  };

  const addMessageToConversation = (chatId, message) => {
    setConversations(prevConvs => prevConvs.map(c =>
      c.id === chatId
        ? { ...c, messages: [...(c.messages || []), message] }
        : c
    ));
  };

  const handleResetSystem = async () => {
    if (!window.confirm('Reset this chat? All documents and messages will be deleted.')) {
      return;
    }

    try {
      await axios.post('http://localhost:8000/reset', {
        chat_id: activeConversationId
      });

      setConversations(conversations.map(c =>
        c.id === activeConversationId
          ? { ...c, hasDocuments: false, messages: [] }
          : c
      ));
    } catch (err) {
      console.error('Error resetting:', err);
      alert('Failed to reset: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-gray-900">
      {/* Sidebar */}
      <aside className="w-72 bg-gray-900/50 backdrop-blur-xl border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h2 className="text-xl font-bold text-white mb-4">💬 Conversations</h2>
          <button
            onClick={createConversation}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <span className="text-lg">+</span> New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin">
          {conversations.map(conv => (
            <div
              key={conv.id}
              onClick={() => setActiveConversationId(conv.id)}
              className={`relative p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                conv.id === activeConversationId
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-800/50 text-gray-300 hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium truncate flex-1">{conv.title}</span>
                <span className="text-xl ml-2">{conv.hasDocuments ? '📄' : '○'}</span>
              </div>
              {conversations.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.id);
                  }}
                  className={`absolute top-2 right-2 w-6 h-6 rounded flex items-center justify-center text-lg opacity-0 group-hover:opacity-100 transition-opacity ${
                    conv.id === activeConversationId
                      ? 'hover:bg-blue-700'
                      : 'hover:bg-gray-700'
                  }`}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        <header className="bg-gray-900/30 backdrop-blur-sm border-b border-gray-800 p-6">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-4xl">🤖</span> RAG Chatbot
              </h1>
              <p className="text-gray-400 mt-1">Chat with Your Documents Using AI</p>
            </div>
            <div className={`px-4 py-2 rounded-full font-medium text-sm ${
              activeConversation?.hasDocuments
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
            }`}>
              {activeConversation?.hasDocuments ? '✓ Ready' : '⏳ Waiting for documents'}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden">
          <ChatWindow
            chatId={activeConversationId}
            chatName={activeConversation?.name}
            hasDocuments={activeConversation?.hasDocuments || false}
            messages={activeConversation?.messages || []}
            onAddMessage={addMessageToConversation}
            onUploadSuccess={handleUploadSuccess}
            onResetSystem={handleResetSystem}
            conversationTitle={activeConversation?.title || 'Chat'}
          />
        </div>
      </main>
    </div>
  );
}

export default App;