import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ScheduleStackParamList } from './types';
import ScheduleScreen from '../features/schedule/screens/ScheduleScreen';
import TaskDetailScreen from '../features/schedule/screens/TaskDetailScreen';
import CreateEditScheduleScreen from '../features/schedule/screens/CreateEditScheduleScreen';

const Stack = createNativeStackNavigator<ScheduleStackParamList>();

export default function ScheduleNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ScheduleMain" component={ScheduleScreen} />
      <Stack.Screen name="TaskDetail" component={TaskDetailScreen} />
      <Stack.Screen name="CreateEditSchedule" component={CreateEditScheduleScreen} />
    </Stack.Navigator>
  );
}
