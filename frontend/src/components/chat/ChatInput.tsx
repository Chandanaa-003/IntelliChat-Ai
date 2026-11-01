import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Square } from 'lucide-react';
import { useChat } from '../../context/ChatContext';

export const ChatInput: React.FC = () => {
  const { sendMessage, isStreaming, stopStreaming } = useChat();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea up to 200px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      <div className="relative rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-lg shadow-slate-900/5 dark:shadow-black/30 p-2 transition-all focus-within:border-primary-500/80 focus-within:ring-2 focus-within:ring-primary-500/20">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message IntelliChat..."
          rows={1}
          className="w-full resize-none bg-transparent px-3 py-2 text-sm sm:text-base text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none max-h-48 leading-relaxed"
        />

        <div className="flex items-center justify-between pt-1 px-2 border-t border-slate-100 dark:border-slate-800/80 mt-1">
          <span className="text-[11px] text-slate-400">
            Use <kbd className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-300 font-mono text-[10px]">Shift + Enter</kbd> for new line
          </span>

          {isStreaming ? (
            <button
              onClick={stopStreaming}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 font-medium text-xs transition-colors"
              title="Stop generating"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Stop</span>
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!input.trim()}
              className="p-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white shadow-md shadow-primary-500/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none hover:scale-105 active:scale-95"
              aria-label="Send message"
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
