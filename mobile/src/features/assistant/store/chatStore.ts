import { create } from 'zustand';
import { ChatAPI, ChatMessage } from '../../../api/chat.api';

interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  loadHistory: () => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isTyping: false,
  
  loadHistory: async () => {
    try {
      const history = await ChatAPI.getHistory();
      set({ messages: history });
    } catch (error) {
      console.error('Failed to load chat history', error);
    }
  },
  
  sendMessage: async (text: string) => {
    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    
    // Optimistic update
    set((state) => ({ 
      messages: [...state.messages, userMsg],
      isTyping: true 
    }));
    
    try {
      const response = await ChatAPI.sendMessage(text);
      set((state) => ({ 
        messages: [...state.messages, response],
        isTyping: false 
      }));
    } catch (error) {
      console.error('Failed to send message', error);
      set({ isTyping: false });
      // You could add an error message to the chat here
    }
  }
}));
