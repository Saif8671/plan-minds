import { apiClient } from './client';

export interface ProfileData {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  subscriptionPlan: 'free' | 'pro';
  joinDate: string;
}

export const ProfileAPI = {
  getProfile: async (): Promise<ProfileData> => {
    const response = await apiClient.get('/users/me');
    return response.data?.data || response.data;
  },
  
  updateProfile: async (data: Partial<ProfileData>): Promise<ProfileData> => {
    const response = await apiClient.patch('/users/me', data);
    return response.data?.data || response.data;
  }
};
