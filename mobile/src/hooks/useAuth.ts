import { useMutation } from '@tanstack/react-query';
import { AuthAPI, LoginRequest, RegisterRequest } from '../api/auth.api';
import { useAuthStore } from '../store/authStore';
import { StorageService } from '../services/storage.service';
import { ErrorHandler } from '../errors/errorHandler';
import { toast } from '../store/toastStore';
import { ProfileAPI } from '../api/profile.api';

export function useLogin() {
  const setUser = useAuthStore((state) => state.setUser);
  
  return useMutation({
    mutationFn: (data: LoginRequest) => AuthAPI.login(data),
    onSuccess: async (res) => {
      await StorageService.setTokens(res.data.access_token, res.data.refresh_token);
      try {
        const profile = await ProfileAPI.getProfile();
        setUser({ id: profile.id, email: profile.email, name: profile.name });
      } catch (err) {
        setUser({ id: 'unknown', email: 'unknown', name: 'User' });
      }
      toast.success('Welcome back!', 'Successfully logged in.');
    },
    onError: (error) => {
      ErrorHandler.handle(error, 'Failed to login. Please check your credentials.');
    },
  });
}

export function useRegister() {
  const setUser = useAuthStore((state) => state.setUser);

  return useMutation({
    mutationFn: (data: RegisterRequest) => AuthAPI.register(data),
    onSuccess: async (res) => {
      await StorageService.setTokens(res.data.access_token, res.data.refresh_token);
      try {
        const profile = await ProfileAPI.getProfile();
        setUser({ id: profile.id, email: profile.email, name: profile.name });
      } catch (err) {
        setUser({ id: 'unknown', email: 'unknown', name: 'User' });
      }
      toast.success('Account created', 'Welcome to PlanMinds!');
    },
    onError: (error) => {
      ErrorHandler.handle(error, 'Failed to register account.');
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email: string) => AuthAPI.forgotPassword(email),
    onError: (error) => ErrorHandler.handle(error),
  });
}

export function useVerifyOTP() {
  return useMutation({
    mutationFn: ({ email, otp }: { email: string; otp: string }) => AuthAPI.verifyOTP(email, otp),
    onError: (error) => ErrorHandler.handle(error, 'Invalid OTP code.'),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) => AuthAPI.resetPassword(token, password),
    onSuccess: () => {
      toast.success('Password updated', 'You can now login with your new password.');
    },
    onError: (error) => ErrorHandler.handle(error, 'Failed to reset password.'),
  });
}

export function useFirebaseLogin() {
  const setUser = useAuthStore((state) => state.setUser);

  return useMutation({
    mutationFn: (idToken: string) => AuthAPI.firebaseLogin(idToken),
    onSuccess: async (res) => {
      await StorageService.setTokens(res.data.access_token, res.data.refresh_token);
      try {
        const profile = await ProfileAPI.getProfile();
        setUser({ id: profile.id, email: profile.email, name: profile.name });
      } catch (err) {
        setUser({ id: 'unknown', email: 'unknown', name: 'User' });
      }
      toast.success('Welcome!', 'Successfully authenticated.');
    },
    onError: (error) => {
      ErrorHandler.handle(error, 'Firebase authentication failed.');
    },
  });
}
