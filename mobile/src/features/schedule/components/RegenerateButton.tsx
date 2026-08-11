import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

interface RegenerateButtonProps {
  onPress: () => void;
  loading?: boolean;
  conflictCount?: number;
}

export function RegenerateButton({ onPress, loading, conflictCount = 0 }: RegenerateButtonProps) {
  if (conflictCount === 0) return null;

  return (
    <View className="bg-error/10 border border-error/20 p-4 rounded-xl flex-row items-center justify-between mb-6">
      <View className="flex-1 mr-4">
        <View className="flex-row items-center mb-1">
          <Ionicons name="warning" size={16} color="#EF4444" className="mr-2" />
          <Text className="text-error font-bold">{conflictCount} Scheduling Conflicts</Text>
        </View>
        <Text className="text-xs text-error/80">
          Let AI reorganize your schedule to fix these overlaps.
        </Text>
      </View>
      <TouchableOpacity 
        onPress={onPress}
        disabled={loading}
        className={cn(
          "bg-error px-4 py-2 rounded-lg flex-row items-center",
          loading && "opacity-50"
        )}
      >
        <Ionicons name="sparkles" size={16} color="white" className="mr-2" />
        <Text className="text-white font-bold">{loading ? 'Fixing...' : 'Fix It'}</Text>
      </TouchableOpacity>
    </View>
  );
}
