import React, { useEffect } from 'react';
import { View, StyleSheet, DimensionValue } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withSequence,
  withTiming,
} from 'react-native-reanimated';
import { cn } from '../../utils/cn';

interface SkeletonLoaderProps {
  width?: DimensionValue;
  height?: DimensionValue;
  className?: string;
  borderRadius?: number;
  variant?: 'rectangular' | 'circular' | 'text';
}

export function SkeletonLoader({
  width = '100%',
  height = 20,
  className,
  borderRadius,
  variant = 'rectangular',
}: SkeletonLoaderProps) {
  const opacity = useSharedValue(0.3);

  useEffect(() => {
    opacity.value = withRepeat(
      withSequence(
        withTiming(0.7, { duration: 800 }),
        withTiming(0.3, { duration: 800 })
      ),
      -1,
      true
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  const getBorderRadius = () => {
    if (borderRadius !== undefined) return borderRadius;
    if (variant === 'circular') return 9999;
    if (variant === 'text') return 4;
    return 8; // rectangular default
  };

  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius: getBorderRadius(),
        },
        animatedStyle,
      ]}
      className={cn('bg-gray-200 dark:bg-gray-700', className)}
    />
  );
}
