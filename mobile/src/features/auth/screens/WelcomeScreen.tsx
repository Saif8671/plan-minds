import React from 'react';
import { View, Text, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Ionicons } from '@expo/vector-icons';

type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Welcome'>;

export default function WelcomeScreen() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <ScreenLayout padding={false}>
      <View className="flex-1 items-center justify-center px-6">
        {/* Placeholder for actual illustration */}
        <View className="mb-8 h-48 w-48 rounded-full bg-primary/10 items-center justify-center">
          <Ionicons name="calendar" size={80} color="#1677FF" />
        </View>

        <Text className="text-4xl font-bold text-dark dark:text-white mb-2 text-center">
          PlanMinds
        </Text>
        <Text className="text-base text-gray-500 dark:text-gray-400 text-center mb-12 px-4">
          Your AI-powered assistant for scheduling and productivity.
        </Text>

        <View className="w-full gap-y-4">
          <Button
            title="Create an Account"
            onPress={() => navigation.navigate('Register')}
          />
          <Button
            title="Log In"
            variant="outline"
            onPress={() => navigation.navigate('Login')}
          />
        </View>
      </View>
    </ScreenLayout>
  );
}
