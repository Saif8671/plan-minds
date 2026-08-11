import React, { ErrorInfo } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ErrorHandler } from '../../errors/errorHandler';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    ErrorHandler.handle(error, 'A fatal error occurred');
    console.error('Uncaught error:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <View className="flex-1 items-center justify-center bg-background px-6 dark:bg-dark">
          <View className="mb-6 rounded-full bg-error/10 p-6">
            <Ionicons name="alert-circle" size={48} color="#EF4444" />
          </View>
          <Text className="mb-2 text-center text-xl font-bold text-dark dark:text-white">
            Oops! Something went wrong.
          </Text>
          <Text className="mb-8 text-center text-base text-gray-500">
            {this.state.error?.message || 'We encountered an unexpected error.'}
          </Text>
          <TouchableOpacity
            onPress={this.resetError}
            className="rounded-xl bg-primary px-6 py-3"
          >
            <Text className="font-semibold text-white">Try Again</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}
