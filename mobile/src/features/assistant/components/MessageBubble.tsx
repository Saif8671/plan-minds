import React from 'react';
import { View, Text } from 'react-native';
import { ChatMessage } from '../../../api/chat.api';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <View className={cn(
      "flex-row mb-4 max-w-[85%]",
      isUser ? "self-end justify-end" : "self-start"
    )}>
      {!isUser && (
        <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center mr-2 mt-1">
          <Ionicons name="sparkles" size={16} color="#1677FF" />
        </View>
      )}
      
      <View className={cn(
        "p-4 rounded-2xl",
        isUser 
          ? "bg-primary rounded-tr-sm" 
          : "bg-gray-100 dark:bg-gray-800 rounded-tl-sm"
      )}>
        <Text className={cn(
          "text-base",
          isUser ? "text-white" : "text-dark dark:text-white"
        )}>
          {message.content}
        </Text>
      </View>
    </View>
  );
}
