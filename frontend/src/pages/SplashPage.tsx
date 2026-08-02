import logo from '../assets/logo.png';
import { NavLink } from 'react-router-dom';

export default function SplashPage() {
  return (
    <section
      className="screen"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '80vh',
      }}
    >
      <div
        className="hero-card animate-slide-up"
        style={{ textAlign: 'center', maxWidth: '540px' }}
      >
        <img
          src={logo}
          alt="PlanMind Logo"
          style={{ height: '160px', marginBottom: '24px' }}
        />
        <h1>Plan your day with calm precision.</h1>
        <p style={{ textAlign: 'center' }}>
          A minimal PlanMind workspace built to turn routines into polished
          daily plans, with AI-powered suggestions, clean analytics, and easy
          task management.
        </p>
        <div className="actions" style={{ justifyContent: 'center' }}>
          <NavLink to="/login" className="button button-primary">
            Sign in
          </NavLink>
          <NavLink to="/register" className="button button-secondary">
            Create account
          </NavLink>
        </div>
      </div>
    </section>
  );
}
