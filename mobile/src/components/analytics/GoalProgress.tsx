import React from 'react';
import { View, Text } from 'react-native';
import { Card } from '../common/Card';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../utils/cn';

interface GoalProgressProps {
  title: string;
  description: string;
  type: 'positive' | 'warning' | 'info';
}

export function GoalProgress({ title, description, type }: GoalProgressProps) {
  const isPositive = type === 'positive';
  const isWarning = type === 'warning';
  
  return (
    <Card className={cn(
      "mb-4 flex-row items-start p-4 border",
      isPositive ? "bg-success/5 border-success/20" : isWarning ? "bg-warning/5 border-warning/20" : "bg-primary/5 border-primary/20"
    )}>
      <View className={cn(
        "w-10 h-10 rounded-full items-center justify-center mr-3 mt-1",
        isPositive ? "bg-success/20" : isWarning ? "bg-warning/20" : "bg-primary/20"
      )}>
        <Ionicons 
          name={isPositive ? "trending-up" : isWarning ? "alert-circle" : "information-circle"} 
          size={20} 
          color={isPositive ? "#10B981" : isWarning ? "#F59E0B" : "#1677FF"} 
        />
      </View>
      <View className="flex-1">
        <Text className="font-bold text-dark dark:text-white text-base mb-1">{title}</Text>
        <Text className="text-sm text-gray-600 dark:text-gray-400 leading-5">{description}</Text>
      </View>
    </Card>
  );
}
