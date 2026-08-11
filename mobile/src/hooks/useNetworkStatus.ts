import { useState, useEffect } from 'react';
// import NetInfo from '@react-native-community/netinfo';

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    // This is a placeholder for the actual NetInfo hook.
    // In a real app, you would install @react-native-community/netinfo
    // and use it like this:
    // const unsubscribe = NetInfo.addEventListener(state => {
    //   setIsOnline(state.isConnected ?? false);
    // });
    // return () => unsubscribe();
  }, []);

  return { isOnline };
}
