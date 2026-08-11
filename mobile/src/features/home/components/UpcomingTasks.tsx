import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card } from '../../../components/common/Card';
import { Task } from '../../../api/dashboard.api';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface UpcomingTasksProps {
  tasks: Task[];
  onTaskPress: (taskId: string) => void;
}

export function UpcomingTasks({ tasks, onTaskPress }: UpcomingTasksProps) {
  if (!tasks || tasks.length === 0) return null;

  return (
    <View className="mb-6">
      <Text className="text-xl font-bold text-dark dark:text-white mb-4">Upcoming</Text>

      {tasks.map((task) => (
        <Card 
          key={task.id} 
          className="p-4 mb-3 flex-row items-center justify-between border-transparent"
        >
          <View className="flex-1 mr-4">
            <Text className="font-bold text-dark dark:text-white text-base mb-1">
              {task.title}
            </Text>
            <View className="flex-row items-center">
              <Ionicons name="calendar-outline" size={14} color="#94A3B8" className="mr-1" />
              <Text className="text-xs text-gray-500">
                {task.dueDate}
              </Text>
            </View>
          </View>
          <TouchableOpacity 
            onPress={() => onTaskPress(task.id)}
            className="w-10 h-10 rounded-full bg-gray-50 dark:bg-gray-800 items-center justify-center"
          >
            <Ionicons name="arrow-forward" size={18} color="#1677FF" />
          </TouchableOpacity>
        </Card>
      ))}
    </View>
  );
}
