import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * MessageBubble component to display individual chat messages
 * with markdown support and syntax highlighting
 */
const MessageBubble = ({ message, isUser }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div
        className={`max-w-[80%] rounded-2xl px-5 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-800 text-gray-100 rounded-bl-sm border border-gray-700'
        }`}
      >
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-semibold opacity-80">
            {isUser ? 'You' : '🤖 AI Assistant'}
          </span>
        </div>
        
        <div className={`${isUser ? 'text-white' : 'markdown-content'}`}>
          {isUser ? (
            <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      className="rounded-lg my-2"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-gray-700 px-1.5 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.text}
            </ReactMarkdown>
          )}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <details className="mt-3 pt-3 border-t border-gray-700">
            <summary className="text-xs font-medium text-blue-400 cursor-pointer hover:text-blue-300 transition-colors">
              📚 Sources ({message.sources.length})
            </summary>
            <div className="mt-2 space-y-2">
              {message.sources.map((source, idx) => (
                <div key={idx} className="bg-gray-900/50 rounded-lg p-3 text-xs">
                  <div className="font-semibold text-blue-400 mb-1">
                    📄 {source.source}
                  </div>
                  <div className="text-gray-400 line-clamp-3">
                    {source.content}
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}

        {message.isError && (
          <div className="mt-2 text-xs text-red-400">
            ⚠️ Error occurred
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
