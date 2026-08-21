export const ENDPOINTS = {
  AUTH: {
    FIREBASE: '/auth/firebase',
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    VERIFY_OTP: '/auth/verify-otp',
    RESET_PASSWORD: '/auth/reset-password',
  },
  USERS: {
    ME: '/users/me',
    PASSWORD: '/users/me/password',
  },
  PREFERENCES: {
    GET: '/users/me/preferences',
    UPDATE: '/users/me/preferences',
  },
  TASKS: {
    BASE: '/tasks',
  },
  ROUTINES: {
    BASE: '/routines',
  },
  SCHEDULE: {
    BASE: '/schedules',
    DAILY: '/schedules/daily',
    WEEK: '/schedules/week/current',
    GENERATE: '/schedules/generate',
    GENERATE_MULTI: '/schedules/generate/multi-day',
    REGENERATE: '/schedules/regenerate',
  },
  AI: {
    CHAT: '/ai/chat',
    CHAT_NEW: '/ai/chat/new',
    CHAT_CONVERSATIONS: '/ai/chat/conversations',
    PARSE_ROUTINE: '/ai/parse-routine',
    ANALYZE: '/ai/analyze',
    SUGGESTIONS: '/ai/suggestions',
  },
  ANALYTICS: {
    BASE: '/analytics',
    DASHBOARD: '/analytics/dashboard',
    WEEKLY: '/analytics/weekly',
    MONTHLY: '/analytics/monthly',
    WEEKLY_REPORT: '/analytics/reports/weekly',
  },
  REMINDERS: {
    BASE: '/reminders',
    RECURRING: '/reminders/recurring',
    GENERATE_FROM_SCHEDULE: '/reminders/generate-from-schedule',
  },
  NOTIFICATIONS: {
    BASE: '/notifications',
    UNREAD_COUNT: '/notifications/unread-count',
    READ_ALL: '/notifications/read-all',
  },
  GAMIFICATION: {
    BASE: '/gamification',
    STATS: '/gamification/progress',
    LEADERBOARD: '/gamification/leaderboard',
  },
  DASHBOARD: {
    GET: '/analytics/dashboard',
  },
} as const;
