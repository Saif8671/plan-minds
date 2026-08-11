import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';

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

  forgotPassword: async (email: string): Promise<void> => {
    // Assuming backend has this, if not mocked temporarily
    // await apiClient.post('/auth/forgot-password', { email });
    return new Promise((resolve) => setTimeout(resolve, 1000));
  },

  verifyOTP: async (email: string, otp: string): Promise<void> => {
    // await apiClient.post('/auth/verify-otp', { email, otp });
    return new Promise((resolve) => setTimeout(resolve, 1000));
  },

  resetPassword: async (token: string, password: string): Promise<void> => {
    // await apiClient.post('/auth/reset-password', { token, password });
    return new Promise((resolve) => setTimeout(resolve, 1000));
  },
};
