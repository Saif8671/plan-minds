import { toast } from '../store/toastStore';
import { AxiosError } from 'axios';

export const ErrorHandler = {
  handle: (error: unknown, fallbackMessage = 'An unexpected error occurred') => {
    console.error('[ErrorHandler]', error);

    let message = fallbackMessage;

    if (error instanceof AxiosError) {
      // Backend error response usually has { detail: "message" } or { message: "message" }
      let extractedMessage = 
        error.response?.data?.error || 
        error.response?.data?.detail || 
        error.response?.data?.message || 
        error.message || 
        fallbackMessage;
      
      if (typeof extractedMessage === 'object' && extractedMessage !== null) {
        message = extractedMessage.message || JSON.stringify(extractedMessage);
      } else {
        message = String(extractedMessage);
      }
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
