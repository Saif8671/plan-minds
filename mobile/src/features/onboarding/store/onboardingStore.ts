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
      
      const formatTime = (time?: string) => {
        if (!time) return undefined;
        // Strip everything except digits and colons
        const clean = time.replace(/[^\d:]/g, '');
        if (!clean) return '09:00'; // Default fallback if no numbers
        
        let h = '09', m = '00';
        if (clean.includes(':')) {
          const parts = clean.split(':');
          h = parts[0].slice(0, 2).padStart(2, '0');
          m = (parts[1] || '00').slice(0, 2).padEnd(2, '0');
        } else {
          if (clean.length <= 2) {
            h = clean.padStart(2, '0');
          } else {
            h = clean.slice(0, 2).padStart(2, '0');
            m = clean.slice(2, 4).padEnd(2, '0');
          }
        }
        
        // Ensure within valid ranges (00-23 and 00-59)
        const hour = Math.min(Math.max(parseInt(h) || 0, 0), 23);
        const minute = Math.min(Math.max(parseInt(m) || 0, 0), 59);
        
        return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      };

      // Map local frontend profile state to backend UserPreferencesUpdate schema
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const workingDays = profile.workingHours?.activeDays?.map((d: number) => dayNames[d]) || [];

      const backendPayload = {
        wake_time: formatTime(profile.sleepSchedule?.wakeUpTime),
        sleep_time: formatTime(profile.sleepSchedule?.bedtime),
        work_start: formatTime(profile.workingHours?.startTime),
        work_end: formatTime(profile.workingHours?.endTime),
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
