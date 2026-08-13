import React, { useEffect, useRef } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet } from 'react-native';
import LottieView from 'lottie-react-native';
import { useTheme } from '../../providers/ThemeProvider';
import { Ionicons } from '@expo/vector-icons';

interface LevelUpModalProps {
  visible: boolean;
  level: number;
  onClose: () => void;
}

export function LevelUpModal({ visible, level, onClose }: LevelUpModalProps) {
  const { colors } = useTheme();
  const animationRef = useRef<LottieView>(null);

  useEffect(() => {
    if (visible) {
      animationRef.current?.play();
    }
  }, [visible]);

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <View className="flex-1 bg-black/60 items-center justify-center p-6">
        <View className="bg-white dark:bg-gray-900 w-full rounded-3xl p-6 items-center shadow-lg relative">
          <TouchableOpacity 
            className="absolute top-4 right-4 z-10 w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-full items-center justify-center"
            onPress={onClose}
          >
            <Ionicons name="close" size={20} color={colors.gray[500]} />
          </TouchableOpacity>

          <View className="w-48 h-48 mb-4">
            {/* Replace this with an actual animation JSON later */}
            {/* <LottieView
              ref={animationRef}
              source={require('../../../assets/animations/confetti.json')}
              autoPlay={false}
              loop={false}
              style={{ width: '100%', height: '100%' }}
            /> */}
            <View className="w-full h-full items-center justify-center bg-primary/10 rounded-full border-4 border-primary">
              <Ionicons name="star" size={80} color={colors.primary} />
            </View>
          </View>

          <Text className="text-3xl font-extrabold text-dark dark:text-white mb-2 text-center">
            Level Up!
          </Text>
          <Text className="text-gray-500 dark:text-gray-400 text-center text-lg mb-6">
            Congratulations! You've reached Level {level}. Keep up the great work!
          </Text>

          <TouchableOpacity 
            className="w-full bg-primary py-4 rounded-xl items-center"
            onPress={onClose}
          >
            <Text className="text-white font-bold text-lg">Awesome</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}
