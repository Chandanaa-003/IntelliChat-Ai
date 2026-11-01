import React, { useState } from 'react';
import { Check, Copy, Terminal } from 'lucide-react';

interface CodeBlockProps {
  language?: string;
  value: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code', err);
    }
  };

  return (
    <div className="relative my-4 rounded-xl overflow-hidden border border-slate-700/60 bg-[#0d1117] text-slate-200 font-mono text-xs sm:text-sm shadow-md">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-[#161b22] text-xs text-slate-400">
        <div className="flex items-center gap-1.5">
          <Terminal className="w-3.5 h-3.5 text-primary-400" />
          <span className="font-semibold uppercase tracking-wider text-[11px]">
            {language || 'text'}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-sans text-[11px]">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="font-sans text-[11px]">Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Content */}
      <pre className="p-4 overflow-x-auto text-slate-100 leading-relaxed scrollbar-thin">
        <code>{value}</code>
      </pre>
    </div>
  );
};
