import React, { useState } from 'react';
import { View, Text, Switch, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ScheduleStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Input } from '../../../components/common/Input';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

type NavigationProp = NativeStackNavigationProp<ScheduleStackParamList, 'CreateEditSchedule'>;

export default function CreateEditScheduleScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [title, setTitle] = useState('');
  const [isAllDay, setIsAllDay] = useState(false);
  const [priority, setPriority] = useState('medium');

  const priorities = [
    { id: 'low', color: '#10B981' },
    { id: 'medium', color: '#F59E0B' },
    { id: 'high', color: '#EF4444' },
  ];

  return (
    <ScreenLayout showBack scrollable onBack={() => navigation.goBack()}>
      <View className="px-4 pt-6 pb-20">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-6">
          New Event
        </Text>

        <Input
          label="Event Title"
          placeholder="e.g. Design Sync"
          value={title}
          onChangeText={setTitle}
        />

        <View className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-4 mb-6 border border-gray-100 dark:border-gray-800">
          <View className="flex-row items-center justify-between py-2 border-b border-gray-200 dark:border-gray-800 mb-2">
            <View className="flex-row items-center">
              <Ionicons name="time-outline" size={20} color="#94A3B8" className="mr-3" />
              <Text className="text-base text-dark dark:text-white font-medium">All-day</Text>
            </View>
            <Switch 
              value={isAllDay} 
              onValueChange={setIsAllDay}
              trackColor={{ false: '#E2E8F0', true: '#34D399' }}
              thumbColor="#fff"
            />
          </View>

          <View className="flex-row items-center justify-between py-3 border-b border-gray-200 dark:border-gray-800 mb-2">
            <Text className="text-base text-dark dark:text-white font-medium pl-8">Starts</Text>
            <View className="flex-row items-center bg-gray-200 dark:bg-gray-800 px-3 py-1.5 rounded-lg">
              <Text className="text-dark dark:text-white font-medium mr-2">Aug 11, 2026</Text>
              {!isAllDay && <Text className="text-dark dark:text-white font-medium">09:00 AM</Text>}
            </View>
          </View>

          <View className="flex-row items-center justify-between py-3">
            <Text className="text-base text-dark dark:text-white font-medium pl-8">Ends</Text>
            <View className="flex-row items-center bg-gray-200 dark:bg-gray-800 px-3 py-1.5 rounded-lg">
              <Text className="text-dark dark:text-white font-medium mr-2">Aug 11, 2026</Text>
              {!isAllDay && <Text className="text-dark dark:text-white font-medium">10:00 AM</Text>}
            </View>
          </View>
        </View>

        <Text className="text-sm font-bold text-gray-500 uppercase mb-3">Priority</Text>
        <View className="flex-row justify-between mb-8">
          {priorities.map(p => (
            <TouchableOpacity 
              key={p.id}
              onPress={() => setPriority(p.id)}
              className={cn(
                "flex-1 mx-1 py-3 items-center rounded-xl border",
                priority === p.id 
                  ? "bg-primary/10 border-primary" 
                  : "bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800"
              )}
            >
              <View className="flex-row items-center">
                <View className="w-2 h-2 rounded-full mr-2" style={{ backgroundColor: p.color }} />
                <Text className={cn(
                  "font-bold capitalize",
                  priority === p.id ? "text-primary" : "text-gray-500"
                )}>
                  {p.id}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <Button title="Save Event" onPress={() => navigation.goBack()} />
      </View>
    </ScreenLayout>
  );
}
