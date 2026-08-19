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
      const response = await apiClient.get<{ data: GamificationStats } | GamificationStats>(ENDPOINTS.GAMIFICATION.STATS);
      const data = 'data' in response.data ? response.data.data : response.data;
      return data as GamificationStats;
    },
  });
}
