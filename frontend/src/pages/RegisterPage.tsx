import { useState, type FormEvent } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { signUp, signInWithGoogle, error } = useAuth();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await signUp(email, password, name);
      navigate('/onboarding');
    } catch {
      // handled by auth context
    }
  };

  const handleGoogleSignup = async () => {
    try {
      await signInWithGoogle();
      navigate('/onboarding');
    } catch {
      // handled by auth context
    }
  };

  return (
    <section className="screen screen-form">
      <div className="form-panel">
        <div className="form-header">
          <span className="eyebrow">Create account</span>
          <h1>Get started with Lovable</h1>
        </div>
        <form className="stacked-form" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Saif"
            />
          </label>
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
            Create account
          </button>
        </form>
        <div className="auth-divider">
          <span>or continue with</span>
        </div>
        <button
          type="button"
          className="button button-secondary full-width"
          onClick={handleGoogleSignup}
        >
          Continue with Google
        </button>
        {error ? <p className="form-error">{error}</p> : null}
        <p className="form-help">
          Already have an account? <NavLink to="/login">Log in</NavLink>
        </p>
      </div>
    </section>
  );
}
