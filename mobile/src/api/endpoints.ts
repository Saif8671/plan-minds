export const ENDPOINTS = {
  AUTH: {
    FIREBASE: '/auth/firebase',
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
  USERS: {
    ME: '/users/me',
  },
  PREFERENCES: {
    GET: '/users/me/preferences',
    UPDATE: '/users/me/preferences',
  },
  TASKS: {
    BASE: '/tasks',
  },
  SCHEDULE: {
    BASE: '/schedules',
    TODAY: '/schedules/today/current',
    WEEK: '/schedules/week/current',
    GENERATE: '/schedules/generate',
    REGENERATE: '/schedules/regenerate',
  },
  AI: {
    CHAT: '/ai/chat',
    CHAT_NEW: '/ai/chat/new',
    CHAT_CONVERSATIONS: '/ai/chat/conversations',
    PARSE_ROUTINE: '/ai/parse-routine',
  },
  ANALYTICS: {
    BASE: '/analytics',
  },
  REMINDERS: {
    BASE: '/reminders',
  },
  GAMIFICATION: {
    BASE: '/gamification',
  },
  DASHBOARD: {
    GET: '/analytics/dashboard',
  },
} as const;
