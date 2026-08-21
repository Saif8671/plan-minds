import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

// ─── Types ────────────────────────────────────────────────────────────

export interface TaskCreate {
  title: string;
  description?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  estimated_duration?: number;
  due_date?: string;
  fixed_start?: string;
  fixed_end?: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
  reminder_time?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  estimated_duration?: number;
  due_date?: string;
  status?: string;
}

export interface TaskResponse {
  id: string;
  title: string;
  description?: string;
  category?: string;
  priority: string;
  status: string;
  estimated_duration?: number;
  due_date?: string;
  fixed_start?: string;
  fixed_end?: string;
  is_recurring: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── API Client ───────────────────────────────────────────────────────

export const TasksAPI = {
  createTask: async (data: TaskCreate): Promise<TaskResponse> => {
    const response = await apiClient.post(ENDPOINTS.TASKS.BASE, data);
    return response.data?.data || response.data;
  },

  listTasks: async (
    page: number = 1,
    pageSize: number = 20,
    status?: string,
  ): Promise<PaginatedResponse<TaskResponse>> => {
    const params: Record<string, any> = { page, page_size: pageSize };
    if (status) params.status = status;
    const response = await apiClient.get(ENDPOINTS.TASKS.BASE, { params });
    return response.data?.data || response.data;
  },

  getTask: async (taskId: string): Promise<TaskResponse> => {
    const response = await apiClient.get(`${ENDPOINTS.TASKS.BASE}/${taskId}`);
    return response.data?.data || response.data;
  },

  updateTask: async (taskId: string, data: TaskUpdate): Promise<TaskResponse> => {
    const response = await apiClient.patch(`${ENDPOINTS.TASKS.BASE}/${taskId}`, data);
    return response.data?.data || response.data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`${ENDPOINTS.TASKS.BASE}/${taskId}`);
  },

  startTask: async (taskId: string): Promise<TaskResponse> => {
    const response = await apiClient.post(`${ENDPOINTS.TASKS.BASE}/${taskId}/start`);
    return response.data?.data || response.data;
  },

  completeTask: async (taskId: string): Promise<TaskResponse> => {
    const response = await apiClient.patch(`${ENDPOINTS.TASKS.BASE}/${taskId}/complete`);
    return response.data?.data || response.data;
  },

  skipTask: async (taskId: string, reason?: string): Promise<TaskResponse> => {
    const body = reason ? { reason } : undefined;
    const response = await apiClient.post(`${ENDPOINTS.TASKS.BASE}/${taskId}/skip`, body);
    return response.data?.data || response.data;
  },

  logActivity: async (taskId: string, timeSpent: number): Promise<{ message: string }> => {
    const response = await apiClient.post(`${ENDPOINTS.TASKS.BASE}/${taskId}/activity`, {
      time_spent: timeSpent,
    });
    return response.data?.data || response.data;
  },
};
