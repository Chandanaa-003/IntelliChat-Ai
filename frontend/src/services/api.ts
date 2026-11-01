
import type {
  AuthResponse,
  Conversation,
  LLMModel,
  Message,
  User,
} from '../types';

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

function getHeaders(
  customHeaders: Record<string, string> = {}
): HeadersInit {
  const token = localStorage.getItem('access_token');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...customHeaders,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function handleError(res: Response, fallback: string) {
  const error = await res.json().catch(() => ({
    detail: fallback,
  }));

  throw new Error(error.detail || fallback);
}

export const api = {
  auth: {
    async register(data: {
      email: string;
      username: string;
      password: string;
    }): Promise<AuthResponse> {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
      });

      if (!res.ok) await handleError(res, 'Registration failed');
      return res.json();
    },

    async login(data: {
      email: string;
      password: string;
    }): Promise<AuthResponse> {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
      });

      if (!res.ok) await handleError(res, 'Login failed');
      return res.json();
    },

    async getMe(): Promise<User> {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: getHeaders(),
      });

      if (!res.ok) await handleError(res, 'Failed to fetch user profile');
      return res.json();
    },
  },

  conversations: {
    async list(search?: string): Promise<Conversation[]> {
      const url = new URL(`${API_BASE}/conversations`);

      if (search) {
        url.searchParams.append('search', search);
      }

      const res = await fetch(url.toString(), {
        headers: getHeaders(),
      });

      if (!res.ok) await handleError(res, 'Failed to load conversations');
      return res.json();
    },

    async create(data: {
      title?: string;
      model?: string;
      system_prompt?: string;
    }): Promise<Conversation> {
      const res = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
      });

      if (!res.ok) await handleError(res, 'Failed to create conversation');
      return res.json();
    },

    async update(
      id: string,
      data: { title?: string; model?: string }
    ): Promise<Conversation> {
      const res = await fetch(`${API_BASE}/conversations/${id}`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify(data),
      });

      if (!res.ok) await handleError(res, 'Failed to update conversation');
      return res.json();
    },

    async delete(id: string): Promise<void> {
      const res = await fetch(`${API_BASE}/conversations/${id}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });

      if (!res.ok) await handleError(res, 'Failed to delete conversation');
    },

    async getMessages(conversationId: string): Promise<Message[]> {
      const res = await fetch(
        `${API_BASE}/conversations/${conversationId}/messages`,
        { headers: getHeaders() }
      );

      if (!res.ok) await handleError(res, 'Failed to load messages');
      return res.json();
    },
  },

  models: {
    async list(): Promise<LLMModel[]> {
      const res = await fetch(`${API_BASE}/models`, {
        headers: getHeaders(),
      });

      if (!res.ok) await handleError(res, 'Failed to load models');
      return res.json();
    },
  },

  chat: {
    async stream(
      payload: {
        conversation_id?: string;
        content: string;
        model?: string;
        system_prompt?: string;
      },
      callbacks: {
        onSession?: (data: any) => void;
        onToken: (token: string) => void;
        onDone: (data: any) => void;
        onError?: (error: string) => void;
      },
      signal?: AbortSignal
    ): Promise<void> {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload),
        signal,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(
          `Streaming failed (${res.status}): ${errorText}`
        );
      }

      await parseSSEStream(res, callbacks);
    },

    async regenerate(
      payload: {
        conversation_id: string;
        model?: string;
      },
      callbacks: {
        onSession?: (data: any) => void;
        onToken: (token: string) => void;
        onDone: (data: any) => void;
        onError?: (error: string) => void;
      },
      signal?: AbortSignal
    ): Promise<void> {
      const res = await fetch(`${API_BASE}/chat/regenerate`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload),
        signal,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(
          `Regeneration failed (${res.status}): ${errorText}`
        );
      }

      await parseSSEStream(res, callbacks);
    },
  },
};

async function parseSSEStream(
  res: Response,
  callbacks: {
    onSession?: (data: any) => void;
    onToken: (token: string) => void;
    onDone: (data: any) => void;
    onError?: (error: string) => void;
  }
): Promise<void> {
  if (!res.body) {
    throw new Error('Response body is null');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');

  let buffer = '';
  let currentEvent = 'token';
  let streamError: string | null = null;

  function processLine(rawLine: string) {
    const line = rawLine.trim();

    if (!line) return;

    if (line.startsWith('event:')) {
      currentEvent = line.substring(6).trim();
      return;
    }

    if (!line.startsWith('data:')) return;

    const dataStr = line.substring(5).trim();

    try {
      const data = JSON.parse(dataStr);

      switch (currentEvent) {
        case 'session':
          callbacks.onSession?.(data);
          break;

        case 'token':
          callbacks.onToken(data.delta || '');
          break;

        case 'done':
          callbacks.onDone(data);
          break;

        case 'error':
          {
            const errorMessage = data.error || 'Unknown stream error';
            streamError = errorMessage;
            callbacks.onError?.(errorMessage);
          }
          break;
      }
    } catch {
      console.warn('Failed to parse SSE data:', dataStr);
    }

    currentEvent = 'token';
  }

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        processLine(line);
      }
    }

    buffer += decoder.decode();

    if (buffer.trim()) {
      processLine(buffer);
    }

    const errorMessage = streamError;
    if (errorMessage !== null) {
      throw new Error(errorMessage);
    }
  } finally {
    reader.releaseLock();
  }
}
