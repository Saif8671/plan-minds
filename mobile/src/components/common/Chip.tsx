import React from 'react';
import { TouchableOpacity, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../utils/cn';

interface ChipProps {
  label: string;
  selected?: boolean;
  onPress?: () => void;
  onRemove?: () => void;
  icon?: keyof typeof Ionicons.glyphMap;
  className?: string;
  disabled?: boolean;
}

export function Chip({
  label,
  selected = false,
  onPress,
  onRemove,
  icon,
  className,
  disabled,
}: ChipProps) {
  const baseClasses = "flex-row items-center rounded-full px-3 py-1.5 border";
  
  const selectedClasses = selected
    ? "bg-primary border-primary"
    : "bg-transparent border-gray-200 dark:border-gray-700";
    
  const textSelectedClasses = selected
    ? "text-white font-medium"
    : "text-gray-700 dark:text-gray-300";

  return (
    <TouchableOpacity
      disabled={disabled || !onPress}
      onPress={onPress}
      activeOpacity={0.7}
      className={cn(
        baseClasses,
        selectedClasses,
        disabled ? "opacity-50" : "",
        className
      )}
    >
      {icon && (
        <Ionicons
          name={icon}
          size={16}
          color={selected ? "#fff" : "#64748B"}
          style={{ marginRight: 6 }}
        />
      )}
      <Text className={cn("text-sm", textSelectedClasses)}>
        {label}
      </Text>
      {onRemove && (
        <TouchableOpacity 
          onPress={onRemove}
          className="ml-2 rounded-full bg-black/10 dark:bg-white/10 p-0.5"
        >
          <Ionicons 
            name="close" 
            size={12} 
            color={selected ? "#fff" : "#94A3B8"} 
          />
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
}
