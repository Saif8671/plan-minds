import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { CalendarStackParamList } from './types';
import CalendarScreen from '../features/calendar/screens/CalendarScreen';

// Placeholders
const PlaceholderScreen = () => null;

const Stack = createNativeStackNavigator<CalendarStackParamList>();

export default function CalendarNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="CalendarMain" component={CalendarScreen} />
      <Stack.Screen name="EventDetail" component={PlaceholderScreen} />
    </Stack.Navigator>
  );
}
