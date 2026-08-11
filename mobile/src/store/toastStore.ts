import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastState {
  toasts: ToastMessage[];
  showToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  showToast: (toast) => {
    const id = Math.random().toString(36).substring(7);
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id, duration: toast.duration || 3000 }],
    }));
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

export const toast = {
  success: (title: string, message?: string, duration?: number) => 
    useToastStore.getState().showToast({ type: 'success', title, message, duration }),
  error: (title: string, message?: string, duration?: number) => 
    useToastStore.getState().showToast({ type: 'error', title, message, duration }),
  warning: (title: string, message?: string, duration?: number) => 
    useToastStore.getState().showToast({ type: 'warning', title, message, duration }),
  info: (title: string, message?: string, duration?: number) => 
    useToastStore.getState().showToast({ type: 'info', title, message, duration }),
};
