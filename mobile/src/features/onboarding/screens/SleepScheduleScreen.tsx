import React, { useState } from 'react';
import { View, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useOnboardingStore } from '../store/onboardingStore';
import { Ionicons } from '@expo/vector-icons';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'SleepSchedule'>;

export default function SleepScheduleScreen() {
  const navigation = useNavigation<NavigationProp>();
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);

  const [bedtime, setBedtime] = useState(profile.sleepSchedule?.bedtime || '23:00');
  const [wakeUpTime, setWakeUpTime] = useState(profile.sleepSchedule?.wakeUpTime || '07:00');

  const handleNext = () => {
    updateProfile({
      sleepSchedule: {
        bedtime,
        wakeUpTime,
      }
    });
    navigation.navigate('TimeZone');
  };

  return (
    <ScreenLayout showBack onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Sleep Schedule
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          We use this to avoid scheduling tasks when you should be resting.
        </Text>

        <View className="flex-row items-center justify-between gap-x-4 mb-12">
          <View className="flex-1 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
            <Text className="text-sm text-gray-500 mb-1">Bedtime</Text>
            <View className="flex-row items-center">
              <Text className="text-xl font-bold text-dark dark:text-white flex-1">{bedtime}</Text>
              <Ionicons name="moon-outline" size={20} color="#7A3EF3" />
            </View>
          </View>
          
          <Ionicons name="swap-horizontal" size={20} color="#94A3B8" />
          
          <View className="flex-1 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
            <Text className="text-sm text-gray-500 mb-1">Wake Up</Text>
            <View className="flex-row items-center">
              <Text className="text-xl font-bold text-dark dark:text-white flex-1">{wakeUpTime}</Text>
              <Ionicons name="sunny-outline" size={20} color="#F59E0B" />
            </View>
          </View>
        </View>

        <View className="items-center justify-center mb-8">
          <View className="w-48 h-48 rounded-full border-4 border-gray-100 dark:border-gray-800 items-center justify-center">
            <Ionicons name="time" size={80} color="#E2E8F0" />
            <Text className="text-gray-400 mt-2">8 Hours</Text>
          </View>
        </View>

        <View className="flex-1 justify-end pb-8">
          <Button title="Continue" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
