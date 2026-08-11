import React from 'react';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Button } from './Button';
import { cn } from '../../utils/cn';

interface EmptyStateProps {
  icon?: keyof typeof Ionicons.glyphMap;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon = 'folder-open-outline',
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <View className={cn('flex-1 items-center justify-center p-8', className)}>
      <View className="mb-6 rounded-full bg-primary/10 p-6 dark:bg-primary/20">
        <Ionicons name={icon} size={48} color="#1677FF" />
      </View>
      
      <Text className="mb-2 text-center text-xl font-bold text-dark dark:text-white">
        {title}
      </Text>
      
      {description && (
        <Text className="mb-8 text-center text-base text-gray-500 dark:text-gray-400">
          {description}
        </Text>
      )}
      
      {actionLabel && onAction && (
        <Button 
          title={actionLabel} 
          onPress={onAction} 
          className="min-w-[160px]"
        />
      )}
    </View>
  );
}
