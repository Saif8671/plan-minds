import React, { useState } from 'react';
import { View, Text, Switch } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Card } from '../../../components/common/Card';
import { useOnboardingStore } from '../store/onboardingStore';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'NotificationPrefs'>;

export default function NotificationPrefsScreen() {
  const navigation = useNavigation<NavigationProp>();
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);

  const [prefs, setPrefs] = useState({
    reminders: profile.notificationPrefs?.reminders ?? true,
    aiSuggestions: profile.notificationPrefs?.aiSuggestions ?? true,
    dailySummary: profile.notificationPrefs?.dailySummary ?? true,
    weeklyReport: profile.notificationPrefs?.weeklyReport ?? false,
  });

  const togglePref = (key: keyof typeof prefs) => {
    setPrefs((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleNext = () => {
    updateProfile({ notificationPrefs: prefs });
    navigation.navigate('Goals');
  };

  const OptionRow = ({ title, description, value, onToggle }: any) => (
    <Card className="p-4 flex-row items-center justify-between mb-4">
      <View className="flex-1 pr-4">
        <Text className="text-lg font-bold text-dark dark:text-white mb-1">{title}</Text>
        <Text className="text-sm text-gray-500">{description}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: '#E2E8F0', true: '#34D399' }}
        thumbColor="#fff"
      />
    </Card>
  );

  return (
    <ScreenLayout showBack scrollable onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Notifications
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Choose what you want to be notified about. You can change these anytime in Settings.
        </Text>

        <OptionRow
          title="Task Reminders"
          description="Get notified before a task begins or is due."
          value={prefs.reminders}
          onToggle={() => togglePref('reminders')}
        />

        <OptionRow
          title="AI Suggestions"
          description="Receive smart tips to optimize your schedule when conflicts occur."
          value={prefs.aiSuggestions}
          onToggle={() => togglePref('aiSuggestions')}
        />

        <OptionRow
          title="Daily Summary"
          description="A morning briefing of your day ahead."
          value={prefs.dailySummary}
          onToggle={() => togglePref('dailySummary')}
        />

        <OptionRow
          title="Weekly Report"
          description="A summary of your productivity and insights at the end of the week."
          value={prefs.weeklyReport}
          onToggle={() => togglePref('weeklyReport')}
        />

        <View className="mt-8 mb-8">
          <Button title="Continue" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
