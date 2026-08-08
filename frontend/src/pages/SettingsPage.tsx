import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function SettingsPage() {
  const { user, signOut } = useAuth();
  const [theme, setTheme] = useState(
    () => localStorage.getItem('theme') || 'light',
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <section className="screen animate-fade-in">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Settings</span>
          <h1>Customize your experience.</h1>
          <p>Manage appearance, notifications, and your account preferences.</p>
        </div>
      </div>

      <div className="grid-layout settings-grid" style={{ marginTop: '16px' }}>
        <article className="card">
          <h2
            style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 600 }}
          >
            Profile
          </h2>
          <p
            style={{
              color: 'var(--muted)',
              fontSize: '0.88rem',
              margin: '0 0 14px',
            }}
          >
            {user?.name ?? 'No name set'} · {user?.email}
          </p>
          <NavLink to="/profile" className="button button-secondary button-sm">
            Edit Profile
          </NavLink>
        </article>

        <article className="card">
          <h2
            style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 600 }}
          >
            Appearance
          </h2>
          <p
            style={{
              color: 'var(--muted)',
              fontSize: '0.88rem',
              margin: '0 0 14px',
            }}
          >
            Currently using {theme} mode.
          </p>
          <button
            className="button button-secondary button-sm"
            onClick={toggleTheme}
          >
            Switch to {theme === 'light' ? 'dark' : 'light'} mode
          </button>
        </article>

        <article className="card">
          <h2
            style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 600 }}
          >
            AI Settings
          </h2>
          <p style={{ color: 'var(--muted)', fontSize: '0.88rem' }}>
            Adjust schedule generation and suggestion behavior from the AI
            routine page.
          </p>
          <NavLink
            to="/ai-routine"
            className="button button-ghost button-sm"
            style={{ marginTop: '12px' }}
          >
            Go to AI Routine
          </NavLink>
        </article>

        <article className="card">
          <h2
            style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 600 }}
          >
            Account
          </h2>
          <p
            style={{
              color: 'var(--muted)',
              fontSize: '0.88rem',
              margin: '0 0 14px',
            }}
          >
            Sign out of your current session.
          </p>
          <button className="button button-danger button-sm" onClick={signOut}>
            Sign out
          </button>
        </article>
      </div>
    </section>
  );
}
