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
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const [analyticsRes, scheduleRes, tasksRes, aiRes] = await Promise.all([
        apiClient.get(ENDPOINTS.ANALYTICS.DASHBOARD).catch(() => ({ data: { data: {} } })),
        apiClient.get(`${ENDPOINTS.SCHEDULE.DAILY}?date=${today}`).catch(() => ({ data: { data: { tasks: [] } } })),
        apiClient.get(`${ENDPOINTS.TASKS.BASE}?status=pending&limit=5`).catch(() => ({ data: { data: [] } })),
        apiClient.get(ENDPOINTS.AI.SUGGESTIONS).catch(() => ({ data: { data: { suggestions: [] } } })),
      ]);

      const analytics = analyticsRes.data?.data || {};
      const blocks = scheduleRes.data?.data?.blocks || [];
      const upcomingTasks = Array.isArray(tasksRes.data?.data) ? tasksRes.data.data : [];
      const suggestions = aiRes.data?.data?.suggestions || [];

      return {
        metrics: {
          tasksCompleted: analytics.completed_tasks || 0,
          totalTasks: analytics.total_tasks || 0,
          focusHours: analytics.focus_hours || 0,
          focusTarget: 4, // Example default
          currentStreak: analytics.consistency_score || 0,
        },
        todaySchedule: blocks.map((b: any) => ({
          id: b.task_id || b.id,
          title: b.title,
          description: b.category || '',
          status: 'pending',
          priority: 'medium',
          startTime: b.start,
          endTime: b.end,
          dueDate: today,
        })),
        upcomingTasks: upcomingTasks,
        aiSuggestions: suggestions.map((text: string, i: number) => ({
          id: `sug_${i}`,
          title: 'AI Insight',
          description: text,
          type: 'optimization',
        })),
      };
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
      throw e;
    }
  },
};
