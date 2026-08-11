import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useOnboardingStore } from '../store/onboardingStore';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'Goals'>;

const GOAL_OPTIONS = [
  { id: 'productivity', label: 'Boost Productivity', icon: 'rocket-outline', color: '#1677FF' },
  { id: 'health', label: 'Better Work-Life Balance', icon: 'heart-outline', color: '#10B981' },
  { id: 'learning', label: 'More Time for Learning', icon: 'book-outline', color: '#7A3EF3' },
  { id: 'personal', label: 'Organize Personal Life', icon: 'home-outline', color: '#F59E0B' },
] as const;

export default function GoalsScreen() {
  const profile = useOnboardingStore((state) => state.profile);
  const updateProfile = useOnboardingStore((state) => state.updateProfile);
  const submitProfile = useOnboardingStore((state) => state.submitProfile);

  const [primaryGoal, setPrimaryGoal] = useState<any>(profile.goals?.primaryGoal || 'productivity');
  const [focusHoursTarget, setFocusHoursTarget] = useState(profile.goals?.focusHoursTarget || 4);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleComplete = async () => {
    setIsSubmitting(true);
    updateProfile({
      goals: {
        primaryGoal,
        focusHoursTarget,
      },
    });
    
    try {
      await submitProfile();
      // Navigation is handled automatically in RootNavigator based on hasCompletedOnboarding flag
    } catch (error) {
      setIsSubmitting(false);
    }
  };

  return (
    <ScreenLayout showBack scrollable>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Your Goals
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          What are you hoping to achieve with PlanMinds?
        </Text>

        <View className="flex-row flex-wrap justify-between gap-y-4 mb-8">
          {GOAL_OPTIONS.map((goal) => {
            const isSelected = primaryGoal === goal.id;
            return (
              <TouchableOpacity
                key={goal.id}
                onPress={() => setPrimaryGoal(goal.id)}
                className={cn(
                  "w-[48%] aspect-square p-4 rounded-2xl border items-center justify-center",
                  isSelected ? "bg-primary/5 border-primary" : "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                )}
              >
                <View 
                  className="w-12 h-12 rounded-full items-center justify-center mb-3"
                  style={{ backgroundColor: `${goal.color}20` }}
                >
                  <Ionicons name={goal.icon as any} size={24} color={goal.color} />
                </View>
                <Text className="text-center font-bold text-dark dark:text-white">
                  {goal.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text className="text-xl font-bold text-dark dark:text-white mb-2">
          Daily Focus Target
        </Text>
        <Text className="text-sm text-gray-500 mb-4">
          How many hours of deep focus do you want to aim for each day?
        </Text>

        <View className="flex-row items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 mb-12">
          <TouchableOpacity 
            onPress={() => setFocusHoursTarget(Math.max(1, focusHoursTarget - 1))}
            className="w-12 h-12 rounded-full bg-white dark:bg-gray-700 items-center justify-center shadow-sm"
          >
            <Ionicons name="remove" size={24} color="#1677FF" />
          </TouchableOpacity>
          
          <View className="mx-8 items-center w-20">
            <Text className="text-4xl font-bold text-dark dark:text-white">{focusHoursTarget}</Text>
            <Text className="text-gray-500">hours</Text>
          </View>

          <TouchableOpacity 
            onPress={() => setFocusHoursTarget(Math.min(12, focusHoursTarget + 1))}
            className="w-12 h-12 rounded-full bg-white dark:bg-gray-700 items-center justify-center shadow-sm"
          >
            <Ionicons name="add" size={24} color="#1677FF" />
          </TouchableOpacity>
        </View>

        <View className="pb-8">
          <Button 
            title="Complete Setup" 
            onPress={handleComplete} 
            loading={isSubmitting} 
          />
        </View>
      </View>
    </ScreenLayout>
  );
}
