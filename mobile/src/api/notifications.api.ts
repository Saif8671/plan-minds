import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

// ─── Types ────────────────────────────────────────────────────────────

export interface NotificationResponse {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  data?: Record<string, any>;
}

// ─── API Client ───────────────────────────────────────────────────────

export const NotificationsAPI = {
  listNotifications: async (
    skip: number = 0,
    limit: number = 50,
    unreadOnly: boolean = false,
  ): Promise<NotificationResponse[]> => {
    const params: Record<string, any> = { skip, limit, unread_only: unreadOnly };
    const response = await apiClient.get(ENDPOINTS.NOTIFICATIONS.BASE, { params });
    const data = response.data?.data || response.data;
    return Array.isArray(data) ? data : [];
  },

  getUnreadCount: async (): Promise<number> => {
    const response = await apiClient.get(ENDPOINTS.NOTIFICATIONS.UNREAD_COUNT);
    const data = response.data?.data || response.data;
    return data?.unread_count ?? 0;
  },

  markAsRead: async (notificationId: string): Promise<NotificationResponse> => {
    const response = await apiClient.patch(
      `${ENDPOINTS.NOTIFICATIONS.BASE}/${notificationId}/read`,
    );
    return response.data?.data || response.data;
  },

  markAllAsRead: async (): Promise<void> => {
    await apiClient.post(ENDPOINTS.NOTIFICATIONS.READ_ALL);
  },

  deleteNotification: async (notificationId: string): Promise<void> => {
    await apiClient.delete(`${ENDPOINTS.NOTIFICATIONS.BASE}/${notificationId}`);
  },

  subscribePush: async (pushToken: string): Promise<void> => {
    await apiClient.post(`${ENDPOINTS.NOTIFICATIONS.BASE}/push/subscribe`, {
      push_token: pushToken
    });
  },
};
