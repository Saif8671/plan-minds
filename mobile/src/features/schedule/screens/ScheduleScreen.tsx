import React, { useState } from 'react';
import { View, Text, ScrollView, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ScheduleStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { SkeletonLoader } from '../../../components/common/SkeletonLoader';
import { EmptyState } from '../../../components/common/EmptyState';
import { useDailySchedule, useRegenerateSchedule } from '../../../hooks/useSchedule';
import { TimeBlock } from '../components/TimeBlock';
import { RegenerateButton } from '../components/RegenerateButton';
import { format } from 'date-fns';

type NavigationProp = NativeStackNavigationProp<ScheduleStackParamList, 'ScheduleMain'>;

export default function ScheduleScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  
  const { data, isLoading, refetch, isRefetching } = useDailySchedule(selectedDate);
  const { mutate: regenerate, isPending: isRegenerating } = useRegenerateSchedule();

  const conflictCount = data?.conflicts?.length || 0;

  const handleTaskPress = (taskId: string) => {
    navigation.navigate('TaskDetail', { taskId });
  };

  const handleRegenerate = () => {
    regenerate(selectedDate);
  };

  if (isLoading) {
    return (
      <ScreenLayout>
        <View className="pt-4 px-4">
          <SkeletonLoader width="60%" height={32} className="mb-2" />
          <SkeletonLoader width="40%" height={20} className="mb-8" />
          <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-4" />
          <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-4" />
        </View>
      </ScreenLayout>
    );
  }

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-1">
          Schedule
        </Text>
        <Text className="text-base text-gray-500">
          {format(new Date(selectedDate), 'EEEE, MMMM d, yyyy')}
        </Text>
      </View>

      <ScrollView 
        className="flex-1 px-4 pt-6" 
        contentContainerStyle={{ paddingBottom: 100 }}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor="#1677FF" />
        }
      >
        <RegenerateButton 
          conflictCount={conflictCount} 
          loading={isRegenerating} 
          onPress={handleRegenerate} 
        />

        {data?.tasks.map((task) => {
          const hasConflict = data.conflicts?.some(c => c.taskId === task.id);
          return (
            <TimeBlock 
              key={task.id} 
              task={task} 
              hasConflict={hasConflict}
              onPress={() => handleTaskPress(task.id)}
            />
          );
        })}
        
        {data?.tasks.length === 0 && (
          <EmptyState
            icon="calendar-outline"
            title="No tasks scheduled"
            description="You have no tasks scheduled for this day."
          />
        )}
      </ScrollView>
    </ScreenLayout>
  );
}
