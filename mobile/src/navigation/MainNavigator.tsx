import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { MainTabParamList } from './types';
import HomeScreen from '../features/home/screens/HomeScreen';
import AssistantScreen from '../features/assistant/screens/AssistantScreen';
import ScheduleNavigator from './ScheduleNavigator';
import InsightsScreen from '../features/analytics/screens/InsightsScreen';
import ProfileScreen from '../features/profile/screens/ProfileScreen';
import { useTheme } from '../providers/ThemeProvider';

const Tab = createBottomTabNavigator<MainTabParamList>();

export default function MainNavigator() {
  const { colors, isDark } = useTheme();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.gray[400],
        tabBarStyle: {
          backgroundColor: isDark ? colors.gray[900] : '#ffffff',
          borderTopColor: isDark ? colors.gray[800] : colors.gray[100],
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'help';

          if (route.name === 'Home') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'Assistant') iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
          else if (route.name === 'Schedule') iconName = focused ? 'calendar' : 'calendar-outline';
          else if (route.name === 'Insights') iconName = focused ? 'stats-chart' : 'stats-chart-outline';
          else if (route.name === 'Profile') iconName = focused ? 'person' : 'person-outline';

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Schedule" component={ScheduleNavigator} />
      <Tab.Screen name="Assistant" component={AssistantScreen} />
      <Tab.Screen name="Insights" component={InsightsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
