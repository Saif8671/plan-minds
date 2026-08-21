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

export interface LeaderboardEntry {
  user_id: string;
  name: string;
  level: number;
  xp: number;
  rank: number;
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

export function useLeaderboard(limit: number = 10) {
  return useQuery({
    queryKey: ['gamification', 'leaderboard', limit],
    queryFn: async () => {
      const response = await apiClient.get(ENDPOINTS.GAMIFICATION.LEADERBOARD, {
        params: { limit },
      });
      const data = response.data?.data || response.data;
      return (Array.isArray(data) ? data : []) as LeaderboardEntry[];
    },
    meta: {
      errorMessage: 'Failed to load leaderboard',
    },
  });
}
