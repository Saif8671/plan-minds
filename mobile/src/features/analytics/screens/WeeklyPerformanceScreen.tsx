import React from 'react';
import { View, Text } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';

export default function WeeklyPerformanceScreen() {
  return (
    <ScreenLayout>
      <View className="flex-1 justify-center items-center">
        <Text className="text-xl font-bold text-dark dark:text-white">WeeklyPerformanceScreen</Text>
      </View>
    </ScreenLayout>
  );
}
