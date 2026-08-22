import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';
import { RemindersAPI, ReminderCreate, ReminderUpdate, ReminderResponse } from '../api/reminders.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export { ReminderResponse as Reminder };

export const REMINDERS_QUERY_KEY = 'reminders';

export function useReminders() {
  return useQuery({
    queryKey: [REMINDERS_QUERY_KEY],
    queryFn: () => RemindersAPI.listReminders(),
    meta: {
      errorMessage: 'Failed to load reminders',
    },
  });
}

export function useUpdateReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: ReminderUpdate }) =>
      RemindersAPI.updateReminder(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REMINDERS_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to update reminder'),
  });
}

export function useCreateReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReminderCreate) => RemindersAPI.createReminder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REMINDERS_QUERY_KEY] });
      toast.success('Reminder Created', 'Your reminder has been set.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to create reminder'),
  });
}

export function useSnoozeReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, minutes }: { id: string; minutes: number }) =>
      RemindersAPI.snoozeReminder(id, minutes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REMINDERS_QUERY_KEY] });
      toast.success('Snoozed', 'Reminder has been snoozed.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to snooze reminder'),
  });
}

export function useCompleteReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => RemindersAPI.completeReminder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REMINDERS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['gamification'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to dismiss reminder'),
  });
}

export function useDeleteReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => RemindersAPI.deleteReminder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REMINDERS_QUERY_KEY] });
      toast.success('Reminder Deleted', 'The reminder has been removed.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete reminder'),
  });
}
