import React, { forwardRef, useCallback, useMemo } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions } from 'react-native';
import { cn } from '../../utils/cn';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

const { height: SCREEN_HEIGHT } = Dimensions.get('window');

interface BottomSheetProps {
  isVisible: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  snapPoints?: string[]; // e.g., ['50%', '90%']
}

export function BottomSheet({
  isVisible,
  onClose,
  children,
  title,
  snapPoints = ['50%'],
}: BottomSheetProps) {
  const translateY = useSharedValue(SCREEN_HEIGHT);
  const opacity = useSharedValue(0);

  // Parse first snap point to number
  const targetHeight = useMemo(() => {
    const point = snapPoints[0];
    if (point.endsWith('%')) {
      return SCREEN_HEIGHT * (parseFloat(point) / 100);
    }
    return parseFloat(point);
  }, [snapPoints]);

  const show = useCallback(() => {
    translateY.value = withSpring(SCREEN_HEIGHT - targetHeight, {
      damping: 20,
      stiffness: 200,
    });
    opacity.value = withTiming(1, { duration: 200 });
  }, [targetHeight]);

  const hide = useCallback(() => {
    opacity.value = withTiming(0, { duration: 200 });
    translateY.value = withSpring(SCREEN_HEIGHT, {
      damping: 20,
      stiffness: 200,
    }, () => {
      runOnJS(onClose)();
    });
  }, [onClose]);

  React.useEffect(() => {
    if (isVisible) {
      show();
    } else {
      hide();
    }
  }, [isVisible, show, hide]);

  const gesture = Gesture.Pan()
    .onUpdate((event) => {
      const newY = (SCREEN_HEIGHT - targetHeight) + event.translationY;
      if (newY >= (SCREEN_HEIGHT - targetHeight)) {
        translateY.value = newY;
      }
    })
    .onEnd((event) => {
      if (event.translationY > targetHeight / 3 || event.velocityY > 1000) {
        runOnJS(hide)();
      } else {
        translateY.value = withSpring(SCREEN_HEIGHT - targetHeight, {
          damping: 20,
          stiffness: 200,
        });
      }
    });

  const backdropStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  const sheetStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    height: targetHeight,
  }));

  if (!isVisible && translateY.value === SCREEN_HEIGHT) return null;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="box-none" className="z-50">
      {/* Backdrop */}
      <Animated.View
        style={[StyleSheet.absoluteFill, backdropStyle]}
        className="bg-black/50"
      >
        <TouchableOpacity style={StyleSheet.absoluteFill} onPress={hide} activeOpacity={1} />
      </Animated.View>

      {/* Sheet */}
      <GestureDetector gesture={gesture}>
        <Animated.View
          style={[sheetStyle, { position: 'absolute', left: 0, right: 0, bottom: 0 }]}
          className="rounded-t-3xl bg-white dark:bg-gray-900 shadow-xl border-t border-gray-200 dark:border-gray-800"
        >
          {/* Drag Handle */}
          <View className="items-center pt-3 pb-2">
            <View className="h-1.5 w-12 rounded-full bg-gray-300 dark:bg-gray-700" />
          </View>

          {/* Title */}
          {title && (
            <View className="px-6 py-3 border-b border-gray-100 dark:border-gray-800">
              <Text className="text-xl font-bold text-dark dark:text-white text-center">
                {title}
              </Text>
            </View>
          )}

          {/* Content */}
          <View className="flex-1 p-6">
            {children}
          </View>
        </Animated.View>
      </GestureDetector>
    </View>
  );
}
