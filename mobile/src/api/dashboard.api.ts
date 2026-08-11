import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

export interface DashboardMetrics {
  tasksCompleted: number;
  totalTasks: number;
  focusHours: number;
  focusTarget: number;
  currentStreak: number;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  startTime?: string;
  endTime?: string;
}

export interface AISuggestion {
  id: string;
  title: string;
  description: string;
  type: 'optimization' | 'break' | 'focus';
}

export interface DashboardData {
  metrics: DashboardMetrics;
  todaySchedule: Task[];
  upcomingTasks: Task[];
  aiSuggestions: AISuggestion[];
}

export const DashboardAPI = {
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await apiClient.get(ENDPOINTS.DASHBOARD.GET);
    return response.data;
  },
};
