# PlanMinds API Contract

This document defines the canonical DTOs (Data Transfer Objects) and API contracts between the mobile frontend and the FastAPI backend. It serves as the single source of truth for all API interactions.

## Base Response Format

All API endpoints return responses in the following format:

```typescript
type ApiResponse<T> = {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  }
}
```

## Authentication

### Login Request
```typescript
type LoginRequest = {
  email: string;
  password: string; // Required
}
```

### Register Request
```typescript
type RegisterRequest = {
  email: string;
  password: string; // Required, min length 8
  name: string;
}
```

### Auth Response
```typescript
type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string; // usually "bearer"
}
```
*Note: The frontend must explicitly fetch the user profile (`GET /users/me`) after storing these tokens.*

## Users & Preferences

### User Profile
```typescript
type UserResponse = {
  id: string;
  email: string;
  name: string | null;
  age: number | null;
  occupation: string | null;
  timezone: string;
  wake_time: string | null; // HH:MM:SS
  sleep_time: string | null; // HH:MM:SS
  working_days: string[] | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Routines

### Routine Create / Update
```typescript
type RoutineCreate = {
  title: string;
  description?: string;
  category?: string; // e.g. "work", "study", "health", "personal", "social", "other"
  priority?: string; // "low", "medium", "high", "urgent"
  frequency?: string; // "daily", "weekly", "monthly", "custom"
  estimated_duration?: number; // minutes
  preferred_time?: string; // HH:MM:SS
  tags?: string[];
  days_of_week?: number[]; // 0 = Monday, 6 = Sunday
  start_time?: string; // HH:MM:SS
  end_time?: string; // HH:MM:SS
}
```

## Schedules

### Schedule Create
```typescript
type ScheduleCreate = {
  title: string;
  description?: string;
  priority?: string; // "low", "medium", "high", "urgent"
  start_time: string; // ISO-8601 UTC
  end_time: string; // ISO-8601 UTC
  status?: string; // "draft", "active", "completed", "cancelled"
  category?: string;
}
```

### Schedule Block Move
```typescript
type ScheduleBlockMove = {
  new_start: string; // HH:MM:SS
  new_end: string; // HH:MM:SS
}
```

### Schedule Merge
```typescript
type ScheduleMergeRequest = {
  block_ids: string[]; // exactly 2 block IDs
  merged_title?: string;
}
```

### Validation Result
```typescript
type ValidationResult = {
  is_valid: boolean;
  conflicts: Array<{
    rule: string;
    message: string;
    block_ids: string[];
    severity: string;
  }>;
  warnings: string[];
}
```

## Tasks

### Task Create
```typescript
type TaskCreate = {
  title: string;
  description?: string;
  priority?: string;
  category?: string;
  duration?: number; // minutes
  deadline?: string; // ISO-8601 UTC
}
```

## Reminders
(Detailed contracts to be added as features are stabilized)

## Notifications
(Detailed contracts to be added as features are stabilized)

## Gamification & Analytics
(Detailed contracts to be added as features are stabilized)
