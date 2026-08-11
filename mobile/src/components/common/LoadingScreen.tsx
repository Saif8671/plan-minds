import React from 'react';
import { View, ActivityIndicator, Text } from 'react-native';
import { cn } from '../../utils/cn';

interface LoadingScreenProps {
  message?: string;
  className?: string;
}

export function LoadingScreen({ message = 'Loading...', className }: LoadingScreenProps) {
  return (
    <View className={cn('flex-1 items-center justify-center bg-background dark:bg-dark p-6', className)}>
      <ActivityIndicator size="large" color="#1677FF" className="mb-4" />
      {message && (
        <Text className="text-gray-500 dark:text-gray-400 font-medium text-base text-center">
          {message}
        </Text>
      )}
    </View>
  );
}
