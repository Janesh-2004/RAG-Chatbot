import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import MessageBubble from './MessageBubble';
import FileUploader from './Fileuploader';

/**
 * ChatWindow component for the chat interface
 */
const ChatWindow = ({
  chatId,
  chatName,
  hasDocuments,
  messages: initialMessages = [],
  onAddMessage,
  onUploadSuccess,
  onResetSystem,
  conversationTitle,
}) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load messages when switching chats
  useEffect(() => {
    setMessages(initialMessages);
    setInput('');
  }, [chatId, initialMessages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || !hasDocuments || isLoading) return;

    const userMessage = {
      text: input.trim(),
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    if (onAddMessage) {
      onAddMessage(chatId, userMessage);
    }
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/query', {
        question: userMessage.text,
        chat_id: chatId,
        chat_name: chatName
      });

      const botMessage = {
        text: response.data.answer,
        isUser: false,
        timestamp: new Date().toISOString(),
        sources: response.data.sources || []
      };

      setMessages(prev => [...prev, botMessage]);
      if (onAddMessage) {
        onAddMessage(chatId, botMessage);
      }
    } catch (err) {
      console.error('Error querying:', err);
      const errorMessage = {
        text: err.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      if (onAddMessage) {
        onAddMessage(chatId, errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all messages in this chat?')) {
      setMessages([]);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto w-full">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/30 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Current Chat</p>
            <h3 className="text-lg font-semibold text-white">{conversationTitle}</h3>
            <span className={`text-sm mt-1 inline-block ${
              hasDocuments ? 'text-green-400' : 'text-yellow-500'
            }`}>
              {hasDocuments ? '✓ Ready to chat' : '⚠️ Upload a file to get started'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleClearChat}
              disabled={messages.length === 0}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear Chat
            </button>
            <button
              onClick={onResetSystem}
              className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
            >
              Reset System
            </button>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="max-w-md">
              <h2 className="text-2xl font-bold text-white mb-3">👋 Welcome!</h2>
              <p className="text-gray-400 mb-6">
                {hasDocuments
                  ? 'Start asking questions about your documents!'
                  : 'Upload a document to begin chatting with your AI assistant.'}
              </p>
              {hasDocuments && (
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-5 text-left">
                  <p className="font-semibold text-white mb-3">💡 Try asking:</p>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400">→</span>
                      Summarize the uploaded document
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400">→</span>
                      What are the key takeaways?
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400">→</span>
                      Explain the section about...
                    </li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <MessageBubble key={`${msg.timestamp}-${idx}`} message={msg} isUser={msg.isUser} />
            ))}
          </>
        )}
        
        {isLoading && (
          <div className="flex items-center gap-3 text-gray-400 mb-4">
            <div className="flex gap-1.5">
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot"></span>
            </div>
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        {!hasDocuments && (
          <p className="text-center text-sm text-yellow-500 mb-3">
            📎 Upload a PDF, DOCX, or TXT file to unlock the chat
          </p>
        )}
        
        <div className="flex items-end gap-3">
          <FileUploader chatId={chatId} chatName={chatName} onUploadSuccess={onUploadSuccess} variant="icon" />
          
          <div className="flex-1 bg-gray-800 rounded-2xl border border-gray-700 focus-within:border-blue-500 transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={
                hasDocuments
                  ? 'Ask anything about your documents...'
                  : 'Upload a document to start chatting'
              }
              disabled={isLoading || !hasDocuments}
              rows="1"
              className="w-full px-4 py-3 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none disabled:opacity-50 max-h-40 overflow-y-auto scrollbar-thin"
              style={{ minHeight: '48px' }}
            />
          </div>

          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim() || !hasDocuments}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white rounded-2xl font-medium transition-colors disabled:cursor-not-allowed min-w-[100px]"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
