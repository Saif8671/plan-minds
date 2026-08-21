import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

// ─── Types ────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggestedActions?: string[];
  actionsTaken?: string[];
}

export interface ChatResponse {
  reply: string;
  suggested_actions?: string[];
  actions_taken?: string[];
}

export interface ParsedRoutine {
  events: any[];
  tasks: any[];
}

export interface AIAnalyzeResponse {
  tasks: any[];
  summary?: string;
}

export interface ConversationSummary {
  id: string;
  title?: string;
  created_at: string;
  last_message_at?: string;
}

export interface AISuggestion {
  type: string;
  message: string;
  confidence?: number;
  data?: Record<string, any>;
}

// ─── API Client ───────────────────────────────────────────────────────

export const ChatAPI = {
  sendMessage: async (message: string, conversationId?: string): Promise<ChatMessage> => {
    try {
      const response = await apiClient.post(ENDPOINTS.AI.CHAT, {
        message,
        conversation_id: conversationId,
      });
      
      const data: ChatResponse = response.data?.data;
      
      return {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: data.reply,
        timestamp: new Date().toISOString(),
        suggestedActions: data.suggested_actions,
        actionsTaken: data.actions_taken,
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  // ── Conversations ─────────────────────────────────────────────────

  listConversations: async (limit: number = 20): Promise<ConversationSummary[]> => {
    const response = await apiClient.get(ENDPOINTS.AI.CHAT_CONVERSATIONS, {
      params: { limit },
    });
    const data = response.data?.data;
    return data?.conversations || [];
  },

  newConversation: async (title?: string): Promise<{ conversation_id: string }> => {
    const params: Record<string, any> = {};
    if (title) params.title = title;
    const response = await apiClient.post(ENDPOINTS.AI.CHAT_NEW, null, { params });
    return response.data?.data || response.data;
  },

  /** @deprecated Use listConversations instead */
  getHistory: async (): Promise<ChatMessage[]> => {
    return [];
  },

  // ── Routine Parsing & Analysis ────────────────────────────────────

  parseRoutine: async (text: string): Promise<ParsedRoutine> => {
    const response = await apiClient.post(ENDPOINTS.AI.PARSE_ROUTINE, { text });
    return response.data?.data || response.data;
  },

  analyzeRoutine: async (
    routine_text: string,
    auto_persist: boolean = false,
  ): Promise<AIAnalyzeResponse> => {
    const response = await apiClient.post(ENDPOINTS.AI.ANALYZE, {
      routine_text,
      auto_persist,
    });
    return response.data?.data || response.data;
  },

  // ── Suggestions ───────────────────────────────────────────────────

  getSuggestions: async (): Promise<AISuggestion[]> => {
    const response = await apiClient.get(ENDPOINTS.AI.SUGGESTIONS);
    const data = response.data?.data;
    return data?.suggestions || [];
  },
};
