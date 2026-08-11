import React, { useEffect, useRef } from 'react';
import { View, FlatList, KeyboardAvoidingView, Platform, SafeAreaView } from 'react-native';
import { useHeaderHeight } from '@react-navigation/elements';
import { useChatStore } from '../store/chatStore';
import { MessageBubble } from '../components/MessageBubble';
import { TypingIndicator } from '../components/TypingIndicator';
import { ChatInput } from '../components/ChatInput';
import { SuggestionChips } from '../components/SuggestionChips';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { HeaderBar } from '../../../components/common/HeaderBar';

export default function AssistantScreen() {
  const { messages, isTyping, loadHistory, sendMessage } = useChatStore();
  const flatListRef = useRef<FlatList>(null);
  
  // Example suggestions based on state (in reality, driven by AI or context)
  const suggestions = messages.length <= 1 
    ? ["Optimize my schedule", "When is my next break?", "Add a workout at 5pm"]
    : [];

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSend = (text: string) => {
    sendMessage(text);
  };

  return (
    <SafeAreaView className="flex-1 bg-background dark:bg-dark">
      <HeaderBar title="PlanMinds AI" showBack={false} />
      
      <KeyboardAvoidingView 
        style={{ flex: 1 }} 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <MessageBubble message={item} />}
          contentContainerStyle={{ padding: 16, paddingBottom: 20 }}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
          ListFooterComponent={() => isTyping ? <TypingIndicator /> : null}
        />
        
        {!isTyping && suggestions.length > 0 && (
          <SuggestionChips 
            suggestions={suggestions} 
            onSelect={handleSend}
            disabled={isTyping} 
          />
        )}
        
        <ChatInput onSend={handleSend} disabled={isTyping} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
