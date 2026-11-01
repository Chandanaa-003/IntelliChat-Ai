import React, { useState } from 'react';
import { PanelLeft, Check, Edit2 } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { ModelSelector } from '../layout/ModelSelector';
import { ThemeToggle } from '../layout/ThemeToggle';
import { useAuth } from '../../context/AuthContext';

export const ChatHeader: React.FC = () => {
  const { toggleSidebar, currentConversation, updateConversationTitle } = useChat();
  const { user, openAuthModal } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [titleText, setTitleText] = useState('');

  const startEdit = () => {
    if (currentConversation) {
      setTitleText(currentConversation.title);
      setIsEditing(true);
    }
  };

  const saveEdit = () => {
    if (currentConversation && titleText.trim()) {
      updateConversationTitle(currentConversation.id, titleText.trim());
    }
    setIsEditing(false);
  };

  return (
    <header className="h-16 px-4 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Toggle Sidebar"
          aria-label="Toggle sidebar"
        >
          <PanelLeft className="w-5 h-5" />
        </button>

        {/* Conversation Title */}
        <div className="flex items-center gap-2">
          {currentConversation ? (
            isEditing ? (
              <div className="flex items-center gap-1">
                <input
                  type="text"
                  value={titleText}
                  onChange={(e) => setTitleText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                  className="px-2 py-1 rounded-lg text-sm bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-primary-500 focus:outline-none"
                  autoFocus
                />
                <button
                  onClick={saveEdit}
                  className="p-1 rounded-md text-emerald-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <Check className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 group">
                <span className="font-semibold text-sm sm:text-base text-slate-800 dark:text-slate-100 truncate max-w-[160px] sm:max-w-xs">
                  {currentConversation.title}
                </span>
                <button
                  onClick={startEdit}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-opacity"
                  title="Rename chat"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )
          ) : (
            <div className="flex items-center gap-2">
              <span className="font-display font-semibold text-base text-slate-800 dark:text-slate-100">
                New Conversation
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <ModelSelector />
        <ThemeToggle />

        {!user && (
          <button
            onClick={() => openAuthModal('login')}
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-medium text-xs sm:text-sm shadow-sm transition-all"
          >
            Sign In
          </button>
        )}
      </div>
    </header>
  );
};
