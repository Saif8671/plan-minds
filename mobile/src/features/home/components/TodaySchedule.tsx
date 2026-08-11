import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card } from '../../../components/common/Card';
import { Task } from '../../../api/dashboard.api';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface TodayScheduleProps {
  tasks: Task[];
  onTaskPress: (taskId: string) => void;
  onSeeAll: () => void;
}

export function TodaySchedule({ tasks, onTaskPress, onSeeAll }: TodayScheduleProps) {
  if (!tasks || tasks.length === 0) return null;

  return (
    <View className="mb-6">
      <View className="flex-row items-center justify-between mb-4">
        <Text className="text-xl font-bold text-dark dark:text-white">Today's Schedule</Text>
        <TouchableOpacity onPress={onSeeAll}>
          <Text className="text-primary font-medium">See All</Text>
        </TouchableOpacity>
      </View>

      <Card className="p-0 overflow-hidden">
        {tasks.map((task, index) => {
          const isLast = index === tasks.length - 1;
          const isCompleted = task.status === 'completed';
          const isActive = task.status === 'in_progress';

          return (
            <TouchableOpacity 
              key={task.id} 
              onPress={() => onTaskPress(task.id)}
              className={cn(
                "flex-row p-4 border-b border-gray-100 dark:border-gray-800 items-center",
                isLast && "border-b-0",
                isActive && "bg-primary/5"
              )}
            >
              <View className="w-16 items-center border-r border-gray-100 dark:border-gray-800 pr-4 mr-4">
                <Text className="text-sm font-bold text-dark dark:text-white">
                  {task.startTime}
                </Text>
                {task.endTime && (
                  <Text className="text-xs text-gray-500 mt-1">{task.endTime}</Text>
                )}
              </View>

              <View className="flex-1">
                <Text className={cn(
                  "font-bold text-base mb-1",
                  isCompleted ? "text-gray-400 line-through" : "text-dark dark:text-white"
                )}>
                  {task.title}
                </Text>
                <View className="flex-row items-center">
                  <View className={cn(
                    "w-2 h-2 rounded-full mr-2",
                    task.priority === 'high' ? "bg-error" : task.priority === 'medium' ? "bg-warning" : "bg-success"
                  )} />
                  <Text className="text-xs text-gray-500 capitalize">{task.priority} Priority</Text>
                </View>
              </View>

              {isCompleted ? (
                <Ionicons name="checkmark-circle" size={24} color="#34D399" />
              ) : isActive ? (
                <View className="bg-primary/10 px-2 py-1 rounded">
                  <Text className="text-primary text-xs font-bold">NOW</Text>
                </View>
              ) : (
                <Ionicons name="chevron-forward" size={20} color="#94A3B8" />
              )}
            </TouchableOpacity>
          );
        })}
      </Card>
    </View>
  );
}
