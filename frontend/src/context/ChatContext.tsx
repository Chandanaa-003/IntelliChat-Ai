import React, { createContext, useCallback, useContext, useEffect, useState, useRef } from 'react';
import type { Conversation, LLMModel, Message } from '../types';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  models: LLMModel[];
  selectedModel: string;
  isStreaming: boolean;
  searchQuery: string;
  sidebarOpen: boolean;
  setSearchQuery: (query: string) => void;
  setSelectedModel: (modelId: string) => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  newChat: () => void;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, newTitle: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  regenerateMessage: () => Promise<void>;
  stopStreaming: () => void;
  loadConversations: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);

  const abortControllerRef = useRef<AbortController | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      const list = await api.conversations.list(searchQuery || undefined);
      setConversations(list);
    } catch (err) {
      console.warn('Failed to load conversations', err);
    }
  }, [searchQuery]);

  // Load models on startup
  useEffect(() => {
    async function fetchModels() {
      try {
        const list = await api.models.list();
        setModels(list);
        const defaultModel = list.find(model => model.is_active) || list[0];
        if (defaultModel) {
          setSelectedModel(current => current || defaultModel.id);
        }
      } catch (err) {
        console.warn('Failed to load models list, using default', err);
      }
    }
    fetchModels();
  }, []);

  // Reload conversations when auth state changes
  useEffect(() => {
    loadConversations();
  }, [isAuthenticated, loadConversations]);

  const newChat = () => {
    if (isStreaming) stopStreaming();
    setCurrentConversation(null);
    setMessages([]);
  };

  const selectConversation = async (id: string) => {
    if (isStreaming) stopStreaming();
    try {
      const msgs = await api.conversations.getMessages(id);
      setMessages(msgs);
      const conv = conversations.find(c => c.id === id) || null;
      setCurrentConversation(conv);
      if (conv) {
        setSelectedModel(conv.model);
      }
    } catch (err) {
      console.error('Failed to load conversation messages', err);
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      await api.conversations.delete(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (currentConversation?.id === id) {
        newChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation', err);
    }
  };

  const updateConversationTitle = async (id: string, newTitle: string) => {
    try {
      const updated = await api.conversations.update(id, { title: newTitle });
      setConversations(prev => prev.map(c => (c.id === id ? { ...c, title: updated.title } : c)));
      if (currentConversation?.id === id) {
        setCurrentConversation(prev => (prev ? { ...prev, title: updated.title } : null));
      }
    } catch (err) {
      console.error('Failed to update conversation title', err);
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || isStreaming) return;

    // 1. Add user message optimistically
    const userMsgId = `temp-user-${Date.now()}`;
    const userMessage: Message = {
      id: userMsgId,
      conversation_id: currentConversation?.id || '',
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    };

    // 2. Add assistant placeholder for streaming
    const assistantMsgId = `temp-assistant-${Date.now()}`;
    const assistantPlaceholder: Message = {
      id: assistantMsgId,
      conversation_id: currentConversation?.id || '',
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMessage, assistantPlaceholder]);
    setIsStreaming(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await api.chat.stream(
        {
          conversation_id: currentConversation?.id,
          content: content.trim(),
          model: selectedModel,
        },
        {
          onSession: (meta) => {
            if (!currentConversation) {
              const newConv: Conversation = {
                id: meta.conversation_id,
                title: meta.title,
                model: selectedModel,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                message_count: 2,
              };
              setCurrentConversation(newConv);
              setConversations(prev => [newConv, ...prev]);
            }
          },
          onToken: (token) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId ? { ...m, content: m.content + token } : m
              )
            );
          },
          onDone: (meta) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId
                  ? { ...m, id: meta.message_id, isStreaming: false }
                  : m
              )
            );
            setIsStreaming(false);
            loadConversations();
          },
          onError: (errMsg) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId
                  ? { ...m, content: m.content + `\n\n⚠️ *${errMsg}*`, isStreaming: false }
                  : m
              )
            );
            setIsStreaming(false);
          },
        },
        controller.signal
      );
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Stream failure:', err);
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: m.content || `⚠️ Network error: ${err.message}`, isStreaming: false }
              : m
          )
        );
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const regenerateMessage = async () => {
    if (!currentConversation || isStreaming) return;

    // Remove last assistant message from local state
    setMessages(prev => {
      const last = prev[prev.length - 1];
      if (last && last.role === 'assistant') {
        return prev.slice(0, -1);
      }
      return prev;
    });

    const assistantMsgId = `temp-assistant-regen-${Date.now()}`;
    const assistantPlaceholder: Message = {
      id: assistantMsgId,
      conversation_id: currentConversation.id,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, assistantPlaceholder]);
    setIsStreaming(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await api.chat.regenerate(
        {
          conversation_id: currentConversation.id,
          model: selectedModel,
        },
        {
          onToken: (token) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId ? { ...m, content: m.content + token } : m
              )
            );
          },
          onDone: (meta) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId
                  ? { ...m, id: meta.message_id, isStreaming: false }
                  : m
              )
            );
            setIsStreaming(false);
          },
          onError: (errMsg) => {
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantMsgId
                  ? { ...m, content: m.content + `\n\n⚠️ *${errMsg}*`, isStreaming: false }
                  : m
              )
            );
            setIsStreaming(false);
          },
        },
        controller.signal
      );
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Regenerate failure:', err);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const toggleSidebar = () => setSidebarOpen(prev => !prev);

  return (
    <ChatContext.Provider
      value={{
        conversations,
        currentConversation,
        messages,
        models,
        selectedModel,
        isStreaming,
        searchQuery,
        sidebarOpen,
        setSearchQuery,
        setSelectedModel,
        setSidebarOpen,
        toggleSidebar,
        newChat,
        selectConversation,
        deleteConversation,
        updateConversationTitle,
        sendMessage,
        regenerateMessage,
        stopStreaming,
        loadConversations,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
};
