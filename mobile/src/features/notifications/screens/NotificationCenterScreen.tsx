import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface NotificationProps {
  title: string;
  message: string;
  time: string;
  type: 'reminder' | 'system' | 'ai';
  isRead: boolean;
}

const notifications: NotificationProps[] = [
  {
    title: 'Upcoming Meeting',
    message: 'Client Sync starts in 15 minutes. Prepare the presentation.',
    time: 'Just now',
    type: 'reminder',
    isRead: false,
  },
  {
    title: 'Schedule Optimized',
    message: 'PlanMinds AI resolved a conflict between your workout and morning sync.',
    time: '2h ago',
    type: 'ai',
    isRead: false,
  },
  {
    title: 'Daily Goal Reached',
    message: 'You hit your 4-hour focus target! Great job!',
    time: 'Yesterday',
    type: 'system',
    isRead: true,
  },
];

export default function NotificationCenterScreen() {
  const NotificationItem = ({ notif }: { notif: NotificationProps }) => {
    const isReminder = notif.type === 'reminder';
    const isAI = notif.type === 'ai';

    return (
      <TouchableOpacity 
        className={cn(
          "flex-row p-4 border-b border-gray-100 dark:border-gray-800",
          !notif.isRead && "bg-primary/5"
        )}
      >
        <View className={cn(
          "w-10 h-10 rounded-full items-center justify-center mr-3 mt-1",
          isReminder ? "bg-warning/10" : isAI ? "bg-primary/10" : "bg-success/10"
        )}>
          <Ionicons 
            name={isReminder ? "time" : isAI ? "sparkles" : "checkmark-circle"} 
            size={20} 
            color={isReminder ? "#F59E0B" : isAI ? "#1677FF" : "#10B981"} 
          />
        </View>
        <View className="flex-1">
          <View className="flex-row justify-between items-center mb-1">
            <Text className={cn(
              "font-bold text-base",
              !notif.isRead ? "text-dark dark:text-white" : "text-gray-700 dark:text-gray-300"
            )}>
              {notif.title}
            </Text>
            <Text className="text-xs text-gray-400">{notif.time}</Text>
          </View>
          <Text className="text-sm text-gray-500 leading-5">
            {notif.message}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <ScreenLayout showBack padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800 flex-row justify-between items-center">
        <Text className="text-3xl font-bold text-dark dark:text-white">Notifications</Text>
        <TouchableOpacity>
          <Text className="text-primary font-medium">Mark all read</Text>
        </TouchableOpacity>
      </View>

      <ScrollView className="flex-1">
        {notifications.map((notif, i) => (
          <NotificationItem key={i} notif={notif} />
        ))}
      </ScrollView>
    </ScreenLayout>
  );
}
