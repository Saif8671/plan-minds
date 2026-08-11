import { create } from 'zustand';
import { StorageService } from '../services/storage.service';

interface User {
  id: string;
  email: string;
  name: string | null;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasCompletedOnboarding: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setHasCompletedOnboarding: (val: boolean) => void;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  hasCompletedOnboarding: false,
  
  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
  setLoading: (loading) => set({ isLoading: loading }),
  setHasCompletedOnboarding: async (val) => {
    await StorageService.setItem('has_completed_onboarding', val ? 'true' : 'false');
    set({ hasCompletedOnboarding: val });
  },
  logout: async () => {
    await StorageService.clearTokens();
    set({ user: null, isAuthenticated: false, isLoading: false });
  },
  hydrate: async () => {
    try {
      const token = await StorageService.getAccessToken();
      const onboardingStr = await StorageService.getItem('has_completed_onboarding');
      
      if (token) {
        // We'll set a placeholder user until the ME endpoint resolves
        set({ 
          isAuthenticated: true, 
          user: { id: 'temp', email: '', name: 'User' },
          hasCompletedOnboarding: onboardingStr === 'true'
        });
      } else {
        set({ isAuthenticated: false, user: null });
      }
    } catch (e) {
      console.error('Hydration failed', e);
    } finally {
      set({ isLoading: false });
    }
  },
}));
