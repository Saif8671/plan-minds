import { toast } from '../store/toastStore';
import { AxiosError } from 'axios';

export const ErrorHandler = {
  handle: (error: unknown, fallbackMessage = 'An unexpected error occurred') => {
    console.error('[ErrorHandler]', error);

    let message = fallbackMessage;

    if (error instanceof AxiosError) {
      // Backend error response usually has { detail: "message" } or { message: "message" }
      message = 
        error.response?.data?.detail || 
        error.response?.data?.message || 
        error.message || 
        fallbackMessage;
    } else if (error instanceof Error) {
      message = error.message;
    }

    toast.error('Error', message);
  },

  captureMessage: (message: string) => {
    // Later integrate with Sentry or Crashlytics
    console.warn('[Captured Message]', message);
  }
};
