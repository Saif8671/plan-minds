import { useQuery } from '@tanstack/react-query';
import { DashboardAPI } from '../api/dashboard.api';
import { ErrorHandler } from '../errors/errorHandler';

export const DASHBOARD_QUERY_KEY = ['dashboard'];

export function useDashboardData() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: () => DashboardAPI.getDashboardData(),
    meta: {
      errorMessage: 'Failed to load dashboard data',
    },
  });
}
