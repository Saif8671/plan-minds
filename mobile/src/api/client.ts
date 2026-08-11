import axios from 'axios';
import Constants from 'expo-constants';
import { StorageService } from '../services/storage.service';
import { ENDPOINTS } from './endpoints';
import { useAuthStore } from '../store/authStore';

const apiUrl = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  async (config) => {
    const token = await StorageService.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await StorageService.getRefreshToken();
        if (!refreshToken) throw new Error('No refresh token');

        // Request new token
        const response = await axios.post(`${apiUrl}${ENDPOINTS.AUTH.REFRESH}`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: new_refresh } = response.data.data;
        await StorageService.setTokens(access_token, new_refresh);

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh token expired or invalid, force logout
        await StorageService.clearTokens();
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
