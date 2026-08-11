import { create } from 'zustand';

interface AppState {
  theme: 'light' | 'dark' | 'system';
  isHydrated: boolean;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setHydrated: (hydrated: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'system',
  isHydrated: false,
  setTheme: (theme) => set({ theme }),
  setHydrated: (isHydrated) => set({ isHydrated }),
}));
