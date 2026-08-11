import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { useAuthStore } from '../../../store/authStore';
import { useAppStore } from '../../../store/appStore';
import { Avatar } from '../../../components/common/Avatar';
import { SettingRow } from '../components/SettingRow';
import { Ionicons } from '@expo/vector-icons';
import { useGamification } from '../../../hooks/useGamification';
import { SkeletonLoader } from '../../../components/common/SkeletonLoader';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useAppStore();
  const { data: stats, isLoading: statsLoading } = useGamification();

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: logout },
    ]);
  };

  const toggleTheme = (val: boolean) => {
    setTheme(val ? 'dark' : 'light');
  };

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800">
        <Text className="text-3xl font-bold text-dark dark:text-white">Profile</Text>
      </View>

      <ScrollView className="flex-1 px-4 pt-6" contentContainerStyle={{ paddingBottom: 100 }}>
        
        <View className="items-center mb-8">
          <Avatar 
            name={user?.name || 'User'} 
            size="xl" 
            className="mb-4 shadow-sm" 
          />
          <Text className="text-2xl font-bold text-dark dark:text-white">
            {user?.name || 'User'}
          </Text>
          <Text className="text-gray-500">{user?.email}</Text>
          
          <TouchableOpacity className="mt-4 bg-primary/10 px-6 py-2 rounded-full">
            <Text className="text-primary font-bold">Edit Profile</Text>
          </TouchableOpacity>
        </View>

        <Text className="font-bold text-gray-500 uppercase text-xs mb-2 mt-4">Gamification Stats</Text>
        <View className="bg-white dark:bg-gray-900 rounded-2xl p-4 mb-6 shadow-sm border border-gray-100 dark:border-gray-800">
          {statsLoading || !stats ? (
            <SkeletonLoader width="100%" height={100} />
          ) : (
            <>
              <View className="flex-row justify-between mb-6">
                <View className="items-center flex-1">
                  <View className="w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 items-center justify-center mb-2">
                    <Ionicons name="flame" size={24} color="#F97316" />
                  </View>
                  <Text className="text-dark dark:text-white font-bold text-lg">{stats.currentStreak} Days</Text>
                  <Text className="text-gray-500 text-xs">Current Streak</Text>
                </View>
                <View className="items-center flex-1 border-l border-r border-gray-100 dark:border-gray-800">
                  <View className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 items-center justify-center mb-2">
                    <Ionicons name="trophy" size={24} color="#A855F7" />
                  </View>
                  <Text className="text-dark dark:text-white font-bold text-lg">{stats.longestStreak} Days</Text>
                  <Text className="text-gray-500 text-xs">Longest Streak</Text>
                </View>
                <View className="items-center flex-1">
                  <View className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 items-center justify-center mb-2">
                    <Ionicons name="analytics" size={24} color="#10B981" />
                  </View>
                  <Text className="text-dark dark:text-white font-bold text-lg">{stats.productivityScore}</Text>
                  <Text className="text-gray-500 text-xs">Productivity</Text>
                </View>
              </View>

              <Text className="font-bold text-dark dark:text-white mb-3">Badges</Text>
              <View className="flex-row flex-wrap">
                {stats.badges.map((badge, index) => (
                  <View key={badge.id} className="items-center mr-4 mb-4 w-1/4">
                    <View className="w-14 h-14 rounded-full bg-primary/10 items-center justify-center mb-1 border border-primary/20">
                      <Ionicons name={badge.icon as any} size={28} color="#1677FF" />
                    </View>
                    <Text className="text-xs text-center text-gray-600 dark:text-gray-400" numberOfLines={1}>{badge.name}</Text>
                  </View>
                ))}
              </View>
            </>
          )}
        </View>

        <Text className="font-bold text-gray-500 uppercase text-xs mb-2 mt-4">Account</Text>
        <View className="bg-white dark:bg-gray-900 rounded-2xl px-4 mb-6 shadow-sm border border-gray-100 dark:border-gray-800">
          <SettingRow icon="star" title="Upgrade to Pro" subtitle="Unlock all AI features" />
          <SettingRow icon="person" title="Personal Details" />
          <SettingRow icon="notifications" title="Notifications" />
          <SettingRow icon="lock-closed" title="Privacy & Security" />
        </View>

        <Text className="font-bold text-gray-500 uppercase text-xs mb-2">Preferences</Text>
        <View className="bg-white dark:bg-gray-900 rounded-2xl px-4 mb-6 shadow-sm border border-gray-100 dark:border-gray-800">
          <SettingRow 
            icon="moon" 
            title="Dark Mode" 
            isSwitch 
            switchValue={theme === 'dark'} 
            onSwitchChange={toggleTheme}
          />
          <SettingRow icon="globe" title="Language" value="English" />
          <SettingRow icon="time" title="Time Zone" value="Auto" />
        </View>

        <Text className="font-bold text-gray-500 uppercase text-xs mb-2">Support</Text>
        <View className="bg-white dark:bg-gray-900 rounded-2xl px-4 mb-6 shadow-sm border border-gray-100 dark:border-gray-800">
          <SettingRow icon="help-circle" title="Help Center" />
          <SettingRow icon="document-text" title="Terms of Service" />
        </View>

        <View className="bg-white dark:bg-gray-900 rounded-2xl px-4 mb-8 shadow-sm border border-gray-100 dark:border-gray-800">
          <SettingRow 
            icon="log-out" 
            title="Sign Out" 
            destructive 
            onPress={handleLogout} 
          />
        </View>
        
        <Text className="text-center text-gray-400 text-xs mb-12">
          PlanMinds Version 1.0.0
        </Text>

      </ScrollView>
    </ScreenLayout>
  );
}
