import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ScheduleAPI, ScheduleGenerateRequest } from '../api/schedule.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export const SCHEDULE_QUERY_KEY = 'schedule';

export function useDailySchedule(date: string) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, date],
    queryFn: () => ScheduleAPI.getDailySchedule(date),
    meta: {
      errorMessage: 'Failed to load schedule',
    },
  });
}

export function useRegenerateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (date: string) => ScheduleAPI.regenerateSchedule(date),
    onSuccess: (data, date) => {
      queryClient.setQueryData([SCHEDULE_QUERY_KEY, date], data);
      toast.success('Schedule Optimized', 'AI has resolved your conflicts.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to regenerate schedule'),
  });
}

export function useTaskDetail(taskId: string) {
  return useQuery({
    queryKey: ['taskDetail', taskId],
    queryFn: () => ScheduleAPI.getTaskById(taskId),
    enabled: !!taskId,
  });
}

export function useWeekSchedule(start?: string) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, 'week', start],
    queryFn: () => ScheduleAPI.getWeekSchedule(start),
    meta: {
      errorMessage: 'Failed to load week schedule',
    },
  });
}

export function useGenerateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ScheduleGenerateRequest) => ScheduleAPI.generateSchedule(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      toast.success('Schedule Generated', 'Your AI-optimized schedule is ready.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to generate schedule'),
  });
}

export function useValidateSchedule(scheduleId: string, bufferMinutes?: number) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, 'validate', scheduleId, bufferMinutes],
    queryFn: () => ScheduleAPI.validateSchedule(scheduleId, bufferMinutes),
    enabled: !!scheduleId,
  });
}
