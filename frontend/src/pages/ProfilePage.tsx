import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { changePassword, deleteAccount, updateProfile } from '../api';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, signOut, refreshUser } = useAuth();

  // Profile form
  const [name, setName] = useState(user?.name ?? '');
  const [age, setAge] = useState(user?.age?.toString() ?? '');
  const [occupation, setOccupation] = useState(user?.occupation ?? '');
  const [timezone, setTimezone] = useState(user?.timezone ?? 'UTC');
  const [wakeTime, setWakeTime] = useState(user?.wake_time ?? '06:00');
  const [sleepTime, setSleepTime] = useState(user?.sleep_time ?? '23:00');
  const [profileMsg, setProfileMsg] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);

  // Password form
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  // Delete form
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleProfileUpdate = async (e: FormEvent) => {
    e.preventDefault();
    setProfileMsg(null);
    setProfileError(null);
    try {
      await updateProfile({
        name,
        age: age ? Number(age) : undefined,
        occupation,
        timezone,
        wake_time: wakeTime,
        sleep_time: sleepTime,
      });
      await refreshUser();
      setProfileMsg('Profile updated successfully');
    } catch (err) {
      setProfileError((err as Error).message);
    }
  };

  const handlePasswordChange = async (e: FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);
    setPasswordError(null);
    try {
      await changePassword(oldPassword, newPassword);
      setOldPassword('');
      setNewPassword('');
      setPasswordMsg('Password changed successfully');
    } catch (err) {
      setPasswordError((err as Error).message);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteError(null);
    try {
      await deleteAccount(deletePassword);
      signOut();
      navigate('/login');
    } catch (err) {
      setDeleteError((err as Error).message);
    }
  };

  return (
    <section className="screen animate-fade-in">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Profile</span>
          <h1>Your account</h1>
          <p>
            Update your personal info, change your password, or manage your
            account.
          </p>
        </div>
      </div>

      <div className="grid-layout settings-grid" style={{ marginTop: '20px' }}>
        {/* Profile card */}
        <article className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ margin: '0 0 16px', fontSize: '1.1rem' }}>
            Personal Information
          </h2>
          <form className="grid-form" onSubmit={handleProfileUpdate}>
            <label>
              Name
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </label>
            <label>
              Age
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="22"
              />
            </label>
            <label>
              Occupation
              <input
                type="text"
                value={occupation}
                onChange={(e) => setOccupation(e.target.value)}
                placeholder="Student"
              />
            </label>
            <label>
              Timezone
              <input
                type="text"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="UTC+05:00"
              />
            </label>
            <label>
              Wake time
              <input
                type="time"
                value={wakeTime}
                onChange={(e) => setWakeTime(e.target.value)}
              />
            </label>
            <label>
              Sleep time
              <input
                type="time"
                value={sleepTime}
                onChange={(e) => setSleepTime(e.target.value)}
              />
            </label>
            <div className="full-width">
              <button type="submit" className="button button-primary">
                Save Profile
              </button>
            </div>
          </form>
          {profileMsg && (
            <p
              style={{
                marginTop: '12px',
                color: 'var(--success)',
                fontWeight: 600,
                fontSize: '0.88rem',
              }}
            >
              {profileMsg}
            </p>
          )}
          {profileError && <p className="form-error">{profileError}</p>}
        </article>

        {/* Change password */}
        <article className="card">
          <h2 style={{ margin: '0 0 16px', fontSize: '1.1rem' }}>
            Change Password
          </h2>
          <form className="stacked-form" onSubmit={handlePasswordChange}>
            <label>
              Current Password
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </label>
            <label>
              New Password
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
              />
            </label>
            <button type="submit" className="button button-secondary">
              Change Password
            </button>
          </form>
          {passwordMsg && (
            <p
              style={{
                marginTop: '12px',
                color: 'var(--success)',
                fontWeight: 600,
                fontSize: '0.88rem',
              }}
            >
              {passwordMsg}
            </p>
          )}
          {passwordError && <p className="form-error">{passwordError}</p>}
        </article>

        {/* Delete account */}
        <article className="card">
          <h2
            style={{
              margin: '0 0 16px',
              fontSize: '1.1rem',
              color: 'var(--error)',
            }}
          >
            Danger Zone
          </h2>
          <p
            style={{
              color: 'var(--muted)',
              fontSize: '0.88rem',
              margin: '0 0 16px',
            }}
          >
            Permanently delete your account and all associated data. This action
            cannot be undone.
          </p>
          {!showDeleteConfirm ? (
            <button
              className="button button-danger"
              onClick={() => setShowDeleteConfirm(true)}
            >
              Delete Account
            </button>
          ) : (
            <div className="stacked-form" style={{ marginTop: 0 }}>
              <label>
                Confirm with your password
                <input
                  type="password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  placeholder="Enter password to confirm"
                />
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className="button button-danger"
                  onClick={handleDeleteAccount}
                >
                  Yes, Delete Forever
                </button>
                <button
                  className="button button-ghost"
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setDeletePassword('');
                  }}
                >
                  Cancel
                </button>
              </div>
              {deleteError && <p className="form-error">{deleteError}</p>}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
