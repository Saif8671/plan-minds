import React from 'react';
import { View, Text } from 'react-native';
import { Card } from '../common/Card';

interface ProductivityChartProps {
  data: { day: string; focus: number; tasks: number }[];
}

export function ProductivityChart({ data }: ProductivityChartProps) {
  if (!data || data.length === 0) return null;

  const maxFocus = Math.max(...data.map(d => d.focus), 1);

  return (
    <Card className="mb-6 border-transparent">
      <Text className="text-xl font-bold text-dark dark:text-white mb-6">Focus Hours</Text>
      
      <View className="flex-row items-end justify-between h-40">
        {data.map((item, index) => {
          const heightPercent = (item.focus / maxFocus) * 100;
          return (
            <View key={index} className="items-center w-10">
              <View className="w-full justify-end items-center flex-1 mb-2">
                <View 
                  className="w-6 bg-primary rounded-t-sm"
                  style={{ height: `${Math.max(heightPercent, 2)}%` }}
                />
              </View>
              <Text className="text-xs text-gray-500">{item.day}</Text>
            </View>
          );
        })}
      </View>
    </Card>
  );
}
