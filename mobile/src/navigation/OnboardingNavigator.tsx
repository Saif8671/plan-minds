import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from './types';
import IntroScreen from '../features/onboarding/screens/IntroScreen';
import PermissionsScreen from '../features/onboarding/screens/PermissionsScreen';
import AIIntroScreen from '../features/onboarding/screens/AIIntroScreen';
import WorkingHoursScreen from '../features/onboarding/screens/WorkingHoursScreen';
import SleepScheduleScreen from '../features/onboarding/screens/SleepScheduleScreen';
import TimeZoneScreen from '../features/onboarding/screens/TimeZoneScreen';
import NotificationPrefsScreen from '../features/onboarding/screens/NotificationPrefsScreen';
import GoalsScreen from '../features/onboarding/screens/GoalsScreen';

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export default function OnboardingNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Intro" component={IntroScreen} />
      <Stack.Screen name="Permissions" component={PermissionsScreen} />
      <Stack.Screen name="AIIntro" component={AIIntroScreen} />
      <Stack.Screen name="WorkingHours" component={WorkingHoursScreen} />
      <Stack.Screen name="SleepSchedule" component={SleepScheduleScreen} />
      <Stack.Screen name="TimeZone" component={TimeZoneScreen} />
      <Stack.Screen name="NotificationPrefs" component={NotificationPrefsScreen} />
      <Stack.Screen name="Goals" component={GoalsScreen} />
    </Stack.Navigator>
  );
}
