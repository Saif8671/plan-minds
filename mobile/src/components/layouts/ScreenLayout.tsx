import React from 'react';
import {
  View,
  ScrollView,
  RefreshControl,
  KeyboardAvoidingView,
  Platform,
  ViewProps,
} from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { cn } from '../../utils/cn';
import { HeaderBar } from '../common/HeaderBar';

interface ScreenLayoutProps extends ViewProps {
  scrollable?: boolean;
  onRefresh?: () => void;
  refreshing?: boolean;
  title?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  headerTransparent?: boolean;
  padding?: boolean;
  keyboardAvoid?: boolean;
}

export function ScreenLayout({
  children,
  scrollable = false,
  onRefresh,
  refreshing = false,
  title,
  showBack = false,
  onBack,
  rightAction,
  headerTransparent,
  padding = true,
  keyboardAvoid = true,
  className,
  ...props
}: ScreenLayoutProps) {
  const insets = useSafeAreaInsets();
  
  const showHeader = title || showBack || rightAction;

  const content = (
    <View className={cn("flex-1 bg-background dark:bg-dark", className)} {...props}>
      {showHeader && (
        <HeaderBar
          title={title}
          showBack={showBack}
          onBack={onBack}
          rightAction={rightAction}
          transparent={headerTransparent}
        />
      )}
      
      {scrollable ? (
        <ScrollView
          className="flex-1"
          contentContainerStyle={{
            padding: padding ? 16 : 0,
            paddingBottom: padding ? Math.max(insets.bottom + 16, 16) : insets.bottom,
          }}
          showsVerticalScrollIndicator={false}
          refreshControl={
            onRefresh ? (
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#1677FF" />
            ) : undefined
          }
        >
          {children}
        </ScrollView>
      ) : (
        <View 
          className={cn(
            "flex-1", 
            padding ? "p-4" : "",
          )}
          style={{ paddingBottom: padding ? Math.max(insets.bottom, 16) : 0 }}
        >
          {children}
        </View>
      )}
    </View>
  );

  if (keyboardAvoid) {
    return (
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {content}
      </KeyboardAvoidingView>
    );
  }

  return content;
}
