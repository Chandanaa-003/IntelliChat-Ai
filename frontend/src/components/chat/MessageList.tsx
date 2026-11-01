import React, { useEffect, useRef } from 'react';
import { Sparkles, Code2, Database, Zap, BookOpen } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { MessageItem } from './MessageItem';

const SUGGESTIONS = [
  {
    icon: Code2,
    title: 'Python FastAPI Stream',
    prompt: 'Show me how to create an asynchronous SSE streaming endpoint in FastAPI.',
  },
  {
    icon: Database,
    title: 'PostgreSQL Optimization',
    prompt: 'What are the best indexing strategies in PostgreSQL for a high-volume chat app?',
  },
  {
    icon: Zap,
    title: 'React Custom Hooks',
    prompt: 'Write a TypeScript React hook to consume Server-Sent Events with reconnection.',
  },
  {
    icon: BookOpen,
    title: 'AI System Architecture',
    prompt: 'Explain the difference between RAG and fine-tuning with architectural trade-offs.',
  },
];

export const MessageList: React.FC = () => {
  const { messages, sendMessage, isStreaming } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-3xl mx-auto animate-fade-in">
        {/* Brand Icon */}
        <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-primary-600 to-indigo-500 text-white flex items-center justify-center shadow-xl shadow-primary-500/25 mb-6">
          <Sparkles className="w-8 h-8" />
        </div>

        <h1 className="text-2xl sm:text-3xl font-display font-bold text-slate-800 dark:text-white mb-2">
          How can I help you today?
        </h1>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mb-8">
          IntelliChat is ready to answer questions, analyze code, and assist with complex engineering challenges.
        </p>

        {/* Suggestion Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          {SUGGESTIONS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                disabled={isStreaming}
                onClick={() => sendMessage(item.prompt)}
                className="flex items-start gap-3.5 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white/60 dark:bg-slate-900/50 hover:bg-white dark:hover:bg-slate-800/80 hover:border-primary-400 dark:hover:border-primary-500/50 text-left transition-all duration-200 shadow-sm hover:shadow-md group"
              >
                <div className="p-2.5 rounded-xl bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400 group-hover:scale-105 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="font-semibold text-sm text-slate-800 dark:text-slate-200 mb-0.5">
                    {item.title}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                    {item.prompt}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 space-y-2">
      {messages.map((message, index) => {
        const isLastAssistant =
          message.role === 'assistant' &&
          index === messages.length - 1 &&
          !message.isStreaming;

        return (
          <MessageItem
            key={message.id || index}
            message={message}
            isLastAssistant={isLastAssistant}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
};
