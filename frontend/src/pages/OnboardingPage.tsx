import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { updateProfile } from '../api';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name ?? '');
  const [age, setAge] = useState(user?.age ?? '');
  const [occupation, setOccupation] = useState(user?.occupation ?? '');
  const [timezone, setTimezone] = useState(user?.timezone ?? 'UTC');
  const [wakeTime, setWakeTime] = useState(user?.wake_time ?? '06:00');
  const [sleepTime, setSleepTime] = useState(user?.sleep_time ?? '23:00');
  const [workingDays, setWorkingDays] = useState('Mon–Fri');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      await updateProfile({
        name,
        age: age ? Number(age) : undefined,
        occupation,
        timezone,
        wake_time: wakeTime,
        sleep_time: sleepTime,
        working_days:
          workingDays === 'Every day'
            ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            : workingDays === 'Mon–Sat'
              ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
              : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
      });
      await refreshUser();
      navigate('/dashboard');
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="screen screen-form">
      <div className="form-panel wide-panel">
        <div className="form-header">
          <span className="eyebrow">Onboarding</span>
          <h1>Tell us a little about your routine</h1>
          <p>Set up your wake times, schedule preferences, and availability.</p>
        </div>
        <form className="grid-form" onSubmit={handleSubmit}>
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
            Age
            <input
              type="number"
              value={age}
              onChange={(event) => setAge(event.target.value)}
              placeholder="22"
            />
          </label>
          <label>
            Occupation
            <input
              type="text"
              value={occupation}
              onChange={(event) => setOccupation(event.target.value)}
              placeholder="Student"
            />
          </label>
          <label>
            Timezone
            <input
              type="text"
              value={timezone}
              onChange={(event) => setTimezone(event.target.value)}
              placeholder="UTC+05:00"
            />
          </label>
          <label>
            Wake time
            <input
              type="time"
              value={wakeTime}
              onChange={(event) => setWakeTime(event.target.value)}
            />
          </label>
          <label>
            Sleep time
            <input
              type="time"
              value={sleepTime}
              onChange={(event) => setSleepTime(event.target.value)}
            />
          </label>
          <label className="full-width">
            Work days
            <select
              value={workingDays}
              onChange={(event) => setWorkingDays(event.target.value)}
            >
              <option>Mon–Fri</option>
              <option>Mon–Sat</option>
              <option>Every day</option>
            </select>
          </label>
          <button type="submit" className="button button-primary full-width">
            Save profile
          </button>
        </form>
        {error ? <p className="form-error">{error}</p> : null}
      </div>
    </section>
  );
}
