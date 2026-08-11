import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';

export interface Reminder {
  id: string;
  title: string;
  description?: string;
  dueDate: string;
  status: 'upcoming' | 'completed' | 'missed' | 'snoozed';
  createdAt: string;
}

export function useReminders() {
  return useQuery({
    queryKey: ['reminders'],
    queryFn: async () => {
      // Use existing endpoint, but fallback to mock data if it fails
      try {
        const response = await apiClient.get<{ data: Reminder[] }>(ENDPOINTS.REMINDERS.BASE);
        return response.data.data;
      } catch (error) {
        console.warn('Failed to fetch reminders, using mock data', error);
        return [
          {
            id: '1',
            title: 'Prepare for meeting',
            dueDate: new Date().toISOString(),
            status: 'upcoming',
            createdAt: new Date().toISOString(),
          },
          {
            id: '2',
            title: 'Call mom',
            dueDate: new Date(Date.now() - 86400000).toISOString(),
            status: 'missed',
            createdAt: new Date().toISOString(),
          }
        ] as Reminder[];
      }
    },
  });
}

export function useUpdateReminder() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: string, updates: Partial<Reminder> }) => {
      const response = await apiClient.patch<{ data: Reminder }>(`${ENDPOINTS.REMINDERS.BASE}/${id}`, updates);
      return response.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
  });
}
