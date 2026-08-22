import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { Task } from './dashboard.api'; // Reuse Task interface

// ─── Types ────────────────────────────────────────────────────────────

export interface ScheduleDay {
  date: string; // YYYY-MM-DD
  tasks: Task[];
  conflicts?: { taskId: string; message: string }[];
}

export interface ScheduleResponse {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  priority: string;
  start_time: string;
  end_time: string;
  status: string;
  category: string;
  date?: string;
  generated_schedule?: any;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  title: string;
  description?: string;
  priority?: string;
  start_time: string;
  end_time: string;
  status?: string;
  category?: string;
}

export interface ScheduleUpdate {
  title?: string;
  status?: string;
}

export interface ScheduleBlockCreate {
  title: string;
  start: string;
  end: string;
  category?: string;
  task_id?: string;
}

export interface ScheduleBlockUpdate {
  title?: string;
  start?: string;
  end?: string;
  category?: string;
}

export interface ScheduleBlockMove {
  new_start: string;
  new_end: string;
}

export interface ScheduleGenerateRequest {
  target_date: string;
  preferences?: Record<string, any>;
}

export interface ScheduleGenerateMultiRequest {
  start_date: string;
  days: number;
  preferences?: Record<string, any>;
}

export interface ValidationResult {
  is_valid: boolean;
  conflicts: { block_ids: string[]; message: string }[];
  warnings: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Helper: transform backend schedule to frontend ScheduleDay ──────

function toScheduleDay(date: string, scheduleResponse: any): ScheduleDay {
  return {
    date,
    tasks: scheduleResponse?.generated_schedule?.blocks?.map((block: any) => ({
      id: block.id,
      title: block.title,
      status: 'pending',
      priority: 'medium',
      startTime: block.start?.substring(0, 5),
      endTime: block.end?.substring(0, 5),
    })) || [],
    conflicts: scheduleResponse?.generated_schedule?.validation?.conflicts?.map((c: any) => ({
      taskId: c.block_ids[0],
      message: c.message
    })) || [],
  };
}

// ─── API Client ───────────────────────────────────────────────────────

export const ScheduleAPI = {
  // ── Existing (connected) ──────────────────────────────────────────

  getDailySchedule: async (date: string): Promise<ScheduleDay> => {
    try {
      const response = await apiClient.get(`${ENDPOINTS.SCHEDULE.DAILY}?date=${date}`);
      const scheduleResponse = response.data?.data;
      return toScheduleDay(date, scheduleResponse);
    } catch (error: any) {
      if (error.response?.status === 404) {
        return { date, tasks: [], conflicts: [] };
      }
      throw error;
    }
  },

  regenerateSchedule: async (date: string): Promise<ScheduleDay> => {
    try {
      const response = await apiClient.post(ENDPOINTS.SCHEDULE.REGENERATE, {
        target_date: date,
        skipped_task_ids: []
      });
      const scheduleResponse = response.data?.data;
      return toScheduleDay(date, scheduleResponse);
    } catch (error) {
      console.error('Failed to regenerate schedule:', error);
      throw error;
    }
  },

  getTaskById: async (taskId: string): Promise<Task & { date?: string; category?: string }> => {
    try {
      const response = await apiClient.get(`${ENDPOINTS.TASKS.BASE}/${taskId}`);
      const t = response.data?.data || response.data;
      return {
        id: t.id || taskId,
        title: t.title || 'Task Details',
        description: t.description || '',
        status: t.status || 'pending',
        priority: t.priority || 'medium',
        startTime: t.startTime || t.start_time || '09:00',
        endTime: t.endTime || t.end_time || '10:00',
        dueDate: t.dueDate || t.due_date,
        date: t.date || 'Today',
        category: t.category || 'General',
      };
    } catch (error) {
      throw error;
    }
  },

  // ── CRUD ──────────────────────────────────────────────────────────

  createSchedule: async (data: ScheduleCreate): Promise<ScheduleResponse> => {
    const response = await apiClient.post(ENDPOINTS.SCHEDULE.BASE, data);
    return response.data?.data || response.data;
  },

  listSchedules: async (
    page: number = 1,
    pageSize: number = 20,
    status?: string,
  ): Promise<PaginatedResponse<ScheduleResponse>> => {
    const params: Record<string, any> = { page, page_size: pageSize };
    if (status) params.status = status;
    const response = await apiClient.get(ENDPOINTS.SCHEDULE.BASE, { params });
    return response.data?.data || response.data;
  },

  getSchedule: async (scheduleId: string): Promise<ScheduleResponse> => {
    const response = await apiClient.get(`${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}`);
    return response.data?.data || response.data;
  },

  updateSchedule: async (scheduleId: string, data: ScheduleUpdate): Promise<ScheduleResponse> => {
    const response = await apiClient.patch(`${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}`, data);
    return response.data?.data || response.data;
  },

  deleteSchedule: async (scheduleId: string): Promise<void> => {
    await apiClient.delete(`${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}`);
  },

  // ── Validation ────────────────────────────────────────────────────

  validateSchedule: async (scheduleId: string, bufferMinutes: number = 5): Promise<ValidationResult> => {
    const response = await apiClient.get(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/validate`,
      { params: { buffer_minutes: bufferMinutes } },
    );
    return response.data?.data || response.data;
  },

  // ── AI Generation ─────────────────────────────────────────────────

  generateSchedule: async (data: ScheduleGenerateRequest): Promise<ScheduleResponse> => {
    const response = await apiClient.post(ENDPOINTS.SCHEDULE.GENERATE, data);
    return response.data?.data || response.data;
  },

  generateMultiDay: async (data: ScheduleGenerateMultiRequest): Promise<ScheduleResponse[]> => {
    const response = await apiClient.post(ENDPOINTS.SCHEDULE.GENERATE_MULTI, data);
    const result = response.data?.data || response.data;
    return Array.isArray(result) ? result : [];
  },

  getWeekSchedule: async (start?: string): Promise<ScheduleResponse[]> => {
    const params: Record<string, any> = {};
    if (start) params.start = start;
    const response = await apiClient.get(ENDPOINTS.SCHEDULE.WEEK, { params });
    const result = response.data?.data || response.data;
    return Array.isArray(result) ? result : [];
  },

  // ── Block CRUD ────────────────────────────────────────────────────

  createBlock: async (scheduleId: string, data: ScheduleBlockCreate): Promise<ScheduleResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks`,
      data,
    );
    return response.data?.data || response.data;
  },

  updateBlock: async (
    scheduleId: string,
    blockId: string,
    data: ScheduleBlockUpdate,
  ): Promise<ScheduleResponse> => {
    const response = await apiClient.patch(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks/${blockId}`,
      data,
    );
    return response.data?.data || response.data;
  },

  moveBlock: async (
    scheduleId: string,
    blockId: string,
    data: ScheduleBlockMove,
  ): Promise<ScheduleResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks/${blockId}/move`,
      data,
    );
    return response.data?.data || response.data;
  },

  splitBlock: async (
    scheduleId: string,
    blockId: string,
    splitAt: string,
  ): Promise<ScheduleResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks/${blockId}/split`,
      { split_at: splitAt },
    );
    return response.data?.data || response.data;
  },

  mergeBlocks: async (
    scheduleId: string,
    blockIds: string[],
    mergedTitle?: string,
  ): Promise<ScheduleResponse> => {
    const response = await apiClient.post(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks/merge`,
      { block_ids: blockIds, merged_title: mergedTitle },
    );
    return response.data?.data || response.data;
  },

  deleteBlock: async (scheduleId: string, blockId: string): Promise<ScheduleResponse> => {
    const response = await apiClient.delete(
      `${ENDPOINTS.SCHEDULE.BASE}/${scheduleId}/blocks/${blockId}`,
    );
    return response.data?.data || response.data;
  },
};
