import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { cn } from '../../utils/cn';

interface HeaderBarProps {
  title?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  className?: string;
  transparent?: boolean;
}

export function HeaderBar({
  title,
  showBack = true,
  onBack,
  rightAction,
  className,
  transparent = false,
}: HeaderBarProps) {
  const navigation = useNavigation();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else if (navigation.canGoBack()) {
      navigation.goBack();
    }
  };

  return (
    <View
      className={cn(
        'flex-row items-center justify-between px-4 py-3',
        transparent ? 'bg-transparent' : 'bg-background dark:bg-dark',
        className
      )}
    >
      <View className="w-10 items-start">
        {showBack && (
          <TouchableOpacity
            onPress={handleBack}
            className="rounded-full bg-gray-100 p-2 dark:bg-gray-800"
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons name="arrow-back" size={20} className="text-dark dark:text-white" />
          </TouchableOpacity>
        )}
      </View>
      
      <View className="flex-1 items-center justify-center">
        {title && (
          <Text 
            className="text-lg font-bold text-dark dark:text-white" 
            numberOfLines={1}
          >
            {title}
          </Text>
        )}
      </View>
      
      <View className="w-10 items-end">
        {rightAction}
      </View>
    </View>
  );
}
