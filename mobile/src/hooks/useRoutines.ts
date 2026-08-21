import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RoutinesAPI, RoutineCreate, RoutineUpdate } from '../api/routines.api';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';

export const ROUTINES_QUERY_KEY = 'routines';

export function useRoutines(page: number = 1, activeOnly: boolean = false) {
  return useQuery({
    queryKey: [ROUTINES_QUERY_KEY, page, activeOnly],
    queryFn: () => RoutinesAPI.listRoutines(page, 20, activeOnly),
    meta: {
      errorMessage: 'Failed to load routines',
    },
  });
}

export function useRoutine(routineId: string) {
  return useQuery({
    queryKey: [ROUTINES_QUERY_KEY, routineId],
    queryFn: () => RoutinesAPI.getRoutine(routineId),
    enabled: !!routineId,
  });
}

export function useCreateRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RoutineCreate) => RoutinesAPI.createRoutine(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROUTINES_QUERY_KEY] });
      toast.success('Routine Created', 'Your new routine has been added.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to create routine'),
  });
}

export function useUpdateRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ routineId, data }: { routineId: string; data: RoutineUpdate }) =>
      RoutinesAPI.updateRoutine(routineId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROUTINES_QUERY_KEY] });
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to update routine'),
  });
}

export function useDeleteRoutine() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (routineId: string) => RoutinesAPI.deleteRoutine(routineId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROUTINES_QUERY_KEY] });
      toast.success('Routine Deleted', 'The routine has been removed.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to delete routine'),
  });
}
