import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

// ─── Types ────────────────────────────────────────────────────────────

export interface RoutineCreate {
  title: string;
  description?: string;
  days_of_week?: number[];
  start_time?: string;
  end_time?: string;
  category?: string;
  priority?: string;
  frequency?: string;
  estimated_duration?: number;
  preferred_time?: string;
  tags?: string[];
  is_active?: boolean;
}

export interface RoutineUpdate {
  title?: string;
  description?: string;
  days_of_week?: number[];
  start_time?: string;
  end_time?: string;
  category?: string;
  priority?: string;
  frequency?: string;
  estimated_duration?: number;
  preferred_time?: string;
  tags?: string[];
  is_active?: boolean;
}

export interface RoutineResponse {
  id: string;
  title: string;
  description?: string;
  days_of_week?: number[];
  start_time?: string;
  end_time?: string;
  category?: string;
  priority: string;
  frequency?: string;
  estimated_duration: number;
  preferred_time?: string;
  tags?: string[];
  is_active: boolean;
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

export const RoutinesAPI = {
  createRoutine: async (data: RoutineCreate): Promise<RoutineResponse> => {
    const response = await apiClient.post(ENDPOINTS.ROUTINES.BASE, data);
    return response.data?.data || response.data;
  },

  listRoutines: async (
    page: number = 1,
    pageSize: number = 20,
    activeOnly: boolean = false,
  ): Promise<PaginatedResponse<RoutineResponse>> => {
    const params: Record<string, any> = { page, page_size: pageSize };
    if (activeOnly) params.active_only = true;
    const response = await apiClient.get(ENDPOINTS.ROUTINES.BASE, { params });
    return response.data?.data || response.data;
  },

  getRoutine: async (routineId: string): Promise<RoutineResponse> => {
    const response = await apiClient.get(`${ENDPOINTS.ROUTINES.BASE}/${routineId}`);
    return response.data?.data || response.data;
  },

  updateRoutine: async (routineId: string, data: RoutineUpdate): Promise<RoutineResponse> => {
    const response = await apiClient.patch(`${ENDPOINTS.ROUTINES.BASE}/${routineId}`, data);
    return response.data?.data || response.data;
  },

  deleteRoutine: async (routineId: string): Promise<void> => {
    await apiClient.delete(`${ENDPOINTS.ROUTINES.BASE}/${routineId}`);
  },
};
