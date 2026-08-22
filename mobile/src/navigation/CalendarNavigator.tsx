import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { CalendarStackParamList } from './types';
import CalendarScreen from '../features/calendar/screens/CalendarScreen';

import TaskDetailScreen from '../features/schedule/screens/TaskDetailScreen';

const Stack = createNativeStackNavigator<CalendarStackParamList>();

export default function CalendarNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="CalendarMain" component={CalendarScreen} />
      <Stack.Screen name="TaskDetail" component={TaskDetailScreen} />
    </Stack.Navigator>
  );
}
