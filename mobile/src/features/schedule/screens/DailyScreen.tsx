import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { format } from 'date-fns';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { ScheduleAPI, ScheduleDay } from '../../../api/schedule.api';
import { Task } from '../../../api/dashboard.api';

export default function DailyScreen() {
  const [scheduleData, setScheduleData] = useState<ScheduleDay | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const today = format(new Date(), 'yyyy-MM-dd');

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    try {
      setError(null);
      const data = await ScheduleAPI.getDailySchedule(today);
      setScheduleData(data);
    } catch (err) {
      console.error('Failed to load schedule:', err);
      setError('Could not load today\'s schedule.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const onRefresh = () => {
    setIsRefreshing(true);
    loadSchedule();
  };

  const handleRegenerate = async () => {
    setIsLoading(true);
    try {
      const data = await ScheduleAPI.regenerateSchedule(today);
      setScheduleData(data);
    } catch (err) {
      console.error('Regenerate error:', err);
      setError('Failed to regenerate schedule.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderTask = (task: Task, index: number) => {
    const isConflicted = scheduleData?.conflicts?.some(c => c.taskId === task.id);
    const conflictMsg = scheduleData?.conflicts?.find(c => c.taskId === task.id)?.message;

    return (
      <View key={task.id || index} className="mb-4">
        <View className="flex-row items-center mb-1">
          <Text className="text-gray-500 dark:text-gray-400 text-xs w-14">{task.startTime}</Text>
          <View className={`w-3 h-3 rounded-full mx-2 ${isConflicted ? 'bg-red-500' : 'bg-primary'}`} />
          <View className="flex-1 h-[1px] bg-gray-200 dark:bg-gray-800" />
        </View>
        
        <View className="flex-row">
          <View className="w-14" />
          <View className={`w-[2px] ${isConflicted ? 'bg-red-200' : 'bg-gray-200 dark:bg-gray-800'} mx-3`} />
          <View className="flex-1 pb-4">
            <TouchableOpacity 
              className={`p-4 rounded-xl border ${
                isConflicted 
                  ? 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-900/30' 
                  : 'bg-white dark:bg-dark-paper border-gray-100 dark:border-gray-800'
              }`}
            >
              <Text className={`font-semibold text-base mb-1 ${
                isConflicted ? 'text-red-700 dark:text-red-400' : 'text-gray-900 dark:text-white'
              }`}>
                {task.title}
              </Text>
              
              <View className="flex-row justify-between items-center mt-2">
                <Text className={`text-sm ${
                  isConflicted ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'
                }`}>
                  {task.startTime} - {task.endTime}
                </Text>
              </View>

              {isConflicted && (
                <View className="mt-3 bg-red-100 dark:bg-red-900/30 p-2 rounded flex-row items-center">
                  <Ionicons name="warning-outline" size={14} color="#dc2626" />
                  <Text className="text-red-600 dark:text-red-400 text-xs ml-1 flex-1">
                    {conflictMsg || 'Schedule conflict'}
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  return (
    <ScreenLayout>
      <View className="px-4 py-2 flex-row justify-between items-center border-b border-gray-200 dark:border-gray-800 pb-4 mb-4">
        <View>
          <Text className="text-gray-500 dark:text-gray-400 text-sm">{format(new Date(), 'EEEE')}</Text>
          <Text className="text-2xl font-bold text-gray-900 dark:text-white">{format(new Date(), 'MMMM d')}</Text>
        </View>
        <TouchableOpacity 
          className="bg-primary/10 px-4 py-2 rounded-full flex-row items-center"
          onPress={handleRegenerate}
          disabled={isLoading}
        >
          <Ionicons name="refresh" size={16} color="#6366f1" />
          <Text className="text-primary font-medium ml-1">Optimize</Text>
        </TouchableOpacity>
      </View>

      {error && (
        <View className="mx-4 bg-red-50 dark:bg-red-900/20 p-3 rounded-xl mb-4 border border-red-100 dark:border-red-900/50">
          <Text className="text-red-600 dark:text-red-400">{error}</Text>
        </View>
      )}

      {isLoading && !isRefreshing ? (
        <View className="flex-1 justify-center items-center py-20">
          <ActivityIndicator size="large" color="#6366f1" />
          <Text className="text-gray-500 mt-4">Loading your schedule...</Text>
        </View>
      ) : scheduleData?.tasks?.length === 0 ? (
        <View className="flex-1 justify-center items-center py-20 px-4">
          <Ionicons name="calendar-outline" size={48} color="#9ca3af" />
          <Text className="text-gray-900 dark:text-white font-semibold text-lg mt-4 text-center">No schedule for today</Text>
          <Text className="text-gray-500 text-center mt-2">Generate a schedule to get started</Text>
          <TouchableOpacity 
            className="bg-primary px-6 py-3 rounded-xl mt-6"
            onPress={handleRegenerate}
          >
            <Text className="text-white font-medium">Generate Schedule</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView 
          className="flex-1 px-4"
          refreshControl={
            <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
          }
        >
          {scheduleData?.tasks.map((task, index) => renderTask(task, index))}
          <View className="h-20" />
        </ScrollView>
      )}
    </ScreenLayout>
  );
}
