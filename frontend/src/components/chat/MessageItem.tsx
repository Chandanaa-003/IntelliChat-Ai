import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User as UserIcon, Copy, Check, RotateCw } from 'lucide-react';
import type { Message } from '../../types';
import { CodeBlock } from './CodeBlock';
import { TypingIndicator } from './TypingIndicator';
import { useChat } from '../../context/ChatContext';

interface MessageItemProps {
  message: Message;
  isLastAssistant?: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, isLastAssistant }) => {
  const { regenerateMessage, isStreaming } = useChat();
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message', err);
    }
  };

  return (
    <div
      className={`group flex gap-3 sm:gap-4 w-full max-w-4xl mx-auto px-2 sm:px-4 py-4 transition-colors ${isUser ? 'justify-end' : 'justify-start'
        }`}
    >
      {/* Assistant Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 sm:w-9 sm:h-9 rounded-2xl bg-gradient-to-tr from-primary-600 to-indigo-500 text-white flex items-center justify-center shadow-md shadow-primary-500/20">
          <Bot className="w-5 h-5" />
        </div>
      )}

      {/* Message Content Container */}
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[85%] sm:max-w-[78%]`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm sm:text-base leading-relaxed shadow-sm transition-all ${isUser
            ? 'bg-gradient-to-r from-primary-600 to-indigo-600 text-white rounded-br-none'
            : 'bg-white dark:bg-slate-900/90 text-slate-800 dark:text-slate-100 border border-slate-200/80 dark:border-slate-800 rounded-bl-none'
            }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : message.isStreaming && !message.content ? (
            <TypingIndicator />
          ) : (
            <div className="prose dark:prose-invert max-w-none text-sm sm:text-base prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 prose-pre:my-0 prose-pre:p-0 prose-pre:bg-transparent">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || '');
                    const codeText = String(children).replace(/\n$/, '');
                    if (!inline && (match || codeText.includes('\n'))) {
                      return (
                        <CodeBlock
                          language={match ? match[1] : undefined}
                          value={codeText}
                        />
                      );
                    }
                    return (
                      <code
                        className="px-1.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-primary-600 dark:text-primary-300 font-mono text-xs sm:text-sm font-semibold"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Action & Metadata Bar */}
        {!isUser && !message.isStreaming && (
          <div className="flex items-center gap-2 mt-1.5 px-1 text-xs text-slate-400 opacity-80 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 hover:text-slate-700 dark:hover:text-slate-200 p-1 rounded transition-colors"
              title="Copy response"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {isLastAssistant && (
              <button
                onClick={regenerateMessage}
                disabled={isStreaming}
                className="flex items-center gap-1 hover:text-slate-700 dark:hover:text-slate-200 p-1 rounded transition-colors disabled:opacity-50"
                title="Regenerate response"
              >
                <RotateCw className="w-3.5 h-3.5" />
                <span>Regenerate</span>
              </button>
            )}

            {message.token_count ? (
              <span className="text-[11px] text-slate-400/80 ml-2">
                ~{message.token_count} tokens
              </span>
            ) : null}
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 sm:w-9 sm:h-9 rounded-2xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-200 flex items-center justify-center shadow-sm">
          <UserIcon className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
