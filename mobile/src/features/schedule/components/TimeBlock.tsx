import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Task } from '../../../api/dashboard.api';
import { cn } from '../../../utils/cn';

interface TimeBlockProps {
  task: Task;
  onPress: () => void;
  hasConflict?: boolean;
}

export function TimeBlock({ task, onPress, hasConflict }: TimeBlockProps) {
  const isCompleted = task.status === 'completed';
  const isActive = task.status === 'in_progress';
  
  // Calculate height based on duration in minutes (1 hour = 90px height, min 72px)
  const getDurationInMinutes = (start?: string, end?: string): number => {
    if (!start || !end) return 60;
    const [startH, startM] = start.split(':').map(Number);
    const [endH, endM] = end.split(':').map(Number);
    if (isNaN(startH) || isNaN(endH)) return 60;
    const diff = (endH * 60 + (endM || 0)) - (startH * 60 + (startM || 0));
    return diff > 0 ? diff : 60;
  };

  const durationMins = getDurationInMinutes(task.startTime, task.endTime);
  const calculatedHeight = Math.max(72, (durationMins / 60) * 90);

  return (
    <View className="flex-row mb-4">
      <View className="w-16 items-center pr-2">
        <Text className="text-sm font-bold text-dark dark:text-white">
          {task.startTime}
        </Text>
        <Text className="text-xs text-gray-500 mt-1">{task.endTime}</Text>
      </View>
      
      <View className="w-px bg-gray-200 dark:bg-gray-800 mx-2" />
      
      <TouchableOpacity 
        onPress={onPress}
        style={{ minHeight: calculatedHeight }}
        className={cn(
          "flex-1 p-4 rounded-xl border-l-4 justify-between",
          isActive 
            ? "bg-primary/10 border-primary" 
            : isCompleted
              ? "bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700"
              : "bg-white dark:bg-gray-800 border-transparent shadow-sm",
          hasConflict && !isCompleted && "border-l-error bg-error/5"
        )}
      >
        <View className="flex-row items-center justify-between mb-1">
          <Text className={cn(
            "font-bold text-base flex-1",
            isCompleted ? "text-gray-400 line-through" : "text-dark dark:text-white"
          )}>
            {task.title}
          </Text>
          {isCompleted && (
            <Ionicons name="checkmark-circle" size={20} color="#34D399" />
          )}
          {hasConflict && !isCompleted && (
            <Ionicons name="warning" size={20} color="#EF4444" />
          )}
        </View>
        
        {task.description && (
          <Text className="text-sm text-gray-500 mb-2" numberOfLines={2}>
            {task.description}
          </Text>
        )}

        <View className="flex-row items-center mt-1">
          <View className={cn(
            "w-2 h-2 rounded-full mr-2",
            task.priority === 'high' ? "bg-error" : task.priority === 'medium' ? "bg-warning" : "bg-success"
          )} />
          <Text className="text-xs text-gray-500 capitalize">{task.priority} Priority</Text>
        </View>
      </TouchableOpacity>
    </View>
  );
}
