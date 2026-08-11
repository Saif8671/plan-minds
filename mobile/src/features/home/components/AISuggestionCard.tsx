import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card } from '../../../components/common/Card';
import { AISuggestion } from '../../../api/dashboard.api';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface AISuggestionCardProps {
  suggestion: AISuggestion;
  onApply: (id: string) => void;
  onDismiss: (id: string) => void;
}

export function AISuggestionCard({ suggestion, onApply, onDismiss }: AISuggestionCardProps) {
  const isBreak = suggestion.type === 'break';
  
  return (
    <Card className={cn(
      "mb-6 p-4 border",
      isBreak ? "bg-secondary/5 border-secondary/20" : "bg-primary/5 border-primary/20"
    )}>
      <View className="flex-row items-start mb-3">
        <View className={cn(
          "p-2 rounded-full mr-3",
          isBreak ? "bg-secondary/20" : "bg-primary/20"
        )}>
          <Ionicons 
            name={isBreak ? "cafe" : "sparkles"} 
            size={20} 
            color={isBreak ? "#7A3EF3" : "#1677FF"} 
          />
        </View>
        <View className="flex-1">
          <View className="flex-row items-center mb-1">
            <Text className="text-sm font-bold text-dark dark:text-white mr-2">PlanMinds AI</Text>
            <View className="bg-white/50 dark:bg-black/20 px-2 py-0.5 rounded">
              <Text className="text-[10px] text-gray-500 uppercase font-bold">Suggestion</Text>
            </View>
          </View>
          <Text className="text-base font-bold text-dark dark:text-white mb-1">
            {suggestion.title}
          </Text>
          <Text className="text-sm text-gray-600 dark:text-gray-400">
            {suggestion.description}
          </Text>
        </View>
      </View>

      <View className="flex-row items-center justify-end gap-x-3 mt-2">
        <TouchableOpacity onPress={() => onDismiss(suggestion.id)} className="px-4 py-2">
          <Text className="text-gray-500 font-medium">Dismiss</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          onPress={() => onApply(suggestion.id)} 
          className={cn(
            "px-4 py-2 rounded-lg",
            isBreak ? "bg-secondary" : "bg-primary"
          )}
        >
          <Text className="text-white font-medium">Apply</Text>
        </TouchableOpacity>
      </View>
    </Card>
  );
}
