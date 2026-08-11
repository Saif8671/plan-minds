import React from 'react';
import { EmptyState } from './EmptyState';

interface ErrorScreenProps {
  error?: Error | string;
  onRetry?: () => void;
  message?: string;
}

export function ErrorScreen({ error, onRetry, message }: ErrorScreenProps) {
  const errorMessage = 
    message || 
    (typeof error === 'string' ? error : error?.message) || 
    'An unexpected error occurred';

  return (
    <EmptyState
      icon="alert-circle-outline"
      title="Something went wrong"
      description={errorMessage}
      actionLabel={onRetry ? "Try Again" : undefined}
      onAction={onRetry}
    />
  );
}
