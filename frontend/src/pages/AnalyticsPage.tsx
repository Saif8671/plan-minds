import { useEffect, useState } from 'react';
import { getAnalytics } from '../api';
import type { AnalyticsDashboard } from '../types';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getAnalytics();
        setAnalytics(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    loadAnalytics();
  }, []);

  return (
    <section className="screen animate-fade-in">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Analytics</span>
          <h1>See how your week is trending.</h1>
          <p>
            Track completion, focus time, study hours, and category breakdowns
            in one view.
          </p>
        </div>
      </div>

      {loading ? (
        <div
          className="grid-layout analytics-grid"
          style={{ marginTop: '16px' }}
        >
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: '130px', borderRadius: 'var(--radius)' }}
            />
          ))}
        </div>
      ) : error ? (
        <p className="form-error">{error}</p>
      ) : analytics ? (
        <>
          <div
            className="grid-layout analytics-grid"
            style={{ marginTop: '16px' }}
          >
            <article className="card card-strong">
              <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Completion Rate
              </h2>
              <p className="metric">{analytics.completion_rate ?? 0}%</p>
              <p
                style={{
                  color: 'var(--muted)',
                  fontSize: '0.82rem',
                  margin: '4px 0 0',
                }}
              >
                {analytics.completed_tasks} of {analytics.total_tasks} tasks
                done
              </p>
            </article>
            <article className="card">
              <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Focus Hours
              </h2>
              <p className="metric">{analytics.focus_hours ?? 0}h</p>
            </article>
            <article className="card">
              <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Study Hours
              </h2>
              <p className="metric">{analytics.study_hours ?? 0}h</p>
            </article>
            <article className="card">
              <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Consistency
              </h2>
              <p className="metric">{analytics.consistency_score ?? 0}%</p>
              <p
                style={{
                  color: 'var(--muted)',
                  fontSize: '0.82rem',
                  margin: '4px 0 0',
                }}
              >
                {analytics.missed_tasks} task
                {analytics.missed_tasks !== 1 ? 's' : ''} missed
              </p>
            </article>
          </div>

          {/* Category breakdown */}
          {analytics.category_breakdown &&
            analytics.category_breakdown.length > 0 && (
              <article className="card" style={{ marginTop: '16px' }}>
                <h2
                  style={{
                    margin: '0 0 14px',
                    fontSize: '0.95rem',
                    fontWeight: 600,
                  }}
                >
                  Category Breakdown
                </h2>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {analytics.category_breakdown.map((cat) => (
                    <div
                      key={cat.category}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                      }}
                    >
                      <span className={`badge badge-${cat.category}`}>
                        {cat.category}
                      </span>
                      <div
                        style={{
                          flex: 1,
                          height: '8px',
                          background: 'var(--surface-muted)',
                          borderRadius: 'var(--radius-pill)',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            height: '100%',
                            width: `${Math.min((cat.hours / Math.max(analytics.focus_hours, 1)) * 100, 100)}%`,
                            background: 'var(--accent)',
                            borderRadius: 'var(--radius-pill)',
                            transition: 'width 0.5s ease',
                          }}
                        />
                      </div>
                      <span
                        style={{
                          fontSize: '0.82rem',
                          color: 'var(--muted)',
                          minWidth: '60px',
                          textAlign: 'right',
                        }}
                      >
                        {cat.hours}h · {cat.task_count} tasks
                      </span>
                    </div>
                  ))}
                </div>
              </article>
            )}
        </>
      ) : (
        <div className="empty-state">
          <h3>No analytics available</h3>
          <p>Complete some tasks to start tracking your progress.</p>
        </div>
      )}
    </section>
  );
}
