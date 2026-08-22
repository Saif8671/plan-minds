import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

export interface AnalyticsData {
  focusHours: number;
  totalTasksCompleted: number;
  weeklyProductivityScore: number;
  dailyStats: {
    day: string;
    focus: number;
    tasks: number;
  }[];
  topCategories: {
    name: string;
    value: number;
    color: string;
  }[];
  insights: {
    id: string;
    title: string;
    description: string;
    type: 'positive' | 'warning' | 'info';
  }[];
}

export interface PeriodAnalytics {
  period: string;
  start_date: string;
  end_date: string;
  completion_rate: number;
  focus_hours: number;
  study_hours: number;
  missed_tasks: number;
  consistency_score: number;
  daily_breakdown: { day: string; focus: number; tasks: number }[];
  insights: string[] | null;
}

const CATEGORY_COLORS: Record<string, string> = {
  Work: '#1677FF',
  Health: '#10B981',
  Learning: '#7A3EF3',
  Personal: '#F59E0B',
  Study: '#6366F1',
  Exercise: '#EC4899',
  Other: '#94A3B8',
};

/** Transform the backend PeriodAnalytics shape into the frontend AnalyticsData shape */
function transformPeriodToAnalyticsData(raw: PeriodAnalytics): AnalyticsData {
  const dailyStats = (raw.daily_breakdown || []).map((d: any) => ({
    day: d.day || d.date || '',
    focus: d.focus_hours ?? d.focus ?? 0,
    tasks: d.completed_tasks ?? d.tasks ?? 0,
  }));

  const totalTasks = dailyStats.reduce((sum, d) => sum + d.tasks, 0);
  const totalFocus = dailyStats.reduce((sum, d) => sum + d.focus, 0);

  return {
    focusHours: raw.focus_hours || totalFocus,
    totalTasksCompleted: totalTasks,
    weeklyProductivityScore: Math.round(raw.consistency_score || 0),
    dailyStats,
    topCategories: [], // Backend PeriodAnalytics doesn't include category breakdown
    insights: (raw.insights || []).map((text, i) => ({
      id: String(i + 1),
      title: text.split('.')[0] || 'Insight',
      description: text,
      type: 'info' as const,
    })),
  };
}

export const AnalyticsAPI = {
  /** Get analytics by combining weekly and dashboard data */
  getAnalytics: async (): Promise<AnalyticsData> => {
    const [weeklyRes, dashboardRes] = await Promise.all([
      apiClient.get(ENDPOINTS.ANALYTICS.WEEKLY),
      apiClient.get(ENDPOINTS.ANALYTICS.DASHBOARD),
    ]);
    
    const weekly: PeriodAnalytics = weeklyRes.data?.data || weeklyRes.data;
    const dashboard = dashboardRes.data?.data || dashboardRes.data;
    
    const data = transformPeriodToAnalyticsData(weekly);
    
    // Add category breakdown from dashboard
    if (dashboard?.category_breakdown) {
      data.topCategories = dashboard.category_breakdown.map((c: any) => ({
        name: c.category.charAt(0).toUpperCase() + c.category.slice(1),
        value: Math.round((c.hours / (dashboard.study_hours + dashboard.focus_hours || 1)) * 100) || Math.round(c.hours),
        color: CATEGORY_COLORS[c.category.charAt(0).toUpperCase() + c.category.slice(1)] || CATEGORY_COLORS.Other
      })).sort((a: any, b: any) => b.value - a.value);
      
      // Re-calculate percentages so they add up to 100
      const totalVal = data.topCategories.reduce((sum: number, c: any) => sum + c.value, 0);
      if (totalVal > 0) {
        data.topCategories = data.topCategories.map((c: any) => ({
          ...c,
          value: Math.round((c.value / totalVal) * 100)
        }));
      }
    }
    
    return data;
  },

  getWeeklyAnalytics: async (): Promise<PeriodAnalytics> => {
    const response = await apiClient.get(ENDPOINTS.ANALYTICS.WEEKLY);
    return response.data?.data || response.data;
  },

  getMonthlyAnalytics: async (): Promise<PeriodAnalytics> => {
    const response = await apiClient.get(ENDPOINTS.ANALYTICS.MONTHLY);
    return response.data?.data || response.data;
  },

  getWeeklyReport: async (): Promise<string> => {
    const response = await apiClient.get(ENDPOINTS.ANALYTICS.WEEKLY_REPORT);
    return response.data;
  },
};
