import React from 'react';
import { View, Text, Image } from 'react-native';
import { cn } from '../../utils/cn';

interface AvatarProps {
  url?: string | null;
  name?: string | null;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  isOnline?: boolean;
}

export function Avatar({ url, name, size = 'md', className, isOnline }: AvatarProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 rounded-full',
    md: 'w-12 h-12 rounded-full',
    lg: 'w-16 h-16 rounded-full',
    xl: 'w-24 h-24 rounded-full',
  };

  const textClasses = {
    sm: 'text-xs',
    md: 'text-base',
    lg: 'text-xl',
    xl: 'text-3xl',
  };
  
  const onlineDotSize = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
    xl: 'w-5 h-5',
  };

  const getInitials = (name?: string | null) => {
    if (!name) return '?';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <View className={cn("relative", className)}>
      {url ? (
        <Image
          source={{ uri: url }}
          className={cn('bg-gray-200 dark:bg-gray-700', sizeClasses[size])}
        />
      ) : (
        <View
          className={cn(
            'items-center justify-center bg-primary/10 dark:bg-primary/20',
            sizeClasses[size]
          )}
        >
          <Text className={cn('font-bold text-primary', textClasses[size])}>
            {getInitials(name)}
          </Text>
        </View>
      )}
      
      {isOnline && (
        <View 
          className={cn(
            "absolute bottom-0 right-0 rounded-full bg-success border-2 border-white dark:border-gray-900",
            onlineDotSize[size]
          )}
        />
      )}
    </View>
  );
}
