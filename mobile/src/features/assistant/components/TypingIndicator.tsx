import React, { useEffect, useRef } from 'react';
import { View, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export function TypingIndicator() {
  const anim1 = useRef(new Animated.Value(0)).current;
  const anim2 = useRef(new Animated.Value(0)).current;
  const anim3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const createAnimation = (anim: Animated.Value, delay: number) => {
      return Animated.sequence([
        Animated.delay(delay),
        Animated.loop(
          Animated.sequence([
            Animated.timing(anim, { toValue: 1, duration: 300, useNativeDriver: true }),
            Animated.timing(anim, { toValue: 0, duration: 300, useNativeDriver: true }),
            Animated.delay(400)
          ])
        )
      ]);
    };

    Animated.parallel([
      createAnimation(anim1, 0),
      createAnimation(anim2, 150),
      createAnimation(anim3, 300),
    ]).start();
  }, []);

  const Dot = ({ anim }: { anim: Animated.Value }) => (
    <Animated.View 
      style={{ 
        opacity: anim.interpolate({ inputRange: [0, 1], outputRange: [0.3, 1] }),
        transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [0, -3] }) }]
      }}
      className="w-2 h-2 rounded-full bg-primary mx-0.5"
    />
  );

  return (
    <View className="flex-row self-start items-end mb-4">
      <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center mr-2">
        <Ionicons name="sparkles" size={16} color="#1677FF" />
      </View>
      <View className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-4 flex-row items-center h-12">
        <Dot anim={anim1} />
        <Dot anim={anim2} />
        <Dot anim={anim3} />
      </View>
    </View>
  );
}
