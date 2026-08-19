import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const ACCESS_TOKEN_KEY = 'planminds_access_token';
const REFRESH_TOKEN_KEY = 'planminds_refresh_token';

export const StorageService = {
  // Secure tokens
  async setTokens(accessToken: string, refreshToken: string) {
    if (Platform.OS === 'web') {
      await AsyncStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      await AsyncStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    } else {
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
    }
  },
  async getAccessToken() {
    if (Platform.OS === 'web') {
      return await AsyncStorage.getItem(ACCESS_TOKEN_KEY);
    }
    return await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
  },
  async getRefreshToken() {
    if (Platform.OS === 'web') {
      return await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
    }
    return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  },
  async clearTokens() {
    if (Platform.OS === 'web') {
      await AsyncStorage.removeItem(ACCESS_TOKEN_KEY);
      await AsyncStorage.removeItem(REFRESH_TOKEN_KEY);
    } else {
      await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
      await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    }
  },
  
  // General Async Storage for non-sensitive data
  async setItem(key: string, value: string) {
    await AsyncStorage.setItem(key, value);
  },
  async getItem(key: string) {
    return await AsyncStorage.getItem(key);
  },
  async removeItem(key: string) {
    await AsyncStorage.removeItem(key);
  },
};
