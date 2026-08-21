import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

// ─── Types ────────────────────────────────────────────────────────────

export interface ReminderCreate {
  title: string;
  description?: string;
  remind_at: string; // ISO datetime
  task_id?: string;
}

export interface ReminderCreateRecurring {
  title: string;
  description?: string;
  remind_at: string;
  recurrence: 'daily' | 'weekly' | 'monthly';
  task_id?: string;
}

export interface ReminderUpdate {
  title?: string;
  description?: string;
  remind_at?: string;
  is_active?: boolean;
}

export interface ReminderResponse {
  id: string;
  title: string;
  description?: string;
  remind_at: string;
  is_sent: boolean;
  is_recurring: boolean;
  recurrence?: string;
  task_id?: string;
  status: 'upcoming' | 'completed' | 'missed' | 'snoozed';
  dueDate: string; // Alias for remind_at, populated by the API transform
  created_at: string;
  updated_at: string;
}

export interface ReminderHistoryEntry {
  id: string;
  reminder_id: string;
  event: string;
  created_at: string;
}

// ─── Normalizer ───────────────────────────────────────────────────────

function normalizeReminder(raw: any): ReminderResponse {
  const remindAt = raw.remind_at || raw.dueDate || raw.created_at;
  let status: ReminderResponse['status'] = 'upcoming';
  if (raw.status) {
    status = raw.status;
  } else if (raw.is_sent) {
    status = 'completed';
  } else if (remindAt && new Date(remindAt) < new Date()) {
    status = 'missed';
  }
  return {
    ...raw,
    status,
    dueDate: remindAt,
  };
}

// ─── API Client ───────────────────────────────────────────────────────

export const RemindersAPI = {
  createReminder: async (data: ReminderCreate): Promise<ReminderResponse> => {
    const response = await apiClient.post(ENDPOINTS.REMINDERS.BASE, data);
    return normalizeReminder(response.data?.data || response.data);
  },

  createRecurringReminder: async (data: ReminderCreateRecurring): Promise<ReminderResponse> => {
    const response = await apiClient.post(ENDPOINTS.REMINDERS.RECURRING, data);
    return normalizeReminder(response.data?.data || response.data);
  },

  generateFromSchedule: async (scheduleId: string): Promise<{ created: number; message: string }> => {
    const response = await apiClient.post(
      `${ENDPOINTS.REMINDERS.GENERATE_FROM_SCHEDULE}/${scheduleId}`,
    );
    return response.data?.data || response.data;
  },

  listReminders: async (
    skip: number = 0,
    limit: number = 50,
    includeSent: boolean = true,
  ): Promise<ReminderResponse[]> => {
    const params: Record<string, any> = { skip, limit, include_sent: includeSent };
    const response = await apiClient.get(ENDPOINTS.REMINDERS.BASE, { params });
    const data = response.data?.data || response.data;
    const list = Array.isArray(data) ? data : [];
    return list.map(normalizeReminder);
  },

  getReminderHistory: async (
    reminderId: string,
    limit: number = 50,
  ): Promise<ReminderHistoryEntry[]> => {
    const response = await apiClient.get(
      `${ENDPOINTS.REMINDERS.BASE}/${reminderId}/history`,
      { params: { limit } },
    );
    const data = response.data?.data || response.data;
    return Array.isArray(data) ? data : [];
  },

  updateReminder: async (reminderId: string, data: ReminderUpdate): Promise<ReminderResponse> => {
    const response = await apiClient.patch(`${ENDPOINTS.REMINDERS.BASE}/${reminderId}`, data);
    return response.data?.data || response.data;
  },

  snoozeReminder: async (reminderId: string, minutes: number): Promise<ReminderResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.REMINDERS.BASE}/${reminderId}/snooze`,
      { snooze_minutes: minutes },
    );
    return response.data?.data || response.data;
  },

  completeReminder: async (reminderId: string): Promise<ReminderResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.REMINDERS.BASE}/${reminderId}/complete`,
    );
    return response.data?.data || response.data;
  },

  deleteReminder: async (reminderId: string): Promise<void> => {
    await apiClient.delete(`${ENDPOINTS.REMINDERS.BASE}/${reminderId}`);
  },
};
