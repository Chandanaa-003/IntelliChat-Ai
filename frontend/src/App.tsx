import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { Sidebar } from './components/layout/Sidebar';
import { ChatHeader } from './components/chat/ChatHeader';
import { MessageList } from './components/chat/MessageList';
import { ChatInput } from './components/chat/ChatInput';
import { AuthModal } from './components/auth/AuthModal';

const ChatApp: React.FC = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 font-sans">
      <Sidebar />
      <main className="flex-1 flex flex-col h-full min-w-0 relative">
        <ChatHeader />
        <MessageList />
        <ChatInput />
      </main>
      <AuthModal />
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ChatProvider>
          <ChatApp />
        </ChatProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
