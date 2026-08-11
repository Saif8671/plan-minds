import React from 'react';
import { TouchableOpacity, View, Text, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface SettingRowProps {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  subtitle?: string;
  value?: string;
  onPress?: () => void;
  isSwitch?: boolean;
  switchValue?: boolean;
  onSwitchChange?: (val: boolean) => void;
  destructive?: boolean;
}

export function SettingRow({ 
  icon, 
  title, 
  subtitle, 
  value, 
  onPress, 
  isSwitch, 
  switchValue, 
  onSwitchChange,
  destructive
}: SettingRowProps) {
  
  const content = (
    <View className="flex-row items-center justify-between py-4 border-b border-gray-100 dark:border-gray-800">
      <View className="flex-row items-center flex-1 pr-4">
        <View className={cn(
          "w-8 h-8 rounded-full items-center justify-center mr-3",
          destructive ? "bg-error/10" : "bg-primary/10"
        )}>
          <Ionicons 
            name={icon} 
            size={18} 
            color={destructive ? "#EF4444" : "#1677FF"} 
          />
        </View>
        <View>
          <Text className={cn(
            "font-medium text-base",
            destructive ? "text-error" : "text-dark dark:text-white"
          )}>
            {title}
          </Text>
          {subtitle && (
            <Text className="text-xs text-gray-500 mt-0.5">{subtitle}</Text>
          )}
        </View>
      </View>
      
      {isSwitch ? (
        <Switch 
          value={switchValue} 
          onValueChange={onSwitchChange}
          trackColor={{ false: '#E2E8F0', true: '#34D399' }}
          thumbColor="#fff"
        />
      ) : (
        <View className="flex-row items-center">
          {value && <Text className="text-gray-400 mr-2">{value}</Text>}
          {!destructive && <Ionicons name="chevron-forward" size={20} color="#94A3B8" />}
        </View>
      )}
    </View>
  );

  if (isSwitch || !onPress) {
    return <View>{content}</View>;
  }

  return (
    <TouchableOpacity onPress={onPress}>
      {content}
    </TouchableOpacity>
  );
}
