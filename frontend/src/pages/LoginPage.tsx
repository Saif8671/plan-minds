import { useState, type FormEvent } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { signIn, signInWithGoogle, error } = useAuth();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await signIn(email, password);
      navigate('/dashboard');
    } catch {
      // handled by auth context
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await signInWithGoogle();
      navigate('/dashboard');
    } catch {
      // handled by auth context
    }
  };

  return (
    <section className="screen screen-form">
      <div className="form-panel">
        <div className="form-header">
          <span className="eyebrow">Welcome back</span>
          <h1>Login to your account</h1>
        </div>
        <form className="stacked-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="hello@lovable.app"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              required
            />
          </label>
          <button type="submit" className="button button-primary">
            Continue
          </button>
        </form>
        <div className="auth-divider">
          <span>or continue with</span>
        </div>
        <button
          type="button"
          className="button button-secondary full-width"
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </button>
        {error ? <p className="form-error">{error}</p> : null}
        <p className="form-help">
          Don&apos;t have an account? <NavLink to="/register">Create one</NavLink>
        </p>
      </div>
    </section>
  );
}
