import { useState, useEffect } from 'react';

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    try {
      // Dynamic import to handle environments where netinfo might be optional/mocked
      const NetInfo = require('@react-native-community/netinfo');
      const unsubscribe = NetInfo.addEventListener((state: any) => {
        setIsOnline(state.isConnected ?? true);
      });
      return () => unsubscribe();
    } catch {
      // Fallback if netinfo native module isn't loaded in test environment
      setIsOnline(true);
    }
  }, []);

  return { isOnline };
}
