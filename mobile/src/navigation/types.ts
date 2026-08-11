import { NavigatorScreenParams } from '@react-navigation/native';

export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  OTPVerification: { email: string };
  ResetPassword: { token: string };
};

export type OnboardingStackParamList = {
  Intro: undefined;
  Permissions: undefined;
  AIIntro: undefined;
  WorkingHours: undefined;
  SleepSchedule: undefined;
  TimeZone: undefined;
  NotificationPrefs: undefined;
  Goals: undefined;
};

export type ScheduleStackParamList = {
  ScheduleMain: undefined;
  TaskDetail: { taskId: string };
  CreateEditSchedule: { date?: string; itemId?: string };
};

export type CalendarStackParamList = {
  CalendarMain: undefined;
  EventDetail: { eventId: string };
};

export type MainTabParamList = {
  Home: undefined;
  Assistant: undefined;
  Schedule: NavigatorScreenParams<ScheduleStackParamList>;
  Insights: undefined;
  Profile: undefined;
};

export type RootStackParamList = {
  Splash: undefined;
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Onboarding: NavigatorScreenParams<OnboardingStackParamList>;
  Main: NavigatorScreenParams<MainTabParamList>;
};
