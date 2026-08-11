import React from 'react';
import { View, Text } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';

export default function FocusHoursScreen() {
  return (
    <ScreenLayout>
      <View className="flex-1 justify-center items-center">
        <Text className="text-xl font-bold text-dark dark:text-white">FocusHoursScreen</Text>
      </View>
    </ScreenLayout>
  );
}
