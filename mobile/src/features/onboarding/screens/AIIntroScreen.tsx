import React from 'react';
import { View, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../../../components/common/Card';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'AIIntro'>;

export default function AIIntroScreen() {
  const navigation = useNavigation<NavigationProp>();

  const handleNext = () => {
    navigation.navigate('WorkingHours');
  };

  return (
    <ScreenLayout showBack onBack={() => navigation.goBack()}>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Meet Your Assistant
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Your personal AI is ready to help you plan. Tell us a bit about your routine to personalize the experience.
        </Text>

        <View className="flex-1 items-center justify-center py-8">
          <Card className="w-full p-4 mb-4 bg-primary/5 border-primary/20">
            <View className="flex-row items-center mb-2">
              <View className="bg-primary rounded-full p-1.5 mr-2">
                <Ionicons name="sparkles" size={14} color="#fff" />
              </View>
              <Text className="font-bold text-dark dark:text-white">PlanMinds AI</Text>
            </View>
            <Text className="text-dark dark:text-white leading-5">
              "Hi there! I'll help you organize your tasks and find the best times to get work done. To get started, I need to know your typical schedule."
            </Text>
          </Card>
          
          <Card className="w-[85%] self-end p-4 bg-gray-100 dark:bg-gray-800 border-transparent">
            <Text className="text-dark dark:text-white leading-5">
              Sounds great! What do you need to know?
            </Text>
          </Card>
        </View>

        <View className="pb-8">
          <Button title="Set up my profile" onPress={handleNext} />
        </View>
      </View>
    </ScreenLayout>
  );
}
