import React, { useState } from 'react';
import { View, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useOnboardingStore } from '../store/onboardingStore';
import { Ionicons } from '@expo/vector-icons';
import { SearchBar } from '../../../components/common/SearchBar';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'TimeZone'>;

export default function TimeZoneScreen() {
  const navigation = useNavigation<NavigationProp>();
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);

  const [timeZone, setTimeZone] = useState(profile.timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNext = () => {
    updateProfile({ timeZone });
    navigation.navigate('NotificationPrefs');
  };

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
            <Text className="text-dark dark:text-white font-medium">{timeZone}</Text>
          </View>
        </View>

        <View className="flex-1 justify-end pb-8">
          <Button title="Continue" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
