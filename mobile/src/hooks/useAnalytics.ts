import { useQuery } from '@tanstack/react-query';
import { AnalyticsAPI } from '../api/analytics.api';

export const ANALYTICS_QUERY_KEY = ['analytics'];

export function useAnalytics() {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEY,
    queryFn: () => AnalyticsAPI.getAnalytics(),
    meta: {
      errorMessage: 'Failed to load analytics data',
    },
  });
}
