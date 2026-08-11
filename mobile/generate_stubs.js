const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

const screens = {
  onboarding: [
    'WelcomeScreen',
    'PersonalInfoScreen',
    'PermissionsScreen',
    'WorkingHoursScreen',
    'SleepScheduleScreen',
    'GoalsScreen',
    'ReminderPreferencesScreen',
    'CompletionScreen'
  ],
  home: [
    'HomeScreen'
  ],
  schedule: [
    'DailyScreen',
    'WeeklyScreen',
    'TaskDetailsScreen',
    'CreateTaskScreen',
    'EditTaskScreen'
  ],
  assistant: [
    'ChatScreen',
    'ConversationHistoryScreen',
    'AISuggestionsScreen',
    'SchedulePreviewScreen'
  ],
  calendar: [
    'MonthViewScreen',
    'WeekViewScreen',
    'AgendaViewScreen',
    'DayViewScreen'
  ],
  reminders: [
    'UpcomingRemindersScreen',
    'CompletedRemindersScreen',
    'MissedRemindersScreen',
    'SnoozedRemindersScreen'
  ],
  analytics: [
    'ProductivityDashboardScreen',
    'TaskCompletionScreen',
    'WeeklyPerformanceScreen',
    'MonthlyInsightsScreen',
    'StreaksScreen',
    'FocusHoursScreen'
  ],
  profile: [
    'ProfileScreen',
    'AccountScreen',
    'PreferencesScreen',
    'ThemeScreen',
    'NotificationsSettingsScreen',
    'PrivacyScreen',
    'AboutScreen'
  ],
  notifications: [
    'NotificationCenterScreen',
    'NotificationHistoryScreen'
  ]
};

function generateStub(screenName) {
  return `import React from 'react';
import { View, Text } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';

export default function ${screenName}() {
  return (
    <ScreenLayout>
      <View className="flex-1 justify-center items-center">
        <Text className="text-xl font-bold text-dark dark:text-white">${screenName}</Text>
      </View>
    </ScreenLayout>
  );
}
`;
}

for (const [feature, featureScreens] of Object.entries(screens)) {
  const screensDir = path.join(srcDir, 'features', feature, 'screens');
  fs.mkdirSync(screensDir, { recursive: true });

  for (const screenName of featureScreens) {
    const filePath = path.join(screensDir, `${screenName}.tsx`);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, generateStub(screenName), 'utf8');
      console.log(`Created stub for ${feature}/${screenName}`);
    }
  }

  // Create component directory too just in case
  const componentsDir = path.join(srcDir, 'features', feature, 'components');
  fs.mkdirSync(componentsDir, { recursive: true });
}
