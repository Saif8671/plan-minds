import React from 'react';
import { View, Text } from 'react-native';
import { Card } from '../../../components/common/Card';
import { useAuthStore } from '../../../store/authStore';

export function GreetingCard({ metrics }: { metrics?: any }) {
  const user = useAuthStore((state) => state.user);
  
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const name = user?.name?.split(' ')[0] || 'there';

  return (
    <Card className="mb-6 bg-primary p-6 shadow-md border-transparent">
      <View className="mb-4">
        <Text className="text-white/80 text-base font-medium mb-1">{getGreeting()},</Text>
        <Text className="text-white text-3xl font-bold">{name}!</Text>
      </View>
      
      {metrics && (
        <View className="flex-row items-center justify-between bg-white/20 p-4 rounded-xl">
          <View>
            <Text className="text-white/90 text-sm font-medium mb-1">Tasks Completed</Text>
            <Text className="text-white text-2xl font-bold">
              {metrics.tasksCompleted} <Text className="text-white/70 text-lg">/ {metrics.totalTasks}</Text>
            </Text>
          </View>
          <View className="h-10 w-px bg-white/20 mx-4" />
          <View>
            <Text className="text-white/90 text-sm font-medium mb-1">Focus Target</Text>
            <Text className="text-white text-2xl font-bold">
              {metrics.focusHours}h <Text className="text-white/70 text-lg">/ {metrics.focusTarget}h</Text>
            </Text>
          </View>
        </View>
      )}
    </Card>
  );
}
