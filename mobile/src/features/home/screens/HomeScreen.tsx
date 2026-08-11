import React from 'react';
import { View, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MainTabParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { SkeletonLoader } from '../../../components/common/SkeletonLoader';
import { useDashboardData } from '../../../hooks/useDashboard';
import { GreetingCard } from '../components/GreetingCard';
import { AISuggestionCard } from '../components/AISuggestionCard';
import { TodaySchedule } from '../components/TodaySchedule';
import { UpcomingTasks } from '../components/UpcomingTasks';
import { QuickActions } from '../components/QuickActions';
import { GamificationWidget } from '../components/GamificationWidget';

type NavigationProp = BottomTabNavigationProp<MainTabParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const { data, isLoading, refetch, isRefetching } = useDashboardData();

  if (isLoading) {
    return (
      <ScreenLayout>
        <View className="pt-4">
          <SkeletonLoader width="100%" height={160} className="rounded-2xl mb-6" />
          <SkeletonLoader width={150} height={24} className="mb-4" />
          <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-4" />
          <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-6" />
        </View>
      </ScreenLayout>
    );
  }

  return (
    <ScreenLayout 
      scrollable 
      padding={false}
      refreshing={isRefetching}
      onRefresh={refetch}
    >
      <View className="px-4 pt-6 pb-20">
        <GreetingCard metrics={data?.metrics} />
        <GamificationWidget />

        {data?.aiSuggestions?.map((suggestion) => (
          <AISuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            onApply={() => console.log('Apply', suggestion.id)}
            onDismiss={() => console.log('Dismiss', suggestion.id)}
          />
        ))}

        <TodaySchedule 
          tasks={data?.todaySchedule || []} 
          onTaskPress={(id) => console.log('Task', id)}
          onSeeAll={() => navigation.navigate('Schedule', { screen: 'ScheduleMain' })}
        />

        <QuickActions 
          onAddEvent={() => console.log('Add event')}
          onAskAI={() => navigation.navigate('Assistant')}
          onFocusMode={() => console.log('Focus')}
          onCalendar={() => (navigation.getParent() as any)?.navigate('Calendar')}
          onReminders={() => (navigation.getParent() as any)?.navigate('Reminders')}
        />

        <UpcomingTasks 
          tasks={data?.upcomingTasks || []}
          onTaskPress={(id) => console.log('Upcoming Task', id)}
        />
      </View>
    </ScreenLayout>
  );
}
