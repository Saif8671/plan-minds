import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { OnboardingProfile, UserPreferencesUpdate } from '../types/onboarding.types';

export const PreferencesAPI = {
  getPreferences: async (): Promise<OnboardingProfile> => {
    const response = await apiClient.get(ENDPOINTS.PREFERENCES.GET);
    return response.data?.data;
  },

  updatePreferences: async (data: UserPreferencesUpdate): Promise<void> => {
    await apiClient.patch(ENDPOINTS.PREFERENCES.UPDATE, data);
  },
};
