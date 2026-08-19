import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

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
  
  getHistory: async (): Promise<ChatMessage[]> => {
    // Currently, backend does not have an endpoint to fetch messages in a conversation.
    // Return empty array and let the UI handle the "no history" state.
    return [];
  }
};
