import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { NotificationsAPI, NotificationResponse } from '../api/notifications.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export const NOTIFICATIONS_QUERY_KEY = 'notifications';

export function useNotifications(unreadOnly: boolean = false) {
  return useQuery({
    queryKey: [NOTIFICATIONS_QUERY_KEY, unreadOnly],
    queryFn: () => NotificationsAPI.listNotifications(0, 50, unreadOnly),
    meta: {
      errorMessage: 'Failed to load notifications',
    },
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: [NOTIFICATIONS_QUERY_KEY, 'unread-count'],
    queryFn: () => NotificationsAPI.getUnreadCount(),
    refetchInterval: 60_000, // Poll every 60 seconds for badge updates
  });
}

export function useMarkAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => NotificationsAPI.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to mark notification as read'),
  });
}

export function useMarkAllAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => NotificationsAPI.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      toast.success('All Read', 'All notifications marked as read.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to mark all as read'),
  });
}

export function useDeleteNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => NotificationsAPI.deleteNotification(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete notification'),
  });
}
