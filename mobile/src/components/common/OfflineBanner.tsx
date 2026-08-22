import React from 'react';
import { View, Text } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';
import { Ionicons } from '@expo/vector-icons';

export function OfflineBanner() {
  const { isOnline } = useNetworkStatus();
  const insets = useSafeAreaInsets();

  if (isOnline) return null;

  return (
    <View 
      style={{ paddingTop: insets.top }} 
      className="bg-error/90 w-full absolute top-0 z-50 px-4 pb-2"
    >
      <View className="flex-row items-center justify-center pt-2">
        <Ionicons name="cloud-offline" size={16} color="white" className="mr-2" />
        <Text className="text-white font-medium text-sm ml-2">No internet connection</Text>
      </View>
    </View>
  );
}
