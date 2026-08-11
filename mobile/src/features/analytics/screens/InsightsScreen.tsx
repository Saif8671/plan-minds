import React from 'react';
import { View, Text, ScrollView, RefreshControl } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { SkeletonLoader } from '../../../components/common/SkeletonLoader';
import { useAnalytics } from '../../../hooks/useAnalytics';
import { ProductivityChart } from '../../../components/analytics/ProductivityChart';
import { GoalProgress } from '../../../components/analytics/GoalProgress';

export default function InsightsScreen() {
  const { data, isLoading, refetch, isRefetching } = useAnalytics();

  if (isLoading) {
    return (
      <ScreenLayout>
        <View className="pt-4 px-4">
          <SkeletonLoader width="60%" height={32} className="mb-8" />
          <SkeletonLoader width="100%" height={200} className="rounded-2xl mb-6" />
          <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-4" />
        </View>
      </ScreenLayout>
    );
  }

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800">
        <Text className="text-3xl font-bold text-dark dark:text-white">
          Insights
        </Text>
      </View>

      <ScrollView 
        className="flex-1 px-4 pt-6" 
        contentContainerStyle={{ paddingBottom: 100 }}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor="#1677FF" />
        }
      >
        
        <View className="flex-row gap-x-4 mb-6">
          <View className="flex-1 bg-primary/10 rounded-2xl p-4">
            <Text className="text-gray-600 font-medium mb-1">Productivity Score</Text>
            <Text className="text-3xl font-bold text-primary">{data?.weeklyProductivityScore}%</Text>
          </View>
          <View className="flex-1 bg-success/10 rounded-2xl p-4">
            <Text className="text-gray-600 font-medium mb-1">Tasks Done</Text>
            <Text className="text-3xl font-bold text-success">{data?.totalTasksCompleted}</Text>
          </View>
        </View>

        <ProductivityChart data={data?.dailyStats || []} />

        <Text className="text-xl font-bold text-dark dark:text-white mb-4 mt-2">
          AI Observations
        </Text>
        
        {data?.insights.map((insight) => (
          <GoalProgress 
            key={insight.id}
            title={insight.title}
            description={insight.description}
            type={insight.type}
          />
        ))}

      </ScrollView>
    </ScreenLayout>
  );
}
