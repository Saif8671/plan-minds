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
      const response = await apiClient.get<{ data: Reminder[] } | Reminder[]>(ENDPOINTS.REMINDERS.BASE);
      const data = Array.isArray(response.data) ? response.data : response.data.data;
      return data as Reminder[];
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
