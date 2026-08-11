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
    return new Promise((resolve) => setTimeout(() => resolve({
      id: '123',
      name: 'Sarah Jenkins',
      email: 'sarah@example.com',
      subscriptionPlan: 'free',
      joinDate: '2026-01-15'
    }), 500));
  },
  
  updateProfile: async (data: Partial<ProfileData>): Promise<ProfileData> => {
    // await apiClient.patch('/profile', data);
    return new Promise((resolve) => setTimeout(() => resolve({
      id: '123',
      name: data.name || 'Sarah Jenkins',
      email: data.email || 'sarah@example.com',
      subscriptionPlan: 'free',
      joinDate: '2026-01-15'
    }), 800));
  }
};
