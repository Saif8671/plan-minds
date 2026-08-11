import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { Task } from './dashboard.api'; // Reuse Task interface

export interface ScheduleDay {
  date: string; // YYYY-MM-DD
  tasks: Task[];
  conflicts?: { taskId: string; message: string }[];
}

export const ScheduleAPI = {
  getDailySchedule: async (date: string): Promise<ScheduleDay> => {
    try {
      const response = await apiClient.get(`${ENDPOINTS.SCHEDULE.TODAY}?date=${date}`);
      
      const scheduleResponse = response.data?.data;
      
      return {
        date,
        tasks: scheduleResponse.generated_schedule?.blocks?.map((block: any) => ({
          id: block.id,
          title: block.title,
          status: 'pending', // You may want to fetch actual status if supported
          priority: 'medium',
          startTime: block.start.substring(0, 5), // Assumes "HH:MM:SS"
          endTime: block.end.substring(0, 5),
        })) || [],
        conflicts: scheduleResponse.generated_schedule?.validation?.conflicts?.map((c: any) => ({
          taskId: c.block_ids[0], // simplified mapping
          message: c.message
        })) || []
      };
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
      
      return {
        date,
        tasks: scheduleResponse.generated_schedule?.blocks?.map((block: any) => ({
          id: block.id,
          title: block.title,
          status: 'pending',
          priority: 'medium',
          startTime: block.start.substring(0, 5),
          endTime: block.end.substring(0, 5),
        })) || [],
        conflicts: scheduleResponse.generated_schedule?.validation?.conflicts?.map((c: any) => ({
          taskId: c.block_ids[0],
          message: c.message
        })) || []
      };
    } catch (error) {
      console.error('Failed to regenerate schedule:', error);
      throw error;
    }
  },
};
