import { View, Text } from 'react-native';

export default function SplashScreen() {
  return (
    <View className="flex-1 items-center justify-center bg-background">
      <Text className="text-3xl font-bold text-primary">PlanMinds</Text>
      <Text className="text-gray-500 mt-2">Loading...</Text>
    </View>
  );
}
