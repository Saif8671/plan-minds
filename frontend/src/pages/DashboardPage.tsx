import { useEffect, useState, useRef } from 'react';
import { NavLink } from 'react-router-dom';
import { fetchProfile, getAnalytics, getTodaySchedule, chatAI } from '../api';
import type { AnalyticsDashboard, ScheduleResponse, User } from '../types';

const DEFAULT_FOCUS_MINUTES = 25;

export default function DashboardPage() {
  const [profile, setProfile] = useState<User | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  
  // Timer State
  const [focusMinutes, setFocusMinutes] = useState(DEFAULT_FOCUS_MINUTES);
  const [focusActive, setFocusActive] = useState(false);
  const [focusRemaining, setFocusRemaining] = useState(DEFAULT_FOCUS_MINUTES * 60);
  
  // Chatbot State
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'ai'; text: string }[]>([
    { role: 'ai', text: 'Hi! I am your AI Routiner. How can I help you organize today?' }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const [profileData, analyticsData, scheduleData] =
          await Promise.allSettled([
            fetchProfile(),
            getAnalytics(),
            getTodaySchedule(),
          ]);
        if (profileData.status === 'fulfilled') setProfile(profileData.value);
        if (analyticsData.status === 'fulfilled')
          setAnalytics(analyticsData.value);
        if (scheduleData.status === 'fulfilled')
          setSchedule(scheduleData.value);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const blocks = schedule?.generated_schedule?.blocks ?? [];
  const primaryBlock = blocks[0];
  const secondaryBlock = blocks[1];
  const completionRate = Math.min(
    100,
    Math.max(0, analytics?.completion_rate ?? 0),
  );

  // Timer logic
  useEffect(() => {
    if (!focusActive) return;
    const timer = window.setInterval(() => {
      setFocusRemaining((prev) => {
        if (prev <= 1) {
          window.clearInterval(timer);
          setFocusActive(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [focusActive]);

  const startFocusTimer = () => setFocusActive(true);
  const pauseFocusTimer = () => setFocusActive(false);
  const resetFocusTimer = () => {
    setFocusActive(false);
    setFocusRemaining(focusMinutes * 60);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
      .toString()
      .padStart(2, '0');
    const secs = Math.floor(seconds % 60)
      .toString()
      .padStart(2, '0');
    return `${mins}:${secs}`;
  };

  // Chatbot logic
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage = chatInput.trim();
    setChatMessages((prev) => [...prev, { role: 'user', text: userMessage }]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      const context = schedule?.generated_schedule?.blocks ?? [];
      const res = await chatAI(userMessage, context);
      setChatMessages((prev) => [...prev, { role: 'ai', text: res.reply }]);
      
      // Refresh schedule to reflect any AI updates
      try {
        const updatedSchedule = await getTodaySchedule();
        setSchedule(updatedSchedule);
      } catch (err) {
        console.error('Failed to reload schedule after chat', err);
      }
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'ai', text: 'Sorry, I encountered an error.' }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <section className="screen animate-fade-in">
      <div className="dashboard-shell">
        <div className="hero-panel hero-panel--compact">
          <div className="hero-copy">
            <span className="eyebrow">
              {greeting()}, {profile?.name ?? 'there'}
            </span>
            <h1>Your day is organized, focused, and ready to move.</h1>
            <p>
              Review your momentum, open the next task, and keep your routine on
              track with a cleaner view of the day ahead.
            </p>
          </div>
          <div className="hero-actions">
            <NavLink to="/planner" className="button button-secondary">
              View Planner
            </NavLink>
          </div>
        </div>

        {loading ? (
          <div className="dashboard-grid" aria-label="Loading dashboard">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton dashboard-card-skeleton" style={{ height: '200px' }} />
            ))}
          </div>
        ) : error ? (
          <p className="form-error">{error}</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Top Row: AI Routine Chatbot & Timer */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              {/* AI Chatbot */}
              <article className="card" style={{ display: 'flex', flexDirection: 'column', height: '350px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                    AI Routine
                  </h2>
                  <NavLink to="/ai-routine" className="button button-ghost button-sm" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                    View Full ↗
                  </NavLink>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '8px', padding: '4px' }}>
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} style={{ 
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      backgroundColor: msg.role === 'user' ? 'var(--accent)' : 'var(--surface-muted)',
                      color: msg.role === 'user' ? '#fff' : 'var(--text)',
                      padding: '8px 12px',
                      borderRadius: '12px',
                      maxWidth: '85%',
                      fontSize: '0.85rem'
                    }}>
                      {msg.text}
                    </div>
                  ))}
                  {isChatLoading && (
                    <div style={{ alignSelf: 'flex-start', padding: '8px 12px', borderRadius: '12px', backgroundColor: 'var(--surface-muted)', fontSize: '0.85rem' }}>
                      <span className="skeleton" style={{ width: '40px', height: '12px', display: 'inline-block' }}></span>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                <form onSubmit={handleChatSubmit} style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Tell me your routine..."
                    style={{ flex: 1, padding: '8px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', background: 'var(--surface)', color: 'inherit' }}
                    disabled={isChatLoading}
                  />
                  <button type="submit" className="button button-primary button-sm" disabled={isChatLoading || !chatInput.trim()}>
                    Send
                  </button>
                </form>
              </article>

              {/* Timer */}
              <article className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', height: '350px' }}>
                <h2 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600, width: '100%', textAlign: 'left' }}>
                  Focus Timer
                </h2>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                  <p style={{ fontSize: '4rem', fontWeight: 700, margin: '0 0 20px 0', lineHeight: 1 }}>
                    {formatTime(focusRemaining)}
                  </p>
                  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Min:</label>
                      <input
                        type="number"
                        min={1}
                        max={90}
                        value={focusMinutes}
                        onChange={(e) => {
                          setFocusMinutes(Number(e.target.value));
                          if (!focusActive) setFocusRemaining(Number(e.target.value) * 60);
                        }}
                        style={{ width: '60px', padding: '4px', textAlign: 'center', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', background: 'var(--surface)', color: 'inherit' }}
                      />
                    </div>
                    <button
                      className="button button-primary button-sm"
                      onClick={focusActive ? pauseFocusTimer : startFocusTimer}
                      style={{ minWidth: '80px' }}
                    >
                      {focusActive ? 'Pause' : 'Play'}
                    </button>
                    <button
                      className="button button-ghost button-sm"
                      onClick={resetFocusTimer}
                    >
                      Reset
                    </button>
                  </div>
                </div>
              </article>
            </div>

            {/* Bottom Row: Analytics & Current/Next Tasks */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <article className="card card-strong" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div className="card-header">
                  <div>
                    <p className="card-eyebrow">Today’s progress</p>
                    <h2>Progress snapshot</h2>
                  </div>
                  <span className="metric-pill">
                    {analytics?.completion_rate ?? 0}%
                  </span>
                </div>

                <div className="progress-track" aria-label="Completion progress">
                  <span
                    className="progress-fill"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
                <p className="progress-caption">
                  Momentum is at {completionRate}% today.
                </p>
                <p
                  style={{
                    marginTop: '8px',
                    color: 'var(--muted)',
                    fontSize: '0.84rem',
                  }}
                >
                  Consistency {analytics?.consistency_score ?? 0}% ·{' '}
                  {analytics?.missed_tasks ?? 0} missed
                </p>

                <div className="metric-stack" style={{ marginTop: 'auto', paddingTop: '24px' }}>
                  <div className="metric-block">
                    <p className="metric-value">{analytics?.focus_hours ?? 0}h</p>
                    <p className="metric-label">Focus hours</p>
                  </div>
                  <div className="metric-block">
                    <p className="metric-value">
                      {analytics?.completed_tasks ?? 0}/
                      {analytics?.total_tasks ?? 0}
                    </p>
                    <p className="metric-label">Tasks done</p>
                  </div>
                </div>
              </article>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <article className="card" style={{ flex: 1 }}>
                  <div className="card-header">
                    <div>
                      <p className="card-eyebrow">Current focus</p>
                      <h2>Now</h2>
                    </div>
                  </div>
                  {primaryBlock ? (
                    <>
                      <p className="task-title">{primaryBlock.title}</p>
                      <p className="task-meta">
                        {primaryBlock.start} → {primaryBlock.end}
                      </p>
                      {primaryBlock.category && (
                        <span className={`badge badge-${primaryBlock.category}`}>
                          {primaryBlock.category}
                        </span>
                      )}
                    </>
                  ) : (
                    <p className="empty-copy">No tasks scheduled today</p>
                  )}
                </article>

                <article className="card" style={{ flex: 1 }}>
                  <div className="card-header">
                    <div>
                      <p className="card-eyebrow">Next up</p>
                      <h2>Coming next</h2>
                    </div>
                  </div>
                  {secondaryBlock ? (
                    <>
                      <p className="task-title">{secondaryBlock.title}</p>
                      <p className="task-meta">
                        {secondaryBlock.start} → {secondaryBlock.end}
                      </p>
                    </>
                  ) : (
                    <p className="empty-copy">Nothing else scheduled</p>
                  )}
                </article>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
