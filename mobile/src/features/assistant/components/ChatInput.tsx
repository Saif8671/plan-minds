import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useKeyboard } from '../../../hooks/useKeyboard';

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState('');
  // const { keyboardHeight } = useKeyboard(); // Useful if not using KeyboardAvoidingView

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };

  return (
    <View className="flex-row items-end p-2 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
      <View className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-3xl min-h-[50px] max-h-[120px] px-4 py-3 mr-2">
        <TextInput
          value={text}
          onChangeText={setText}
          placeholder="Ask PlanMinds..."
          placeholderTextColor="#94A3B8"
          multiline
          className="text-base text-dark dark:text-white"
          style={{ paddingTop: 0, paddingBottom: 0 }}
        />
      </View>
      
      <TouchableOpacity 
        onPress={handleSend}
        disabled={!text.trim() || disabled}
        className={`w-[50px] h-[50px] rounded-full items-center justify-center ${
          text.trim() && !disabled ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
        }`}
      >
        <Ionicons 
          name="arrow-up" 
          size={24} 
          color={text.trim() && !disabled ? "white" : "#94A3B8"} 
        />
      </TouchableOpacity>
    </View>
  );
}
