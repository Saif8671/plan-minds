import type {
  AIAnalyzeResponse,
  AnalyticsDashboard,
  Notification,
  PaginatedResponse,
  ParsedRoutine,
  Schedule,
  ScheduleResponse,
  Task,
  TokenResponse,
  User,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const TOKEN_KEY = 'lovable_access_token';
const REFRESH_KEY = 'lovable_refresh_token';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string, refreshToken: string) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

async function authFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    ...options,
    headers,
  });

  // Auto-refresh on 401
  if (response.status === 401 && localStorage.getItem(REFRESH_KEY)) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${getToken()}`;
      const retry = await fetch(`${API_BASE_URL}${path}`, {
        credentials: 'include',
        ...options,
        headers,
      });
      if (retry.ok) {
        if (retry.status === 204) return undefined as T;
        return retry.json() as Promise<T>;
      }
    }
    clearToken();
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function tryRefreshToken(): Promise<boolean> {
  try {
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) return false;

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const tokens = (await response.json()) as TokenResponse;
    setToken(tokens.access_token, tokens.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// ─── Auth ──────────────────────────────────────────────────────────────

export async function login(email: string, password: string) {
  return authFetch<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function register(email: string, password: string, name?: string) {
  return authFetch<TokenResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, name }),
  });
}

export async function exchangeFirebaseToken(idToken: string) {
  const response = await fetch(`${API_BASE_URL}/auth/firebase`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }

  return response.json() as Promise<TokenResponse>;
}

// ─── User ──────────────────────────────────────────────────────────────

export async function fetchProfile() {
  return authFetch<User>('/users/me');
}

export async function updateProfile(data: Partial<User>) {
  return authFetch<User>('/users/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function changePassword(oldPassword: string, newPassword: string) {
  return authFetch<{ message: string }>('/users/me/password', {
    method: 'PUT',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });
}

export async function deleteAccount(password: string) {
  return authFetch<{ message: string }>('/users/me', {
    method: 'DELETE',
    body: JSON.stringify({ password }),
  });
}

// ─── Tasks ─────────────────────────────────────────────────────────────

export async function createTask(data: Partial<Task>) {
  return authFetch<Task>('/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getTasks(page = 1, pageSize = 20, status?: string) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (status) params.set('status', status);
  return authFetch<PaginatedResponse<Task>>(`/tasks?${params}`);
}

export async function getTask(taskId: string) {
  return authFetch<Task>(`/tasks/${taskId}`);
}

export async function updateTask(taskId: string, data: Partial<Task>) {
  return authFetch<Task>(`/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteTask(taskId: string) {
  return authFetch<void>(`/tasks/${taskId}`, { method: 'DELETE' });
}

// ─── Schedules ─────────────────────────────────────────────────────────

export async function createSchedule(data: Partial<Schedule>) {
  return authFetch<ScheduleResponse>('/schedules', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSchedules(page = 1, pageSize = 20) {
  return authFetch<PaginatedResponse<ScheduleResponse>>(
    `/schedules?page=${page}&page_size=${pageSize}`,
  );
}

export async function getSchedule(id: string) {
  return authFetch<ScheduleResponse>(`/schedules/${id}`);
}

export async function updateSchedule(id: string, data: Partial<Schedule>) {
  return authFetch<ScheduleResponse>(`/schedules/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteSchedule(id: string) {
  return authFetch<void>(`/schedules/${id}`, { method: 'DELETE' });
}

export async function parseRoutine(routineText: string, timezone?: string) {
  return authFetch<ParsedRoutine>('/ai/parse-routine', {
    method: 'POST',
    body: JSON.stringify({ routine_text: routineText, timezone }),
  });
}

export async function generateSchedule(
  targetDate?: string,
  parsedRoutine?: ParsedRoutine,
) {
  return authFetch<ScheduleResponse>('/schedules/generate', {
    method: 'POST',
    body: JSON.stringify({
      target_date: targetDate,
      include_parsed_routine: parsedRoutine,
    }),
  });
}

export async function getTodaySchedule() {
  return authFetch<ScheduleResponse>('/schedules/today/current');
}

export async function getWeekSchedules(start?: string) {
  const params = start ? `?start=${start}` : '';
  return authFetch<ScheduleResponse[]>(`/schedules/week/current${params}`);
}

// ─── AI ────────────────────────────────────────────────────────────────

export async function analyzeRoutine(text: string, timezone?: string) {
  return authFetch<AIAnalyzeResponse>('/ai/analyze', {
    method: 'POST',
    body: JSON.stringify({ text, timezone }),
  });
}

export async function chatAI(message: string, context?: any) {
  return authFetch<{ reply: string }>('/ai/chat', {
    method: 'POST',
    body: JSON.stringify({ message, context }),
  });
}

// ─── Analytics ─────────────────────────────────────────────────────────

export async function getAnalytics() {
  return authFetch<AnalyticsDashboard>('/analytics/dashboard');
}

// ─── Notifications ─────────────────────────────────────────────────────

export async function getNotifications(
  skip = 0,
  limit = 50,
  unreadOnly = false,
) {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
    unread_only: String(unreadOnly),
  });
  return authFetch<Notification[]>(`/notifications?${params}`);
}

export async function getUnreadCount() {
  return authFetch<{ unread_count: number }>('/notifications/unread-count');
}

export async function markNotificationRead(id: string) {
  return authFetch<Notification>(`/notifications/${id}/read`, {
    method: 'PATCH',
  });
}

export async function markAllNotificationsRead() {
  return authFetch<{ message: string }>('/notifications/read-all', {
    method: 'POST',
  });
}

export async function deleteNotification(id: string) {
  return authFetch<void>(`/notifications/${id}`, { method: 'DELETE' });
}

export { getToken, setToken, clearToken };
