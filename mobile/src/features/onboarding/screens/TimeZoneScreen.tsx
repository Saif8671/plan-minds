import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useOnboardingStore } from '../store/onboardingStore';
import { Ionicons } from '@expo/vector-icons';
import { SearchBar } from '../../../components/common/SearchBar';
import { cn } from '../../../utils/cn';

const COMMON_TIMEZONES = [
  'America/Los_Angeles',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Kolkata',
  'Asia/Calcutta',
  'Asia/Dubai',
  'Australia/Sydney',
  'Pacific/Auckland',
  'UTC'
];

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'TimeZone'>;

export default function TimeZoneScreen() {
  const navigation = useNavigation<NavigationProp>();
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);

  const detectedTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const [timeZone, setTimeZone] = useState(profile?.timeZone || detectedTimeZone);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNext = () => {
    updateProfile({ timeZone });
    navigation.navigate('NotificationPrefs');
  };

  const allTimezones = Array.from(new Set([detectedTimeZone, ...COMMON_TIMEZONES])).sort();
  const filteredTimezones = allTimezones.filter(tz => 
    tz.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ScreenLayout showBack onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Time Zone
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Make sure your schedules and reminders are perfectly timed.
        </Text>

        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Search time zones..."
          className="mb-6"
        />

        <View className="bg-primary/10 border border-primary/20 rounded-xl p-4 flex-row items-center mb-6">
          <Ionicons name="globe-outline" size={24} color="#1677FF" className="mr-3" />
          <View className="flex-1 ml-3">
            <Text className="text-sm text-primary font-bold">Detected Time Zone</Text>
            <Text className="text-dark dark:text-white font-medium">{detectedTimeZone}</Text>
          </View>
        </View>

        <View className="flex-1 mb-4">
          <FlatList
            data={filteredTimezones}
            keyExtractor={(item) => item}
            showsVerticalScrollIndicator={false}
            renderItem={({ item }) => (
              <TouchableOpacity
                onPress={() => setTimeZone(item)}
                className={cn(
                  "p-4 border-b border-gray-100 dark:border-gray-800 flex-row items-center justify-between",
                  timeZone === item && "bg-primary/5 rounded-lg border-b-0 mb-1"
                )}
              >
                <Text className={cn(
                  "text-base", 
                  timeZone === item ? "text-primary font-bold" : "text-dark dark:text-white"
                )}>
                  {item}
                </Text>
                {timeZone === item && (
                  <Ionicons name="checkmark-circle" size={20} color="#1677FF" />
                )}
              </TouchableOpacity>
            )}
          />
        </View>

        <View className="pb-8">
          <Button title="Continue" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
