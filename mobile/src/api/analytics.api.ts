import { apiClient } from './client';

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

export const AnalyticsAPI = {
  getAnalytics: async (): Promise<AnalyticsData> => {
    return new Promise((resolve) => setTimeout(() => resolve({
      focusHours: 24.5,
      totalTasksCompleted: 42,
      weeklyProductivityScore: 85,
      dailyStats: [
        { day: 'Mon', focus: 3, tasks: 5 },
        { day: 'Tue', focus: 4, tasks: 7 },
        { day: 'Wed', focus: 2.5, tasks: 4 },
        { day: 'Thu', focus: 5, tasks: 8 },
        { day: 'Fri', focus: 3.5, tasks: 6 },
        { day: 'Sat', focus: 1, tasks: 2 },
        { day: 'Sun', focus: 0, tasks: 0 },
      ],
      topCategories: [
        { name: 'Work', value: 60, color: '#1677FF' },
        { name: 'Health', value: 20, color: '#10B981' },
        { name: 'Learning', value: 15, color: '#7A3EF3' },
        { name: 'Personal', value: 5, color: '#F59E0B' },
      ],
      insights: [
        {
          id: '1',
          title: 'Peak Productivity',
          description: 'You get the most deep work done between 9 AM and 11 AM.',
          type: 'positive'
        },
        {
          id: '2',
          title: 'Sleep Correlation',
          description: 'When you sleep less than 6 hours, your completed tasks drop by 30%.',
          type: 'warning'
        }
      ]
    }), 800));
  }
};
