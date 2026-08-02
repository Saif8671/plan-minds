export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  age?: number;
  occupation?: string;
  timezone?: string;
  wake_time?: string;
  sleep_time?: string;
  working_days?: string[];
  preferred_study_hours?: Record<string, unknown>;
  reminder_preferences?: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  schedule_id?: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category:
    'work' | 'study' | 'health' | 'personal' | 'meal' | 'sleep' | 'other';
  duration: number;
  travel_time_minutes: number;
  deadline?: string;
  reminder_time?: string;
  recurrence?: 'daily' | 'weekly' | 'monthly' | 'custom';
  recurrence_rule?: Record<string, unknown>;
  is_fixed: boolean;
  fixed_start?: string;
  fixed_end?: string;
  is_recurring: boolean;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface Schedule {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  start_time: string;
  end_time: string;
  status: 'draft' | 'active' | 'completed' | 'cancelled';
  category:
    'work' | 'study' | 'health' | 'personal' | 'meal' | 'sleep' | 'other';
  date?: string;
  generated_schedule?: GeneratedSchedule;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message?: string;
  notification_type:
    | 'schedule_generated'
    | 'task_reminder'
    | 'task_completed'
    | 'task_missed'
    | 'system';
  is_read: boolean;
  data?: Record<string, unknown>;
  created_at: string;
}

export interface ParsedRoutine {
  wake_time?: string;
  sleep_time?: string;
  fixed_events?: Array<{
    title: string;
    start: string;
    end: string;
    category?: string;
  }>;
  flexible_tasks?: Array<{
    title: string;
    duration: number;
    priority?: string;
    category?: string;
  }>;
  notes?: string;
}

export interface ScheduleBlock {
  title: string;
  start: string;
  end: string;
  task_id?: string;
  category?: string;
  is_fixed?: boolean;
}

export interface GeneratedSchedule {
  date?: string;
  wake_time?: string;
  sleep_time?: string;
  blocks?: ScheduleBlock[];
  unscheduled_tasks?: string[];
  metadata?: Record<string, unknown>;
}

export interface ScheduleResponse {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  priority: string;
  start_time: string;
  end_time: string;
  status: string;
  category: string;
  date?: string;
  generated_schedule?: GeneratedSchedule;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsDashboard {
  completion_rate: number;
  focus_hours: number;
  study_hours: number;
  average_sleep_hours?: number;
  missed_tasks: number;
  consistency_score: number;
  total_tasks: number;
  completed_tasks: number;
  category_breakdown: Array<{
    category: string;
    hours: number;
    task_count: number;
  }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface AIAnalyzeResponse {
  tasks: Array<{
    title: string;
    start?: string;
    end?: string;
    duration?: number;
    category?: string;
    priority?: string;
  }>;
  wake_time?: string;
  sleep_time?: string;
  notes?: string;
}
