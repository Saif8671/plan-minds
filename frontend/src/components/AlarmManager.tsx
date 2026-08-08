import { useEffect, useState, useRef } from 'react';
import { getTodaySchedule, getReminders, updateReminder } from '../api';

export default function AlarmManager() {
  const [activeAlarm, setActiveAlarm] = useState<{
    title: string;
    time: string;
  } | null>(null);

  // Track which alarms have already rung today to prevent infinite loops
  const alarmedTasks = useRef<Set<string>>(new Set());
  const audioCtxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    // Check schedule every minute
    const interval = setInterval(async () => {
      try {
        const scheduleData = await getTodaySchedule().catch(() => null);
        if (!scheduleData || !scheduleData.generated_schedule) return;

        const now = new Date();
        const currentHours = now.getHours().toString().padStart(2, '0');
        const currentMinutes = now.getMinutes().toString().padStart(2, '0');
        const currentTime = `${currentHours}:${currentMinutes}`;

        const blocks = scheduleData.generated_schedule?.blocks ?? [];
        for (const block of blocks) {
          // If it's time to start the block and we haven't alarmed yet today
          const blockKey = `${scheduleData.date}-${block.title}-${block.start}`;
          if (
            block.start === currentTime &&
            !alarmedTasks.current.has(blockKey)
          ) {
            alarmedTasks.current.add(blockKey);
            triggerAlarm(block.title, block.start);
            break; // Only trigger one alarm at a time
          }
        }

        // Check reminders from backend
        const remindersData = await getReminders(0, 50, false).catch(() => null);
        if (remindersData) {
          for (const reminder of remindersData) {
            const reminderTime = new Date(reminder.reminder_time);
            if (reminderTime <= now && !reminder.is_sent) {
              triggerAlarm(reminder.title, reminderTime.toLocaleTimeString());
              // Show browser notification
              if (Notification.permission === 'granted') {
                new Notification(reminder.title, { body: reminder.message || 'Reminder' });
              }
              // Mark as sent
              await updateReminder(reminder.id, { is_sent: true }).catch(() => {});
            }
          }
        }
      } catch (err) {
        console.error('Failed to check alarms:', err);
      }
    }, 60000); // check every 60 seconds

    // Request notification permission if not asked
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    return () => clearInterval(interval);
  }, []);

  const triggerAlarm = (title: string, time: string) => {
    setActiveAlarm({ title, time });
    playBeepSequence();
  };

  const playBeepSequence = () => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (
        window.AudioContext || (window as any).webkitAudioContext
      )();
    }
    const ctx = audioCtxRef.current;
    if (ctx.state === 'suspended') {
      ctx.resume();
    }

    const playBeep = (startTime: number) => {
      const osc = ctx.createOscillator();
      const gainNode = ctx.createGain();
      osc.connect(gainNode);
      gainNode.connect(ctx.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, startTime); // 800Hz beep

      gainNode.gain.setValueAtTime(0, startTime);
      gainNode.gain.linearRampToValueAtTime(1, startTime + 0.05);
      gainNode.gain.setValueAtTime(1, startTime + 0.2);
      gainNode.gain.linearRampToValueAtTime(0, startTime + 0.3);

      osc.start(startTime);
      osc.stop(startTime + 0.3);
    };

    const now = ctx.currentTime;
    // Play a sequence of 3 beeps
    playBeep(now);
    playBeep(now + 0.4);
    playBeep(now + 0.8);
  };

  const dismissAlarm = () => {
    setActiveAlarm(null);
  };

  if (!activeAlarm) return null;

  return (
    <div className="modal-overlay" style={{ zIndex: 9999 }}>
      <div
        className="modal-panel"
        style={{ textAlign: 'center', maxWidth: '400px' }}
      >
        <div style={{ fontSize: '3rem', marginBottom: '10px' }}>⏰</div>
        <h2 style={{ marginBottom: '8px' }}>Time for your next task!</h2>
        <p
          style={{
            fontSize: '1.2rem',
            fontWeight: 600,
            color: 'var(--accent)',
            marginBottom: '4px',
          }}
        >
          {activeAlarm.title}
        </p>
        <p style={{ color: 'var(--muted)', marginBottom: '24px' }}>
          Scheduled for {activeAlarm.time}
        </p>
        <button
          className="button button-primary full-width"
          onClick={dismissAlarm}
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
