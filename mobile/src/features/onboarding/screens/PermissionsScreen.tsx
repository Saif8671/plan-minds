import React, { useState } from 'react';
import { View, Text, Switch } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Card } from '../../../components/common/Card';
import { Ionicons } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'Permissions'>;

export default function PermissionsScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [calendarEnabled, setCalendarEnabled] = useState(false);
  
  const [isRequesting, setIsRequesting] = useState(false);

  const requestNotifications = async (value: boolean) => {
    if (value) {
      setIsRequesting(true);
      const { status } = await Notifications.requestPermissionsAsync();
      setNotificationsEnabled(status === 'granted');
      setIsRequesting(false);
    } else {
      setNotificationsEnabled(false);
    }
  };

  const handleNext = () => {
    navigation.navigate('AIIntro');
  };

  return (
    <ScreenLayout showBack onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Almost Ready
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          PlanMinds needs a few permissions to work its magic.
        </Text>

        <Card className="p-4 flex-row items-center justify-between mb-4">
          <View className="flex-1 pr-4">
            <View className="flex-row items-center mb-1">
              <View className="bg-primary/10 p-2 rounded-lg mr-3">
                <Ionicons name="notifications" size={20} color="#1677FF" />
              </View>
              <Text className="text-lg font-bold text-dark dark:text-white">Notifications</Text>
            </View>
            <Text className="text-sm text-gray-500 mt-2">
              Get gentle reminders and scheduling suggestions when you need them.
            </Text>
          </View>
          <Switch 
            value={notificationsEnabled} 
            onValueChange={requestNotifications}
            disabled={isRequesting}
            trackColor={{ false: '#E2E8F0', true: '#34D399' }}
            thumbColor="#fff"
          />
        </Card>

        <Card className="p-4 flex-row items-center justify-between">
          <View className="flex-1 pr-4">
            <View className="flex-row items-center mb-1">
              <View className="bg-secondary/10 p-2 rounded-lg mr-3">
                <Ionicons name="calendar" size={20} color="#7A3EF3" />
              </View>
              <Text className="text-lg font-bold text-dark dark:text-white">Calendar Access</Text>
            </View>
            <Text className="text-sm text-gray-500 mt-2">
              Sync with your local calendar to detect conflicts and optimize your day.
            </Text>
          </View>
          <Switch 
            value={calendarEnabled} 
            onValueChange={setCalendarEnabled}
            trackColor={{ false: '#E2E8F0', true: '#34D399' }}
            thumbColor="#fff"
          />
        </Card>

        <View className="flex-1 justify-end pb-8 pt-4">
          <Button title="Continue" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
