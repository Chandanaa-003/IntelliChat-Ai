import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center gap-1.5 px-3 py-2 rounded-2xl bg-white dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/60 w-fit shadow-sm">
      <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce [animation-delay:-0.3s]"></span>
      <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce [animation-delay:-0.15s]"></span>
      <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce"></span>
    </div>
  );
};
