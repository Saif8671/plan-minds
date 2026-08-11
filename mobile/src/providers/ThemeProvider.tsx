import React, { createContext, useContext, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { useAppStore } from '../store/appStore';
import { colors } from '../theme/colors';
import { darkColors } from '../theme/darkColors';

type ThemeContextType = {
  isDark: boolean;
  colors: typeof colors;
};

const ThemeContext = createContext<ThemeContextType>({
  isDark: false,
  colors,
});

export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const systemColorScheme = useColorScheme();
  const themePreference = useAppStore((state: any) => state.theme);

  const isDark = 
    themePreference === 'dark' || 
    (themePreference === 'system' && systemColorScheme === 'dark');

  const activeColors = isDark ? darkColors : colors;

  return (
    <ThemeContext.Provider value={{ isDark, colors: activeColors as any }}>
      {children}
    </ThemeContext.Provider>
  );
}
