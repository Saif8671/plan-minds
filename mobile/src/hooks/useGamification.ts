import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';

export interface GamificationStats {
  level: number;
  currentXP: number;
  xpToNextLevel: number;
  currentStreak: number;
  longestStreak: number;
  productivityScore: number;
  badges: Array<{ id: string; name: string; icon: string; earnedAt: string }>;
  todayProgress: number; // 0 to 100
}

export function useGamification() {
  return useQuery({
    queryKey: ['gamification'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ data: GamificationStats }>(ENDPOINTS.GAMIFICATION.BASE);
        return response.data.data;
      } catch (error) {
        console.warn('Failed to fetch gamification stats, using mock data');
        return {
          level: 5,
          currentXP: 2450,
          xpToNextLevel: 3000,
          currentStreak: 12,
          longestStreak: 21,
          productivityScore: 85,
          todayProgress: 65,
          badges: [
            { id: '1', name: 'Early Bird', icon: 'sunny', earnedAt: new Date().toISOString() },
            { id: '2', name: 'Task Master', icon: 'checkmark-done', earnedAt: new Date().toISOString() },
            { id: '3', name: 'Focus Guru', icon: 'timer', earnedAt: new Date().toISOString() },
          ],
        } as GamificationStats;
      }
    },
  });
}
