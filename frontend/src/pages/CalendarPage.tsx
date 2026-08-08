import { useCallback, useEffect, useState } from 'react';
import { getWeekSchedules } from '../api';
import type { ScheduleResponse } from '../types';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const getLocalDateString = (d = new Date()) => {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
};

export default function CalendarPage() {
  const [weekStart, setWeekStart] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay());
    d.setHours(0, 0, 0, 0);
    return d;
  });
  const [schedules, setSchedules] = useState<ScheduleResponse[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(
    getLocalDateString()
  );
  const [selectedSchedule, setSelectedSchedule] =
    useState<ScheduleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getWeekDates = () => {
    const dates: Date[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(weekStart);
      d.setDate(weekStart.getDate() + i);
      dates.push(d);
    }
    return dates;
  };

  const loadWeek = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const startStr = weekStart.toISOString().split('T')[0];
      const data = await getWeekSchedules(startStr);
      setSchedules(data);
    } catch (err) {
      setError((err as Error).message);
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  }, [weekStart]);

  useEffect(() => {
    void loadWeek();
  }, [loadWeek]);

  useEffect(() => {
    const found = schedules.find((s) => s.date === selectedDate);
    setSelectedSchedule(found || null);
  }, [selectedDate, schedules]);

  const prevWeek = () => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() - 7);
    setWeekStart(d);
  };

  const nextWeek = () => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + 7);
    setWeekStart(d);
  };

  const goToday = () => {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay());
    d.setHours(0, 0, 0, 0);
    setWeekStart(d);
    setSelectedDate(getLocalDateString());
  };

  const weekDates = getWeekDates();
  const today = getLocalDateString();
  const scheduleDates = new Set(schedules.map((s) => s.date));
  const selectedBlocks = selectedSchedule?.generated_schedule?.blocks ?? [];
  const selectedDateLabel = new Date(
    selectedDate + 'T00:00:00',
  ).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <section className="screen animate-fade-in">
      <div className="calendar-shell">
        <div className="hero-panel">
          <div>
            <span className="eyebrow">Calendar</span>
            <h1>Weekly schedule view</h1>
            <p>
              Navigate through your weeks and see scheduled blocks at a glance.
            </p>
          </div>
          <button className="button button-secondary" onClick={goToday}>
            Today
          </button>
        </div>

        <div className="calendar-toolbar">
          <div className="calendar-nav">
            <button
              className="button button-ghost button-sm"
              onClick={prevWeek}
            >
              ← Prev
            </button>
            <button
              className="button button-ghost button-sm"
              onClick={nextWeek}
            >
              Next →
            </button>
          </div>
          <div className="calendar-range-pill">
            <span>📅</span>
            <span>
              {weekDates[0].toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })}{' '}
              –{' '}
              {weekDates[6].toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
          </div>
        </div>

        <div className="summary-grid calendar-summary-grid">
          <div className="calendar-summary-card">
            <p className="card-eyebrow">Week overview</p>
            <h3>Balanced scheduling for the next 7 days.</h3>
            <p>
              {scheduleDates.size} day{scheduleDates.size === 1 ? '' : 's'}{' '}
              currently have scheduled items in this view.
            </p>
          </div>
          <div className="calendar-summary-card calendar-summary-card--accent">
            <p className="card-eyebrow">Selected day</p>
            <h3>{selectedDateLabel}</h3>
            <p>
              {selectedBlocks.length} planned block
              {selectedBlocks.length === 1 ? '' : 's'} ready to review.
            </p>
          </div>
        </div>

        <div className="calendar-grid-card">
          <div className="calendar-grid">
            {DAYS.map((d) => (
              <div key={d} className="calendar-day-label">
                {d}
              </div>
            ))}
            {weekDates.map((date) => {
              const dateStr = getLocalDateString(date);
              const isToday = dateStr === today;
              const isSelected = dateStr === selectedDate;
              const hasSchedule = scheduleDates.has(dateStr);
              return (
                <button
                  key={dateStr}
                  type="button"
                  className={`calendar-day ${isSelected ? 'active' : ''} ${hasSchedule ? 'has-schedule' : ''}`}
                  aria-pressed={isSelected}
                  onClick={() => setSelectedDate(dateStr)}
                >
                  <span className="calendar-day-number">{date.getDate()}</span>
                  {hasSchedule && <span className="calendar-day-dot" />}
                  {isToday && !isSelected && (
                    <span className="calendar-day-today">Today</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {error && <p className="form-error">{error}</p>}

        <div className="calendar-detail-card">
          <div className="calendar-detail-header">
            <div>
              <p className="card-eyebrow">Schedule details</p>
              <h2>{selectedDateLabel}</h2>
            </div>
            <span className="metric-pill">{selectedBlocks.length} blocks</span>
          </div>

          {loading ? (
            <div style={{ display: 'grid', gap: '10px' }}>
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="skeleton"
                  style={{ height: '56px', borderRadius: 'var(--radius-sm)' }}
                />
              ))}
            </div>
          ) : selectedBlocks.length > 0 ? (
            <div className="timeline-list">
              {selectedBlocks.map((block, i) => (
                <article key={`${block.title}-${i}`} className="timeline-card">
                  <div className="timeline-time">{block.start}</div>
                  <div>
                    <h3
                      style={{
                        margin: 0,
                        fontSize: '0.95rem',
                        fontWeight: 600,
                      }}
                    >
                      {block.title}
                    </h3>
                    <div className="task-meta" style={{ marginTop: '4px' }}>
                      <span>→ {block.end}</span>
                      {block.category && (
                        <span className={`badge badge-${block.category}`}>
                          {block.category}
                        </span>
                      )}
                      {block.is_fixed && (
                        <span className="badge badge-other">Fixed</span>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state calendar-empty-state">
              <h3>No schedule for this day</h3>
              <p>
                Generate a schedule from the AI Routine page or create tasks
                first.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
