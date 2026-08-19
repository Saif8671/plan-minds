import React, { useRef, useState } from 'react';
import { View, Text, FlatList, Dimensions, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const slides = [
  {
    id: '1',
    title: 'Welcome to PlanMinds',
    description: 'Your intelligent assistant for seamless scheduling and productivity.',
    icon: 'planet',
  },
  {
    id: '2',
    title: 'Smart Scheduling',
    description: 'Let AI automatically organize your tasks around your energy levels and availability.',
    icon: 'calendar',
  },
  {
    id: '3',
    title: 'Stay on Track',
    description: 'Receive gentle nudges and personalized insights to maintain your momentum.',
    icon: 'trending-up',
  },
];

type NavigationProp = NativeStackNavigationProp<OnboardingStackParamList, 'Intro'>;

export default function IntroScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const handleNext = () => {
    if (currentIndex < slides.length - 1) {
      const nextIndex = currentIndex + 1;
      flatListRef.current?.scrollToOffset({ offset: nextIndex * SCREEN_WIDTH, animated: true });
      setCurrentIndex(nextIndex);
    } else {
      navigation.navigate('Permissions');
    }
  };

  const handleSkip = () => {
    navigation.navigate('Permissions');
  };

  const renderItem = ({ item }: { item: typeof slides[0] }) => (
    <View style={{ width: SCREEN_WIDTH }} className="items-center justify-center p-6">
      <View className="mb-8 h-48 w-48 rounded-full bg-primary/10 items-center justify-center">
        <Ionicons name={item.icon as any} size={80} color="#1677FF" />
      </View>
      <Text className="mb-4 text-center text-3xl font-bold text-dark dark:text-white">
        {item.title}
      </Text>
      <Text className="text-center text-lg text-gray-500 dark:text-gray-400">
        {item.description}
      </Text>
    </View>
  );

  return (
    <ScreenLayout padding={false}>
      <View className="flex-row items-center justify-between px-6 pt-6 pb-2">
        <View className="w-16" />
        <View className="flex-row gap-x-2">
          {slides.map((_, index) => (
            <View
              key={index}
              className={cn(
                "h-2 rounded-full",
                currentIndex === index ? "w-6 bg-primary" : "w-2 bg-gray-300 dark:bg-gray-700"
              )}
            />
          ))}
        </View>
        <TouchableOpacity onPress={handleSkip} className="w-16 items-end">
          <Text className="text-gray-500 font-medium">Skip</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={slides}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(e) => {
          const index = Math.round(e.nativeEvent.contentOffset.x / SCREEN_WIDTH);
          setCurrentIndex(index);
        }}
      />

      <View className="p-6">
        <Button
          title={currentIndex === slides.length - 1 ? "Get Started" : "Next"}
          onPress={handleNext}
        />
      </View>
    </ScreenLayout>
  );
}
