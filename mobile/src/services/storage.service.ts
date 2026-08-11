import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ACCESS_TOKEN_KEY = 'planminds_access_token';
const REFRESH_TOKEN_KEY = 'planminds_refresh_token';

export const StorageService = {
  // Secure tokens
  async setTokens(accessToken: string, refreshToken: string) {
    await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
  },
  async getAccessToken() {
    return await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
  },
  async getRefreshToken() {
    return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  },
  async clearTokens() {
    await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
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
