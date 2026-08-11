import React from 'react';
import { View, Text } from 'react-native';
import { cn } from '../../utils/cn';

interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  label?: string;
  className?: string;
}

export function Divider({ orientation = 'horizontal', label, className }: DividerProps) {
  const isHorizontal = orientation === 'horizontal';

  if (label && isHorizontal) {
    return (
      <View className={cn("flex-row items-center w-full my-4", className)}>
        <View className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
        <Text className="mx-4 text-sm text-gray-400 dark:text-gray-500 font-medium">
          {label}
        </Text>
        <View className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
      </View>
    );
  }

  return (
    <View
      className={cn(
        'bg-gray-200 dark:bg-gray-700',
        isHorizontal ? 'w-full h-px my-4' : 'h-full w-px mx-4',
        className
      )}
    />
  );
}
