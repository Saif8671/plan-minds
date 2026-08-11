import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';

interface SuggestionChipsProps {
  suggestions: string[];
  onSelect: (text: string) => void;
  disabled?: boolean;
}

export function SuggestionChips({ suggestions, onSelect, disabled }: SuggestionChipsProps) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <View className="mb-4">
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
      >
        {suggestions.map((suggestion, index) => (
          <TouchableOpacity
            key={index}
            disabled={disabled}
            onPress={() => onSelect(suggestion)}
            className="px-4 py-2 bg-primary/10 border border-primary/20 rounded-full"
          >
            <Text className="text-primary font-medium">{suggestion}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}
