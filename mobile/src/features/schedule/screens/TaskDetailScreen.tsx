import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ScheduleStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

type RouteType = RouteProp<ScheduleStackParamList, 'TaskDetail'>;
type NavigationProp = NativeStackNavigationProp<ScheduleStackParamList, 'TaskDetail'>;

export default function TaskDetailScreen() {
  const route = useRoute<RouteType>();
  const navigation = useNavigation<NavigationProp>();
  const { taskId } = route.params;

  // Mock task data for the ID
  const task = {
    id: taskId,
    title: 'Client Meeting Prep',
    description: 'Review the latest designs and prepare the presentation deck for the Acme Corp meeting.',
    status: 'pending',
    priority: 'high',
    startTime: '14:30',
    endTime: '15:30',
    date: 'August 11, 2026',
    category: 'Work'
  };

  return (
    <ScreenLayout showBack scrollable onBack={() => navigation.goBack()}>
      <View className="px-4 pt-6 pb-20 flex-1">
        
        <View className="flex-row items-center justify-between mb-4">
          <View className="bg-primary/10 px-3 py-1 rounded-full">
            <Text className="text-primary font-bold text-xs uppercase">{task.category}</Text>
          </View>
          <View className="flex-row items-center gap-x-3">
            <TouchableOpacity className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center">
              <Ionicons name="pencil" size={20} color="#94A3B8" />
            </TouchableOpacity>
            <TouchableOpacity className="w-10 h-10 rounded-full bg-error/10 items-center justify-center">
              <Ionicons name="trash" size={20} color="#EF4444" />
            </TouchableOpacity>
          </View>
        </View>

        <Text className="text-3xl font-bold text-dark dark:text-white mb-6">
          {task.title}
        </Text>

        <View className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-4 mb-6 border border-gray-100 dark:border-gray-800">
          <View className="flex-row items-center mb-4">
            <View className="w-10 h-10 rounded-full bg-white dark:bg-gray-800 items-center justify-center mr-3 shadow-sm border border-gray-100 dark:border-gray-700">
              <Ionicons name="calendar-outline" size={20} color="#1677FF" />
            </View>
            <View>
              <Text className="text-gray-500 text-xs font-medium uppercase mb-0.5">Date</Text>
              <Text className="text-dark dark:text-white font-bold text-base">{task.date}</Text>
            </View>
          </View>

          <View className="flex-row items-center mb-4">
            <View className="w-10 h-10 rounded-full bg-white dark:bg-gray-800 items-center justify-center mr-3 shadow-sm border border-gray-100 dark:border-gray-700">
              <Ionicons name="time-outline" size={20} color="#7A3EF3" />
            </View>
            <View>
              <Text className="text-gray-500 text-xs font-medium uppercase mb-0.5">Time</Text>
              <Text className="text-dark dark:text-white font-bold text-base">{task.startTime} - {task.endTime}</Text>
            </View>
          </View>

          <View className="flex-row items-center">
            <View className="w-10 h-10 rounded-full bg-white dark:bg-gray-800 items-center justify-center mr-3 shadow-sm border border-gray-100 dark:border-gray-700">
              <Ionicons name="flag-outline" size={20} color="#EF4444" />
            </View>
            <View>
              <Text className="text-gray-500 text-xs font-medium uppercase mb-0.5">Priority</Text>
              <Text className="text-dark dark:text-white font-bold text-base capitalize">{task.priority}</Text>
            </View>
          </View>
        </View>

        <Text className="text-lg font-bold text-dark dark:text-white mb-2">Description</Text>
        <Text className="text-base text-gray-600 dark:text-gray-400 leading-6 mb-8">
          {task.description}
        </Text>

        <Button title="Mark as Completed" leftIcon={<Ionicons name="checkmark" size={20} color="white" />} />
      </View>
    </ScreenLayout>
  );
}
