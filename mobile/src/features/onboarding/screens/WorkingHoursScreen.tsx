import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useOnboardingStore } from '../store/onboardingStore';
import { cn } from '../../../utils/cn';
import { Ionicons } from '@expo/vector-icons';

const DAYS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'WorkingHours'>;

export default function WorkingHoursScreen() {
  const navigation = useNavigation<NavigationProp>();
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);

  const [activeDays, setActiveDays] = useState<number[]>(profile.workingHours?.activeDays || [1, 2, 3, 4, 5]);
  const [startTime, setStartTime] = useState(profile.workingHours?.startTime || '09:00');
  const [endTime, setEndTime] = useState(profile.workingHours?.endTime || '17:00');

  const toggleDay = (index: number) => {
    setActiveDays(prev => 
      prev.includes(index) ? prev.filter(d => d !== index) : [...prev, index].sort()
    );
  };

  const handleNext = () => {
    updateProfile({
      workingHours: {
        activeDays,
        startTime,
        endTime,
      }
    });
    navigation.navigate('SleepSchedule');
  };

  return (
    <ScreenLayout showBack onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Working Hours
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          When do you typically focus on work or studying?
        </Text>

        <Text className="font-bold text-dark dark:text-white mb-4">Active Days</Text>
        <View className="flex-row justify-between mb-8">
          {DAYS.map((day, index) => {
            const isActive = activeDays.includes(index);
            return (
              <TouchableOpacity
                key={index}
                onPress={() => toggleDay(index)}
                className={cn(
                  "w-10 h-10 rounded-full items-center justify-center border",
                  isActive 
                    ? "bg-primary border-primary" 
                    : "bg-transparent border-gray-200 dark:border-gray-700"
                )}
              >
                <Text className={cn("font-bold text-base", isActive ? "text-white" : "text-gray-500 dark:text-gray-400")}>
                  {day}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text className="font-bold text-dark dark:text-white mb-4">Typical Schedule</Text>
        <View className="flex-row items-center justify-between gap-x-4 mb-8">
          <View className="flex-1 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
            <Text className="text-sm text-gray-500 mb-1">Start Time</Text>
            <View className="flex-row items-center">
              <Text className="text-xl font-bold text-dark dark:text-white flex-1">{startTime}</Text>
              <Ionicons name="time-outline" size={20} color="#94A3B8" />
            </View>
          </View>
          
          <Ionicons name="arrow-forward" size={20} color="#94A3B8" />
          
          <View className="flex-1 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
            <Text className="text-sm text-gray-500 mb-1">End Time</Text>
            <View className="flex-row items-center">
              <Text className="text-xl font-bold text-dark dark:text-white flex-1">{endTime}</Text>
              <Ionicons name="time-outline" size={20} color="#94A3B8" />
            </View>
          </View>
        </View>

        <View className="flex-1 justify-end pb-8">
          <Button title="Continue" onPress={handleNext} disabled={activeDays.length === 0} />
        </View>
      </View>
    </ScreenLayout>
  );
}
