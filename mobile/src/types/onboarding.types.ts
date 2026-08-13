export interface WorkingHours {
  activeDays: number[]; // 0 = Sunday, 1 = Monday, etc.
  startTime: string; // "09:00"
  endTime: string; // "17:00"
}

export interface SleepSchedule {
  bedtime: string; // "23:00"
  wakeUpTime: string; // "07:00"
}

export interface NotificationPreferences {
  reminders: boolean;
  aiSuggestions: boolean;
  dailySummary: boolean;
  weeklyReport: boolean;
  quietHoursStart?: string;
  quietHoursEnd?: string;
}

export interface UserGoals {
  primaryGoal: 'productivity' | 'health' | 'learning' | 'work' | 'personal';
  focusHoursTarget: number;
}

export interface OnboardingProfile {
  workingHours: WorkingHours;
  sleepSchedule: SleepSchedule;
  timeZone: string;
  notificationPrefs: NotificationPreferences;
  goals: UserGoals;
}

export interface UserPreferencesUpdate {
  wake_time?: string;
  sleep_time?: string;
  work_start?: string;
  work_end?: string;
  timezone?: string;
  notification_preferences?: NotificationPreferences;
  working_days?: string[];
}
