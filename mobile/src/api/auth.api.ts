import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { StorageService } from '../services/storage.service';
import { useAuthStore } from '../store/authStore';

export interface LoginRequest {
  email: string;
  password?: string; // Optional if using magic link or OTP
}

export interface RegisterRequest {
  email: string;
  password?: string;
  name: string;
}

export interface AuthResponse {
  data: {
    user: {
      id: string;
      email: string;
      name: string | null;
    };
    access_token: string;
    refresh_token: string;
  };
}

export const AuthAPI = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post(ENDPOINTS.AUTH.LOGIN, data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post(ENDPOINTS.AUTH.REGISTER, data);
    return response.data;
  },

  firebaseLogin: async (idToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post(ENDPOINTS.AUTH.FIREBASE, { id_token: idToken });
    return response.data;
  },

  forgotPassword: async (email: string): Promise<{ reset_token: string; message: string }> => {
    const response = await apiClient.post(ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
    return response.data?.data || response.data;
  },

  verifyOTP: async (email: string, otp: string): Promise<{ reset_token: string }> => {
    const response = await apiClient.post(ENDPOINTS.AUTH.VERIFY_OTP, { email, otp });
    return response.data?.data || response.data || { reset_token: otp };
  },

  resetPassword: async (token: string, password: string): Promise<void> => {
    await apiClient.post(ENDPOINTS.AUTH.RESET_PASSWORD, { token, password });
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post(ENDPOINTS.AUTH.LOGOUT);
    } finally {
      await StorageService.clearTokens();
      useAuthStore.getState().logout();
    }
  },
};
