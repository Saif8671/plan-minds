import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withTiming,
  withDelay,
  runOnJS,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { ToastMessage, useToastStore } from '../../store/toastStore';
import { cn } from '../../utils/cn';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const ToastItem = ({ toast, onRemove }: { toast: ToastMessage; onRemove: (id: string) => void }) => {
  const translateY = useSharedValue(-100);
  const opacity = useSharedValue(0);

  useEffect(() => {
    translateY.value = withSequence(
      withTiming(0, { duration: 300 }),
      withDelay(
        toast.duration || 3000,
        withTiming(-100, { duration: 300 }, () => {
          runOnJS(onRemove)(toast.id);
        })
      )
    );
    opacity.value = withSequence(
      withTiming(1, { duration: 300 }),
      withDelay(toast.duration || 3000, withTiming(0, { duration: 300 }))
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  const config = {
    success: { icon: 'checkmark-circle', color: 'text-success', bg: 'bg-success/10 border-success/20' },
    error: { icon: 'alert-circle', color: 'text-error', bg: 'bg-error/10 border-error/20' },
    warning: { icon: 'warning', color: 'text-warning', bg: 'bg-warning/10 border-warning/20' },
    info: { icon: 'information-circle', color: 'text-info', bg: 'bg-info/10 border-info/20' },
  }[toast.type];

  return (
    <Animated.View
      style={animatedStyle}
      className={cn(
        'mx-4 mb-2 flex-row items-center rounded-xl border p-4 shadow-sm backdrop-blur-md',
        'bg-white/90 dark:bg-gray-800/90 dark:border-gray-700',
        config.bg
      )}
    >
      <Ionicons name={config.icon as any} size={24} className={config.color} />
      <View className="ml-3 flex-1">
        <Text className="text-sm font-bold text-dark dark:text-white">{toast.title}</Text>
        {toast.message && (
          <Text className="mt-0.5 text-xs text-gray-600 dark:text-gray-300">
            {toast.message}
          </Text>
        )}
      </View>
      <TouchableOpacity onPress={() => onRemove(toast.id)}>
        <Ionicons name="close" size={20} className="text-gray-400" />
      </TouchableOpacity>
    </Animated.View>
  );
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();
  const insets = useSafeAreaInsets();

  if (toasts.length === 0) return null;

  return (
    <View 
      className="absolute left-0 right-0 z-50 pointer-events-none"
      style={{ top: Math.max(insets.top, 16) }}
    >
      {toasts.map((toast) => (
        <View key={toast.id} className="pointer-events-auto">
          <ToastItem toast={toast} onRemove={removeToast} />
        </View>
      ))}
    </View>
  );
}
