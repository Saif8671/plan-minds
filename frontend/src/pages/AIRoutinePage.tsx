import { useEffect, useState, type FormEvent } from 'react';
import { parseRoutine, generateSchedule } from '../api';
import type { ParsedRoutine } from '../types';

export default function AIRoutinePage() {
  const [routine, setRoutine] = useState('');
  const [parsed, setParsed] = useState<ParsedRoutine | null>(null);
  const [scheduleId, setScheduleId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [voiceHint, setVoiceHint] = useState(
    'Voice input is ready. Try saying your routine aloud.',
  );

  useEffect(() => {
    if (!(
      'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
    )) {
      setVoiceHint(
        'Voice input is not available in this browser. You can still type your routine.',
      );
    }
  }, []);

  const handleVoiceInput = () => {
    const SpeechRecognitionCtor =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) {
      setVoiceHint('Speech recognition is not supported here.');
      return;
    }

    const recognition = new SpeechRecognitionCtor();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () =>
      setVoiceHint('Voice input stopped. Please try again.');
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(' ');
      setRoutine((prev) => (prev ? `${prev}\n${transcript}` : transcript));
      setVoiceHint('Voice input captured. Review and generate your schedule.');
    };
    recognition.start();
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const parsedRoutine = await parseRoutine(routine);
      setParsed(parsedRoutine);
      const schedule = await generateSchedule(undefined, parsedRoutine);
      setScheduleId(schedule.id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="screen screen-form">
      <div className="form-panel wide-panel">
        <div className="form-header">
          <span className="eyebrow">AI Routine</span>
          <h1>Describe your day in plain language.</h1>
          <p>
            Tell Lovable your routine and we’ll generate a structured schedule
            for you.
          </p>
        </div>
        <form className="stacked-form" onSubmit={handleSubmit}>
          <label className="full-width">
            Routine description
            <textarea
              rows={10}
              value={routine}
              onChange={(event) => setRoutine(event.target.value)}
              placeholder={`Describe your daily routine...\n\nExample:\nI wake up at 6.\nCollege 9 to 4.\nGym at 6.\nNeed 2 hours DSA.\nNeed IELTS preparation.`}
            />
          </label>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="button button-secondary"
              onClick={handleVoiceInput}
              disabled={isListening}
            >
              {isListening ? 'Listening…' : '🎤 Voice input'}
            </button>
            <button
              type="submit"
              className="button button-primary full-width"
              disabled={loading || !routine.trim()}
            >
              {loading ? 'Generating…' : 'Generate schedule'}
            </button>
          </div>
          <p style={{ margin: 0, color: 'var(--muted)', fontSize: '0.84rem' }}>
            {voiceHint}
          </p>
        </form>
        {error ? <p className="form-error">{error}</p> : null}

        {parsed ? (
          <section className="card parsed-summary">
            <h2>Parsed routine</h2>
            <div className="summary-grid">
              <div>
                <strong>Wake</strong>
                <p>{parsed.wake_time ?? '—'}</p>
              </div>
              <div>
                <strong>Sleep</strong>
                <p>{parsed.sleep_time ?? '—'}</p>
              </div>
            </div>
            <div>
              <strong>Fixed events</strong>
              <ul>
                {parsed.fixed_events?.map((item, index) => (
                  <li
                    key={index}
                  >{`${item.title} ${item.start}–${item.end}`}</li>
                ))}
              </ul>
              <strong>Flexible tasks</strong>
              <ul>
                {parsed.flexible_tasks?.map((item, index) => (
                  <li key={index}>{`${item.title} · ${item.duration}m`}</li>
                ))}
              </ul>
            </div>
          </section>
        ) : null}

        {scheduleId ? (
          <p className="form-help">Schedule generated: {scheduleId}</p>
        ) : null}
      </div>
    </section>
  );
}
