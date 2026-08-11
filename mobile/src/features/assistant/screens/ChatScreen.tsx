import React, { useState, useEffect, useRef } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  FlatList, 
  KeyboardAvoidingView, 
  Platform,
  ActivityIndicator,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { ChatAPI, ChatMessage } from '../../../api/chat.api';
import { useAuthStore } from '../../../store/authStore';

export default function ChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const flatListRef = useRef<FlatList>(null);
  const user = useAuthStore(state => state.user);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await ChatAPI.getHistory();
      setMessages(history);
    } catch (err) {
      console.error('Failed to load chat history', err);
      setError('Could not load conversation history.');
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setError(null);

    try {
      const aiResponse = await ChatAPI.sendMessage(userMessage.content);
      setMessages(prev => [...prev, aiResponse]);
    } catch (err: any) {
      console.error('Chat error:', err);
      // Surface fallback/error gracefully
      const errorMessage = err.response?.status >= 500 
        ? "The AI is currently unavailable. (Rule-based fallback active)"
        : "Sorry, I had trouble processing that request.";
      
      setError(errorMessage);
      
      // Optionally add an error message to the chat
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `[Error] ${errorMessage}`,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isUser = item.role === 'user';
    const isError = item.content.startsWith('[Error]');
    
    return (
      <View className={`flex-row my-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
        {!isUser && (
          <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center mr-2 mt-1">
            <Ionicons name="sparkles" size={16} color="#6366f1" />
          </View>
        )}
        
        <View 
          className={`max-w-[80%] px-4 py-3 rounded-2xl ${
            isUser 
              ? 'bg-primary rounded-tr-sm' 
              : isError
                ? 'bg-red-100 dark:bg-red-900/30 rounded-tl-sm border border-red-200 dark:border-red-800'
                : 'bg-white dark:bg-dark-paper rounded-tl-sm border border-gray-100 dark:border-gray-800'
          }`}
        >
          <Text 
            className={`text-base ${
              isUser 
                ? 'text-white' 
                : isError
                  ? 'text-red-600 dark:text-red-400 font-medium'
                  : 'text-gray-800 dark:text-gray-200'
            }`}
          >
            {isError ? item.content.replace('[Error] ', '') : item.content}
          </Text>
          
          {item.suggestedActions && item.suggestedActions.length > 0 && (
            <View className="mt-3 flex-row flex-wrap gap-2">
              {item.suggestedActions.map((action, idx) => (
                <TouchableOpacity 
                  key={idx}
                  className="bg-primary/10 px-3 py-1.5 rounded-full"
                  onPress={() => setInputText(action)}
                >
                  <Text className="text-primary text-sm font-medium">{action}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <ScreenLayout noScroll>
      <View className="flex-1 px-4 py-2">
        {error && (
          <View className="bg-red-50 dark:bg-red-900/20 p-3 rounded-xl mb-4 border border-red-100 dark:border-red-900/50 flex-row items-center">
            <Ionicons name="alert-circle-outline" size={20} color="#ef4444" />
            <Text className="ml-2 text-red-600 dark:text-red-400 flex-1 text-sm">{error}</Text>
          </View>
        )}
        
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={item => item.id}
          renderItem={renderMessage}
          contentContainerStyle={{ paddingBottom: 20 }}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />

        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
          <View className="flex-row items-end py-3 px-2 mt-2 bg-white/50 dark:bg-dark-paper/50 rounded-3xl border border-gray-200 dark:border-gray-800">
            <TextInput
              className="flex-1 min-h-[44px] max-h-[120px] px-4 py-3 text-base text-gray-900 dark:text-white"
              placeholder="Ask anything or add a routine..."
              placeholderTextColor="#9ca3af"
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
            />
            <TouchableOpacity 
              className={`w-11 h-11 rounded-full items-center justify-center mb-1 mr-1 ${
                inputText.trim() && !isLoading ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-800'
              }`}
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#ffffff" size="small" />
              ) : (
                <Ionicons 
                  name="arrow-up" 
                  size={20} 
                  color={inputText.trim() ? '#ffffff' : '#9ca3af'} 
                />
              )}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </View>
    </ScreenLayout>
  );
}
