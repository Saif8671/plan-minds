import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Calendar, DateData } from 'react-native-calendars';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { useTheme } from '../../../providers/ThemeProvider';
import { format } from 'date-fns';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

export default function CalendarScreen() {
  const { colors, isDark } = useTheme();
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  const handleDayPress = (day: DateData) => {
    setSelectedDate(day.dateString);
  };

  // Mock marked dates
  const markedDates = {
    [selectedDate]: { selected: true, selectedColor: colors.primary },
    '2026-08-11': { marked: true, dotColor: colors.accent },
    '2026-08-12': { marked: true, dotColor: colors.warning },
    '2026-08-15': { marked: true, dotColor: colors.error },
  };

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800 flex-row justify-between items-center">
        <Text className="text-3xl font-bold text-dark dark:text-white">Calendar</Text>
        <TouchableOpacity className="bg-primary/10 w-10 h-10 rounded-full items-center justify-center">
          <Ionicons name="add" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View className="flex-1">
        <Calendar
          current={selectedDate}
          onDayPress={handleDayPress}
          markedDates={markedDates}
          theme={{
            backgroundColor: 'transparent',
            calendarBackground: 'transparent',
            textSectionTitleColor: colors.gray[400],
            selectedDayBackgroundColor: colors.primary,
            selectedDayTextColor: '#ffffff',
            todayTextColor: colors.primary,
            dayTextColor: isDark ? colors.gray[100] : colors.gray[800],
            textDisabledColor: colors.gray[600],
            dotColor: colors.primary,
            selectedDotColor: '#ffffff',
            arrowColor: colors.primary,
            monthTextColor: isDark ? '#ffffff' : colors.dark,
            indicatorColor: colors.primary,
            textDayFontFamily: 'System',
            textMonthFontFamily: 'System',
            textDayHeaderFontFamily: 'System',
            textMonthFontWeight: 'bold',
          }}
          enableSwipeMonths={true}
        />

        <View className="flex-1 px-4 pt-6">
          <Text className="text-xl font-bold text-dark dark:text-white mb-4">
            {format(new Date(selectedDate), 'EEEE, MMMM d')}
          </Text>
          
          <View className="items-center justify-center py-12">
            <View className="w-16 h-16 rounded-full bg-gray-50 dark:bg-gray-800 items-center justify-center mb-4">
              <Ionicons name="calendar-outline" size={32} color={colors.gray[400]} />
            </View>
            <Text className="text-gray-500 font-medium">No events for this day</Text>
            <TouchableOpacity className="mt-4">
              <Text className="text-primary font-bold">Add Event</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScreenLayout>
  );
}
