import React from 'react';
import { View, Text } from 'react-native';
import { cn } from '../../utils/cn';

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  className?: string;
  textClassName?: string;
}

export function Badge({ label, variant = 'primary', size = 'md', className, textClassName }: BadgeProps) {
  const variantClasses = {
    primary: 'bg-primary/10 dark:bg-primary/20',
    success: 'bg-success/10 dark:bg-success/20',
    warning: 'bg-warning/10 dark:bg-warning/20',
    error: 'bg-error/10 dark:bg-error/20',
    info: 'bg-info/10 dark:bg-info/20',
    neutral: 'bg-gray-100 dark:bg-gray-800',
  };

  const textVariantClasses = {
    primary: 'text-primary',
    success: 'text-success',
    warning: 'text-warning',
    error: 'text-error',
    info: 'text-info',
    neutral: 'text-gray-700 dark:text-gray-300',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 rounded-md',
    md: 'px-2.5 py-1 rounded-full',
  };
  
  const textSizeClasses = {
    sm: 'text-[10px]',
    md: 'text-xs',
  };

  return (
    <View
      className={cn(
        'self-start items-center justify-center',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      <Text
        className={cn(
          'font-semibold',
          textVariantClasses[variant],
          textSizeClasses[size],
          textClassName
        )}
      >
        {label}
      </Text>
    </View>
  );
}
