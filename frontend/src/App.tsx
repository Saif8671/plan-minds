import { useEffect, useState } from 'react';
import logo from './assets/logo.png';
import {
  BrowserRouter,
  NavLink,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';
import { useAuth } from './context/useAuth';
import { getUnreadCount } from './api';
import SplashPage from './pages/SplashPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import AIRoutinePage from './pages/AIRoutinePage';
import PlannerPage from './pages/PlannerPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import CalendarPage from './pages/CalendarPage';
import ProfilePage from './pages/ProfilePage';
import ProtectedRoute from './pages/ProtectedRoute';
import AlarmManager from './components/AlarmManager';
import FloatingAssistant from './components/FloatingAssistant';
import './App.css';

const topNavItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/planner', label: 'Planner' },
  { to: '/calendar', label: 'Calendar' },
  { to: '/ai-routine', label: 'AI Routine' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/settings', label: 'Settings' },
];

function LiveClock() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div
      style={{
        fontWeight: 600,
        fontSize: '0.9rem',
        color: 'var(--text)',
        backgroundColor: 'var(--surface-muted)',
        padding: '8px 12px',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border)',
      }}
    >
      {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
    </div>
  );
}

function AppLayout() {
  const { user } = useAuth();
  const location = useLocation();
  const [unread, setUnread] = useState(0);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const isAuthPage = ['/', '/login', '/register'].includes(location.pathname);

  useEffect(() => {
    if (user) {
      getUnreadCount()
        .then((r) => setUnread(r.unread_count))
        .catch(() => {});
    }
  }, [user, location.pathname]);

  useEffect(() => {
    const savedTheme =
      localStorage.getItem('theme') === 'dark' ? 'dark' : 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('theme', nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  };

  return (
    <div className="app-shell">
      {!isAuthPage && <AlarmManager />}
      {!isAuthPage && <FloatingAssistant />}
      {!isAuthPage && (
        <header className="app-header">
          <div className="brand-block">
            <img src={logo} alt="PlanMind Logo" className="brand-logo" />
          </div>

          <nav className="top-nav" aria-label="Primary navigation">
            {topNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'active' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="header-actions">
            <LiveClock />
            <button
              type="button"
              className="icon-button"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? 'Sun' : 'Moon'}
            </button>
            <NavLink
              to="/settings"
              className="notification-bell"
              title="Notifications"
            >
              Bell
              {unread > 0 && (
                <span className="notification-badge">
                  {unread > 9 ? '9+' : unread}
                </span>
              )}
            </NavLink>
          </div>
        </header>
      )}

      <main className="app-content">
        <Routes>
          <Route path="/" element={<SplashPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/planner"
            element={
              <ProtectedRoute>
                <PlannerPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/calendar"
            element={
              <ProtectedRoute>
                <CalendarPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai-routine"
            element={
              <ProtectedRoute>
                <AIRoutinePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;
