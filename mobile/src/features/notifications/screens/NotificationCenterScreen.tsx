import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';
import { useNotifications, useMarkAsRead, useMarkAllAsRead } from '../../../hooks/useNotifications';
import { NotificationResponse } from '../../../api/notifications.api';

function getNotificationType(notif: NotificationResponse): 'reminder' | 'system' | 'ai' {
  const type = notif.type?.toLowerCase() || '';
  if (type.includes('reminder')) return 'reminder';
  if (type.includes('ai') || type.includes('schedule')) return 'ai';
  return 'system';
}

function formatTimeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHr = Math.floor(diffMs / 3_600_000);
  const diffDay = Math.floor(diffMs / 86_400_000);

  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay === 1) return 'Yesterday';
  return `${diffDay}d ago`;
}

export default function NotificationCenterScreen() {
  const { data: notifications = [], isLoading, refetch, isRefetching } = useNotifications();
  const markAsRead = useMarkAsRead();
  const markAllAsRead = useMarkAllAsRead();

  const NotificationItem = ({ notif }: { notif: NotificationResponse }) => {
    const type = getNotificationType(notif);
    const isReminder = type === 'reminder';
    const isAI = type === 'ai';

    return (
      <TouchableOpacity
        className={cn(
          "flex-row p-4 border-b border-gray-100 dark:border-gray-800",
          !notif.is_read && "bg-primary/5"
        )}
        onPress={() => {
          if (!notif.is_read) {
            markAsRead.mutate(notif.id);
          }
        }}
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
              !notif.is_read ? "text-dark dark:text-white" : "text-gray-700 dark:text-gray-300"
            )}>
              {notif.title}
            </Text>
            <Text className="text-xs text-gray-400">{formatTimeAgo(notif.created_at)}</Text>
          </View>
          <Text className="text-sm text-gray-500 leading-5">
            {notif.message}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <ScreenLayout showBack padding={false}>
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#1677FF" />
        </View>
      </ScreenLayout>
    );
  }

  return (
    <ScreenLayout showBack padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800 flex-row justify-between items-center">
        <Text className="text-3xl font-bold text-dark dark:text-white">Notifications</Text>
        <TouchableOpacity onPress={() => markAllAsRead.mutate()}>
          <Text className="text-primary font-medium">Mark all read</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        className="flex-1"
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor="#1677FF" />
        }
      >
        {notifications.length === 0 ? (
          <View className="items-center justify-center py-20">
            <Ionicons name="notifications-off-outline" size={48} color="#94A3B8" />
            <Text className="text-gray-400 mt-4 text-base">No notifications yet</Text>
          </View>
        ) : (
          notifications.map((notif) => (
            <NotificationItem key={notif.id} notif={notif} />
          ))
        )}
      </ScrollView>
    </ScreenLayout>
  );
}
