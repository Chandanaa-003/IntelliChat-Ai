import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, ChevronDown, Check, Cpu } from 'lucide-react';
import { useChat } from '../../context/ChatContext';

export const ModelSelector: React.FC = () => {
  const { models, selectedModel, setSelectedModel, isStreaming } = useChat();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeModelObj = models.find(m => m.id === selectedModel) || {
    id: 'smart-assistant-v1',
    name: 'Smart Assistant',
    provider: 'mock',
    description: 'Built-in intelligent offline assistant',
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => !isStreaming && setIsOpen(!isOpen)}
        disabled={isStreaming}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-200 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <Sparkles className="w-4 h-4 text-primary-500" />
        <span className="truncate max-w-[140px] sm:max-w-[200px]">{activeModelObj.name}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 sm:w-80 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl shadow-slate-900/10 dark:shadow-black/40 py-2 z-50 animate-fade-in">
          <div className="px-3 py-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Select AI Model
          </div>
          <div className="max-h-64 overflow-y-auto space-y-1 px-1">
            {models.map(model => (
              <button
                key={model.id}
                onClick={() => {
                  setSelectedModel(model.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-start gap-3 p-2.5 rounded-xl text-left transition-colors ${
                  selectedModel === model.id
                    ? 'bg-primary-50 dark:bg-primary-950/40 text-primary-900 dark:text-primary-100'
                    : 'hover:bg-slate-100 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div className="mt-0.5 p-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                  <Cpu className="w-3.5 h-3.5 text-primary-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="font-medium text-xs sm:text-sm truncate">{model.name}</span>
                    {selectedModel === model.id && (
                      <Check className="w-4 h-4 text-primary-500 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{model.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
