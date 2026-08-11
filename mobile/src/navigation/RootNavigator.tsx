import { useEffect } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as SplashScreenNative from 'expo-splash-screen';
import { RootStackParamList } from './types';
import { useAuthStore } from '../store/authStore';
import SplashScreen from '../features/auth/screens/SplashScreen';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';
import OnboardingNavigator from './OnboardingNavigator';
import CalendarNavigator from './CalendarNavigator';
import RemindersScreen from '../features/reminders/screens/RemindersScreen';

// Keep the splash screen visible while we fetch resources
SplashScreenNative.preventAutoHideAsync().catch(() => {});

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  const { isAuthenticated, isLoading, hasCompletedOnboarding, hydrate } = useAuthStore();

  useEffect(() => {
    // Run hydration
    hydrate().finally(() => {
      // Hide native splash once state is ready (we'll show our custom splash component if still loading)
      SplashScreenNative.hideAsync().catch(() => {});
    });
  }, [hydrate]);

  if (isLoading) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Splash" component={SplashScreen} />
      </Stack.Navigator>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      ) : !hasCompletedOnboarding ? (
        <Stack.Screen name="Onboarding" component={OnboardingNavigator} />
      ) : (
        <>
          <Stack.Screen name="Main" component={MainNavigator} />
          <Stack.Screen 
            name="Calendar" 
            component={CalendarNavigator} 
            options={{ presentation: 'modal' }} 
          />
          <Stack.Screen 
            name="Reminders" 
            component={RemindersScreen} 
            options={{ presentation: 'modal' }} 
          />
        </>
      )}
    </Stack.Navigator>
  );
}
