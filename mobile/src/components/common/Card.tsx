import React from 'react';
import { View, ViewProps, TouchableOpacity, TouchableOpacityProps } from 'react-native';
import { cn } from '../../utils/cn';

interface CardProps extends ViewProps {
  className?: string;
  onPress?: TouchableOpacityProps['onPress'];
  activeOpacity?: number;
}

export function Card({ className, onPress, activeOpacity = 0.9, children, ...props }: CardProps) {
  const baseClasses = "bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden";
  
  if (onPress) {
    return (
      <TouchableOpacity 
        className={cn(baseClasses, className)} 
        onPress={onPress} 
        activeOpacity={activeOpacity}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return (
    <View className={cn(baseClasses, className)} {...props}>
      {children}
    </View>
  );
}
