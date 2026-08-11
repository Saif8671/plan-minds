import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface QuickActionsProps {
  onAddEvent: () => void;
  onAskAI: () => void;
  onFocusMode: () => void;
  onReminders?: () => void;
  onCalendar?: () => void;
}

export function QuickActions({ onAddEvent, onAskAI, onFocusMode, onReminders, onCalendar }: QuickActionsProps) {
  return (
    <View className="mb-8 mt-2">
      <Text className="text-xl font-bold text-dark dark:text-white mb-4">Quick Actions</Text>
      
      {/* Row 1 */}
      <View className="flex-row justify-between mb-4">
        <TouchableOpacity 
          onPress={onAddEvent}
          className="flex-1 items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 mr-2"
        >
          <View className="bg-primary/10 p-3 rounded-full mb-2">
            <Ionicons name="add" size={24} color="#1677FF" />
          </View>
          <Text className="text-dark dark:text-white font-medium text-xs text-center">Add Event</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          onPress={onAskAI}
          className="flex-1 items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 mx-2"
        >
          <View className="bg-secondary/10 p-3 rounded-full mb-2">
            <Ionicons name="sparkles" size={24} color="#7A3EF3" />
          </View>
          <Text className="text-dark dark:text-white font-medium text-xs text-center">Ask AI</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          onPress={onFocusMode}
          className="flex-1 items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 ml-2"
        >
          <View className="bg-accent/10 p-3 rounded-full mb-2">
            <Ionicons name="timer" size={24} color="#10B981" />
          </View>
          <Text className="text-dark dark:text-white font-medium text-xs text-center">Focus</Text>
        </TouchableOpacity>
      </View>

      {/* Row 2 */}
      <View className="flex-row justify-between">
        <TouchableOpacity 
          onPress={onCalendar}
          className="flex-1 items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 mr-2"
        >
          <View className="bg-warning/10 p-3 rounded-full mb-2">
            <Ionicons name="calendar" size={24} color="#F59E0B" />
          </View>
          <Text className="text-dark dark:text-white font-medium text-xs text-center">Calendar</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          onPress={onReminders}
          className="flex-1 items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 mx-2"
        >
          <View className="bg-error/10 p-3 rounded-full mb-2">
            <Ionicons name="notifications" size={24} color="#EF4444" />
          </View>
          <Text className="text-dark dark:text-white font-medium text-xs text-center">Reminders</Text>
        </TouchableOpacity>
        
        <View className="flex-1 ml-2" />
      </View>
    </View>
  );
}
