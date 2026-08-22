import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ScheduleAPI,
  ScheduleGenerateRequest,
  ScheduleGenerateMultiRequest,
  ScheduleCreate,
  ScheduleUpdate,
  ScheduleBlockCreate,
  ScheduleBlockUpdate,
  ScheduleBlockMove
} from '../api/schedule.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export const SCHEDULE_QUERY_KEY = 'schedule';
export const TASKS_QUERY_KEY = 'tasks';

export function useDailySchedule(date: string) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, date],
    queryFn: () => ScheduleAPI.getDailySchedule(date),
    meta: {
      errorMessage: 'Failed to load schedule',
    },
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

export function useScheduleDetail(scheduleId: string) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, 'detail', scheduleId],
    queryFn: () => ScheduleAPI.getSchedule(scheduleId),
    enabled: !!scheduleId,
  });
}

export function useValidateSchedule(scheduleId: string, bufferMinutes?: number) {
  return useQuery({
    queryKey: [SCHEDULE_QUERY_KEY, 'validate', scheduleId, bufferMinutes],
    queryFn: () => ScheduleAPI.validateSchedule(scheduleId, bufferMinutes),
    enabled: !!scheduleId,
  });
}

// ─── Mutations ────────────────────────────────────────────────────────

export function useCreateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ScheduleCreate) => ScheduleAPI.createSchedule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedule Created', 'Successfully created schedule.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to create schedule'),
  });
}

export function useUpdateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, data }: { scheduleId: string; data: ScheduleUpdate }) => 
      ScheduleAPI.updateSchedule(scheduleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedule Updated', 'Successfully updated schedule.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to update schedule'),
  });
}

export function useDeleteSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (scheduleId: string) => ScheduleAPI.deleteSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedule Deleted', 'Successfully deleted schedule.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete schedule'),
  });
}

export function useGenerateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ScheduleGenerateRequest) => ScheduleAPI.generateSchedule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedule Generated', 'Your AI-optimized schedule is ready.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to generate schedule'),
  });
}

export function useGenerateMultiDay() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ScheduleGenerateMultiRequest) => ScheduleAPI.generateMultiDay(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedules Generated', 'Your AI-optimized multi-day schedule is ready.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to generate schedules'),
  });
}

export function useRegenerateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (date: string) => ScheduleAPI.regenerateSchedule(date),
    onSuccess: (data, date) => {
      queryClient.setQueryData([SCHEDULE_QUERY_KEY, date], data);
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Schedule Optimized', 'AI has resolved your conflicts.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to regenerate schedule'),
  });
}

// ─── Block Mutations ──────────────────────────────────────────────────

export function useCreateBlock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, data }: { scheduleId: string; data: ScheduleBlockCreate }) => 
      ScheduleAPI.createBlock(scheduleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to create block'),
  });
}

export function useUpdateBlock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, blockId, data }: { scheduleId: string; blockId: string; data: ScheduleBlockUpdate }) => 
      ScheduleAPI.updateBlock(scheduleId, blockId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to update block'),
  });
}

export function useMoveBlock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, blockId, data }: { scheduleId: string; blockId: string; data: ScheduleBlockMove }) => 
      ScheduleAPI.moveBlock(scheduleId, blockId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to move block'),
  });
}

export function useSplitBlock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, blockId, splitAt }: { scheduleId: string; blockId: string; splitAt: string }) => 
      ScheduleAPI.splitBlock(scheduleId, blockId, splitAt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to split block'),
  });
}

export function useMergeBlocks() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, blockIds, mergedTitle }: { scheduleId: string; blockIds: string[]; mergedTitle?: string }) => 
      ScheduleAPI.mergeBlocks(scheduleId, blockIds, mergedTitle),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to merge blocks'),
  });
}

export function useDeleteBlock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, blockId }: { scheduleId: string; blockId: string }) => 
      ScheduleAPI.deleteBlock(scheduleId, blockId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SCHEDULE_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete block'),
  });
}

export function useTaskDetail(taskId: string) {
  return useQuery({
    queryKey: ['taskDetail', taskId],
    queryFn: () => ScheduleAPI.getTaskById(taskId),
    enabled: !!taskId,
  });
}
