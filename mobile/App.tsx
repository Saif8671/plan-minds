import './global.css';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import RootNavigator from './src/navigation/RootNavigator';
import { ThemeProvider, useTheme } from './src/providers/ThemeProvider';
import { QueryProvider } from './src/providers/QueryProvider';
import { ErrorBoundary } from './src/components/common/ErrorBoundary';
import { ToastContainer } from './src/components/common/ToastContainer';

const linking = {
  prefixes: ['planminds://', 'http://localhost:8082', 'http://localhost:8081'],
  config: {
    screens: {
      Auth: {
        screens: {
          Welcome: 'welcome',
          Login: 'login',
          Register: 'signup',
          ForgotPassword: 'forgot-password',
        },
      },
      Main: {
        screens: {
          Home: 'home',
          Assistant: 'assistant',
          Schedule: 'schedule',
          Insights: 'insights',
          Profile: 'profile',
        },
      },
    },
  },
};

function AppContent() {
  const { isDark } = useTheme();
  return (
    <SafeAreaProvider>
      <NavigationContainer linking={linking}>
        <RootNavigator />
        <StatusBar style={isDark ? "light" : "dark"} />
        <ToastContainer />
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <QueryProvider>
          <ThemeProvider>
            <AppContent />
          </ThemeProvider>
        </QueryProvider>
      </GestureHandlerRootView>
    </ErrorBoundary>
  );
}
