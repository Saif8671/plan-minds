import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TasksAPI, TaskCreate, TaskUpdate, TaskResponse } from '../api/tasks.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export const TASKS_QUERY_KEY = 'tasks';

export function useTasks(page: number = 1, status?: string) {
  return useQuery({
    queryKey: [TASKS_QUERY_KEY, page, status],
    queryFn: () => TasksAPI.listTasks(page, 20, status),
    meta: {
      errorMessage: 'Failed to load tasks',
    },
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreate) => TasksAPI.createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      toast.success('Task Created', 'Your new task has been added.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to create task'),
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: TaskUpdate }) =>
      TasksAPI.updateTask(taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to update task'),
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => TasksAPI.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      toast.success('Task Deleted', 'The task has been removed.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete task'),
  });
}

export function useStartTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => TasksAPI.startTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to start task'),
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => TasksAPI.completeTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['schedule'] });
      queryClient.invalidateQueries({ queryKey: ['gamification'] });
      toast.success('Task Completed', 'Great work! XP awarded.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to complete task'),
  });
}

export function useSkipTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, reason }: { taskId: string; reason?: string }) =>
      TasksAPI.skipTask(taskId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TASKS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['schedule'] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to skip task'),
  });
}
