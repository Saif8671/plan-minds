import { create } from 'zustand';
import { OnboardingProfile } from '../../../types/onboarding.types';
import { PreferencesAPI } from '../../../api/preferences.api';
import { useAuthStore } from '../../../store/authStore';

interface OnboardingState {
  profile: Partial<OnboardingProfile>;
  updateProfile: (data: Partial<OnboardingProfile>) => void;
  submitProfile: () => Promise<void>;
}

export const useOnboardingStore = create<OnboardingState>((set, get) => ({
  profile: {
    workingHours: {
      activeDays: [1, 2, 3, 4, 5],
      startTime: '09:00',
      endTime: '17:00',
    },
    sleepSchedule: {
      bedtime: '23:00',
      wakeUpTime: '07:00',
    },
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    notificationPrefs: {
      reminders: true,
      aiSuggestions: true,
      dailySummary: true,
      weeklyReport: false,
    },
    goals: {
      primaryGoal: 'productivity',
      focusHoursTarget: 4,
    },
  },

  updateProfile: (data) => {
    set((state) => ({
      profile: {
        ...state.profile,
        ...data,
      },
    }));
  },

  submitProfile: async () => {
    try {
      const { profile } = get();
      
      // Map local frontend profile state to backend UserPreferencesUpdate schema
      const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      const workingDays = profile.workingHours?.activeDays?.map((d: number) => dayNames[d - 1]) || [];

      const backendPayload = {
        wake_time: profile.sleepSchedule?.wakeUpTime,
        sleep_time: profile.sleepSchedule?.bedtime,
        work_start: profile.workingHours?.startTime,
        work_end: profile.workingHours?.endTime,
        timezone: profile.timeZone,
        notification_preferences: profile.notificationPrefs,
        working_days: workingDays,
      };

      await PreferencesAPI.updatePreferences(backendPayload);
      // Mark onboarding as complete globally
      useAuthStore.getState().setHasCompletedOnboarding(true);
    } catch (error) {
      console.error('Failed to submit onboarding profile:', error);
      throw error;
    }
  },
}));
