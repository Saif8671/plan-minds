import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../../providers/ThemeProvider';
import { useGamification } from '../../../hooks/useGamification';
import { SkeletonLoader } from '../../../components/common/SkeletonLoader';

export function GamificationWidget() {
  const { colors } = useTheme();
  const { data: stats, isLoading } = useGamification();

  if (isLoading || !stats) {
    return <SkeletonLoader width="100%" height={100} className="rounded-2xl mb-6 mt-4" />;
  }

  const xpPercentage = (stats.currentXP / stats.xpToNextLevel) * 100;

  return (
    <View className="bg-gray-50 dark:bg-gray-800 rounded-3xl p-5 mb-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <View className="flex-row justify-between items-center mb-4">
        <View className="flex-row items-center">
          <View className="bg-primary/20 w-10 h-10 rounded-full items-center justify-center mr-3">
            <Ionicons name="star" size={20} color={colors.primary} />
          </View>
          <View>
            <Text className="text-gray-500 dark:text-gray-400 font-medium text-xs">Current Level</Text>
            <Text className="text-dark dark:text-white font-bold text-lg">Level {stats.level}</Text>
          </View>
        </View>
        <View className="flex-row items-center bg-orange-100 dark:bg-orange-900/30 px-3 py-1.5 rounded-full">
          <Ionicons name="flame" size={16} color="#F97316" />
          <Text className="text-orange-600 dark:text-orange-400 font-bold ml-1">{stats.currentStreak} Day Streak</Text>
        </View>
      </View>
      
      <View className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden mb-2">
        <View 
          className="bg-primary h-full rounded-full" 
          style={{ width: `${xpPercentage}%` }} 
        />
      </View>
      
      <View className="flex-row justify-between">
        <Text className="text-gray-500 dark:text-gray-400 text-xs font-medium">{stats.currentXP} XP</Text>
        <Text className="text-gray-500 dark:text-gray-400 text-xs font-medium">{stats.xpToNextLevel} XP</Text>
      </View>
    </View>
  );
}
