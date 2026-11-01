export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Conversation {
  id: string;
  user_id?: string | null;
  title: string;
  model: string;
  system_prompt?: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  token_count?: number;
  created_at: string;
  isStreaming?: boolean;
}

export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  is_active: boolean;
  description: string;
}

export type ThemeMode = 'light' | 'dark' | 'system';
