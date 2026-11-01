import React from 'react';
import { Plus, MessageSquare, Trash2, Search, Sparkles, LogOut, LogIn } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversation,
    selectConversation,
    deleteConversation,
    newChat,
    searchQuery,
    setSearchQuery,
    sidebarOpen,
    setSidebarOpen,
  } = useChat();

  const { user, isAuthenticated, logout, openAuthModal } = useAuth();

  const filtered = conversations.filter(c =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30 lg:hidden"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 w-72 sm:w-80 flex flex-col border-r border-slate-200/80 dark:border-slate-800/80 bg-slate-50 dark:bg-[#0d121f] transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:hidden'
        }`}
      >
        {/* Top Header & Brand */}
        <div className="p-4 flex items-center justify-between border-b border-slate-200/60 dark:border-slate-800/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary-600 to-indigo-500 text-white flex items-center justify-center shadow-md shadow-primary-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <span className="font-display font-bold text-lg text-slate-800 dark:text-white">
              IntelliChat AI
            </span>
          </div>

          <button
            onClick={() => {
              newChat();
              if (window.innerWidth < 1024) setSidebarOpen(false);
            }}
            className="p-2 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200/80 dark:border-slate-700 shadow-sm transition-all hover:scale-105"
            title="New Conversation"
          >
            <Plus className="w-4 h-4 text-primary-500" />
          </button>
        </div>

        {/* New Chat Primary Action */}
        <div className="p-3">
          <button
            onClick={() => {
              newChat();
              if (window.innerWidth < 1024) setSidebarOpen(false);
            }}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-medium text-sm shadow-md shadow-primary-500/20 transition-all hover:shadow-lg active:scale-98"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="px-3 pb-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="px-2 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Conversations
          </div>

          {filtered.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-400">
              {searchQuery ? 'No matching chats found.' : 'No conversations yet.'}
            </div>
          ) : (
            filtered.map((conv) => {
              const isActive = currentConversation?.id === conv.id;
              return (
                <div
                  key={conv.id}
                  onClick={() => {
                    selectConversation(conv.id);
                    if (window.innerWidth < 1024) setSidebarOpen(false);
                  }}
                  className={`group flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition-all ${
                    isActive
                      ? 'bg-primary-500/10 text-primary-600 dark:text-primary-300 font-medium'
                      : 'hover:bg-slate-200/60 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <MessageSquare className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-primary-500' : 'text-slate-400'}`} />
                    <span className="text-xs sm:text-sm truncate">{conv.title}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-500 transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* User Session Footer */}
        <div className="p-3 border-t border-slate-200/60 dark:border-slate-800/60 bg-white/40 dark:bg-slate-900/40">
          {isAuthenticated && user ? (
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-100 dark:bg-slate-800/80">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-full bg-primary-600/20 text-primary-600 dark:text-primary-400 flex items-center justify-center font-semibold text-xs flex-shrink-0">
                  {user.username.slice(0, 2).toUpperCase()}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {user.username}
                  </p>
                  <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => openAuthModal('login')}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 transition-colors"
            >
              <LogIn className="w-4 h-4 text-primary-500" />
              <span>Sign In / Create Account</span>
            </button>
          )}
        </div>
      </aside>
    </>
  );
};
