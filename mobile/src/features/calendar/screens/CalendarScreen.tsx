import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { CalendarProvider, ExpandableCalendar, TimelineList } from 'react-native-calendars';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { useTheme } from '../../../providers/ThemeProvider';
import { format, addDays } from 'date-fns';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../../utils/cn';

import { useDailySchedule } from '../../../hooks/useSchedule';

export default function CalendarScreen() {
  const { colors, isDark } = useTheme();
  const [currentDate, setCurrentDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const { data: scheduleData } = useDailySchedule(currentDate);

  const onDateChanged = (date: string) => {
    setCurrentDate(date);
  };

  const events = {
    [currentDate]: (scheduleData?.tasks || []).map((task) => {
      const startTime = task.startTime || '09:00';
      const endTime = task.endTime || '10:00';
      const formattedStart = startTime.length === 5 ? `${startTime}:00` : startTime;
      const formattedEnd = endTime.length === 5 ? `${endTime}:00` : endTime;
      return {
        start: `${currentDate} ${formattedStart}`,
        end: `${currentDate} ${formattedEnd}`,
        title: task.title,
        summary: task.description || '',
        color: task.priority === 'high' ? colors.error : task.priority === 'medium' ? colors.warning : colors.primary,
      };
    }),
  };

  return (
    <ScreenLayout padding={false}>
      <View className="px-4 pt-6 pb-2 border-b border-gray-100 dark:border-gray-800 flex-row justify-between items-center">
        <Text className="text-3xl font-bold text-dark dark:text-white">Calendar</Text>
        <TouchableOpacity className="bg-primary/10 w-10 h-10 rounded-full items-center justify-center">
          <Ionicons name="add" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View className="flex-1">
        <CalendarProvider
          date={currentDate}
          onDateChanged={onDateChanged}
          showTodayButton
          theme={{
            todayButtonTextColor: colors.primary,
          }}
        >
          <ExpandableCalendar
            firstDay={1}
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
              textDayFontFamily: 'System',
              textMonthFontFamily: 'System',
              textDayHeaderFontFamily: 'System',
              textMonthFontWeight: 'bold',
            }}
          />
          <TimelineList
            events={events}
            timelineProps={{
              format24h: false,
              theme: {
                backgroundColor: isDark ? colors.dark : '#ffffff',
                timeLabelColor: colors.gray[500],
                lineColor: isDark ? colors.gray[800] : colors.gray[200],
              } as any
            }}
            showNowIndicator
            scrollToFirst
            initialTime={{ hour: 8, minutes: 0 }}
          />
        </CalendarProvider>
      </View>
    </ScreenLayout>
  );
}
