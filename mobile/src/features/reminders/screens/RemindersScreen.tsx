import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { useTheme } from '../../../providers/ThemeProvider';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';
import { useReminders } from '../../../hooks/useReminders';
import { format } from 'date-fns';

export default function RemindersScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [activeTab, setActiveTab] = useState<'upcoming' | 'completed' | 'missed'>('upcoming');

  const tabs = [
    { id: 'upcoming', label: 'Upcoming' },
    { id: 'completed', label: 'Completed' },
    { id: 'missed', label: 'Missed' },
  ] as const;

  const { data: reminders = [], isLoading } = useReminders();
  
  const filteredReminders = reminders.filter(r => r.status === activeTab);

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800 flex-row items-center">
        <TouchableOpacity 
          className="mr-4 w-10 h-10 items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-full"
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="close" size={24} color={isDark ? '#fff' : '#000'} />
        </TouchableOpacity>
        <Text className="text-3xl font-bold text-dark dark:text-white flex-1">Reminders</Text>
        <TouchableOpacity className="bg-primary/10 w-10 h-10 rounded-full items-center justify-center">
          <Ionicons name="add" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View className="flex-row px-4 pt-4 pb-2 space-x-2">
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.id}
            onPress={() => setActiveTab(tab.id)}
            className={cn(
              "px-4 py-2 rounded-full border",
              activeTab === tab.id 
                ? "bg-primary border-primary" 
                : "bg-transparent border-gray-200 dark:border-gray-700"
            )}
          >
            <Text 
              className={cn(
                "font-medium",
                activeTab === tab.id 
                  ? "text-white" 
                  : "text-gray-600 dark:text-gray-400"
              )}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView className="flex-1 px-4 py-4">
        {isLoading ? (
          <View className="items-center justify-center py-20">
            <Text className="text-gray-500 font-medium">Loading reminders...</Text>
          </View>
        ) : filteredReminders.length === 0 ? (
          <View className="items-center justify-center py-20">
            <View className="w-16 h-16 rounded-full bg-gray-50 dark:bg-gray-800 items-center justify-center mb-4">
              <Ionicons name="notifications-outline" size={32} color={colors.gray[400]} />
            </View>
            <Text className="text-gray-500 font-medium">No {activeTab} reminders</Text>
          </View>
        ) : (
          filteredReminders.map(reminder => (
            <View key={reminder.id} className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-4 mb-3 border border-gray-100 dark:border-gray-700">
              <View className="flex-row justify-between items-start">
                <View className="flex-1">
                  <Text className="text-dark dark:text-white font-bold text-lg mb-1">{reminder.title}</Text>
                  {reminder.description && (
                    <Text className="text-gray-500 dark:text-gray-400 mb-2">{reminder.description}</Text>
                  )}
                  <View className="flex-row items-center">
                    <Ionicons name="time-outline" size={16} color={colors.primary} />
                    <Text className="text-primary ml-1 text-sm">{format(new Date(reminder.dueDate), 'MMM d, h:mm a')}</Text>
                  </View>
                </View>
                <TouchableOpacity className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 items-center justify-center">
                  <Ionicons name="checkmark" size={16} color={colors.gray[500]} />
                </TouchableOpacity>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </ScreenLayout>
  );
}
