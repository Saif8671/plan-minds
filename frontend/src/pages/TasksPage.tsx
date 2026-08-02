import { useEffect, useState, type FormEvent } from 'react';
import { createTask, deleteTask, getTasks, updateTask } from '../api';
import type { PaginatedResponse, Task } from '../types';

const CATEGORIES = [
  'work',
  'study',
  'health',
  'personal',
  'meal',
  'sleep',
  'other',
] as const;
const PRIORITIES = ['low', 'medium', 'high', 'urgent'] as const;
const STATUSES = [
  'pending',
  'in_progress',
  'completed',
  'skipped',
  'cancelled',
] as const;

export default function TasksPage() {
  const [tasks, setTasks] = useState<PaginatedResponse<Task> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [page, setPage] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<string>('medium');
  const [category, setCategory] = useState<string>('other');
  const [duration, setDuration] = useState(60);
  const [travelTime, setTravelTime] = useState(0);
  const [isFixed, setIsFixed] = useState(false);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrence, setRecurrence] = useState<
    'daily' | 'weekly' | 'monthly' | 'custom'
  >('daily');
  const [fixedStart, setFixedStart] = useState('');
  const [fixedEnd, setFixedEnd] = useState('');

  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTasks(page, 20, filterStatus || undefined);
      setTasks(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [page, filterStatus]);

  const openCreate = () => {
    setEditingTask(null);
    setTitle('');
    setDescription('');
    setPriority('medium');
    setCategory('other');
    setDuration(60);
    setTravelTime(0);
    setIsFixed(false);
    setIsRecurring(false);
    setRecurrence('daily');
    setFixedStart('');
    setFixedEnd('');
    setShowModal(true);
  };

  const openEdit = (task: Task) => {
    setEditingTask(task);
    setTitle(task.title);
    setDescription(task.description ?? '');
    setPriority(task.priority);
    setCategory(task.category);
    setDuration(task.duration);
    setTravelTime(task.travel_time_minutes ?? 0);
    setIsFixed(task.is_fixed);
    setIsRecurring(task.is_recurring);
    setRecurrence(
      (task.recurrence as 'daily' | 'weekly' | 'monthly' | 'custom') ?? 'daily',
    );
    setFixedStart(task.fixed_start ?? '');
    setFixedEnd(task.fixed_end ?? '');
    setShowModal(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const data: Partial<Task> = {
        title,
        description: description || undefined,
        priority: priority as Task['priority'],
        category: category as Task['category'],
        duration,
        travel_time_minutes: travelTime,
        is_fixed: isFixed,
        is_recurring: isRecurring,
        recurrence: recurrence === 'custom' ? undefined : recurrence,
        fixed_start: isFixed ? fixedStart : undefined,
        fixed_end: isFixed ? fixedEnd : undefined,
      };
      if (editingTask) {
        await updateTask(editingTask.id, data);
      } else {
        await createTask(data);
      }
      setShowModal(false);
      loadTasks();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const newCompleted = !task.completed;
      await updateTask(task.id, {
        completed: newCompleted,
        status: newCompleted ? 'completed' : 'pending',
      });
      loadTasks();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await deleteTask(taskId);
      loadTasks();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const totalPages = tasks ? Math.ceil(tasks.total / tasks.page_size) : 0;

  return (
    <section className="screen animate-fade-in">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Tasks</span>
          <h1>Manage all your tasks</h1>
          <p>
            Create, organize, and track your daily tasks with priority and
            category filters.
          </p>
        </div>
        <button className="button button-primary" onClick={openCreate}>
          + New Task
        </button>
      </div>

      {/* Filter bar */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginTop: '16px',
        }}
      >
        <button
          className={`button button-sm ${!filterStatus ? 'button-primary' : 'button-ghost'}`}
          onClick={() => {
            setFilterStatus('');
            setPage(1);
          }}
        >
          All
        </button>
        {STATUSES.map((s) => (
          <button
            key={s}
            className={`button button-sm ${filterStatus === s ? 'button-primary' : 'button-ghost'}`}
            onClick={() => {
              setFilterStatus(s);
              setPage(1);
            }}
          >
            {s.replace('_', ' ')}
          </button>
        ))}
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <div className="task-list" style={{ marginTop: '16px' }}>
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: '64px', width: '100%' }}
            />
          ))}
        </div>
      ) : tasks && tasks.items.length > 0 ? (
        <>
          <div className="task-list" style={{ marginTop: '16px' }}>
            {tasks.items.map((task) => (
              <div key={task.id} className="task-item">
                <button
                  className={`task-check ${task.completed ? 'checked' : ''}`}
                  onClick={() => handleToggleComplete(task)}
                  title={task.completed ? 'Mark incomplete' : 'Mark complete'}
                />
                <div className="task-item-content">
                  <div
                    className="task-title"
                    style={{
                      textDecoration: task.completed ? 'line-through' : 'none',
                      opacity: task.completed ? 0.6 : 1,
                    }}
                  >
                    <span
                      className={`priority-dot priority-${task.priority}`}
                    />
                    {task.title}
                  </div>
                  <div className="task-meta">
                    <span className={`badge badge-${task.category}`}>
                      {task.category}
                    </span>
                    <span className={`status-chip status-${task.status}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                    <span>{task.duration}m</span>
                    {task.is_fixed && task.fixed_start && (
                      <span>
                        {task.fixed_start} – {task.fixed_end}
                      </span>
                    )}
                  </div>
                </div>
                <div className="task-item-actions">
                  <button
                    className="button button-ghost button-sm"
                    onClick={() => openEdit(task)}
                  >
                    Edit
                  </button>
                  <button
                    className="button button-danger button-sm"
                    onClick={() => handleDelete(task.id)}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '8px',
                marginTop: '16px',
              }}
            >
              <button
                className="button button-ghost button-sm"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                ← Prev
              </button>
              <span
                style={{
                  padding: '8px 12px',
                  color: 'var(--muted)',
                  fontSize: '0.85rem',
                }}
              >
                Page {page} of {totalPages}
              </span>
              <button
                className="button button-ghost button-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <h3>No tasks yet</h3>
          <p>Create your first task to get started with schedule management.</p>
          <button className="button button-primary" onClick={openCreate}>
            + Create Task
          </button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingTask ? 'Edit Task' : 'New Task'}</h2>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ✕
              </button>
            </div>
            <form className="stacked-form" onSubmit={handleSubmit}>
              <label>
                Title
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Task title"
                  required
                />
              </label>
              <label>
                Description
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional description..."
                />
              </label>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px',
                }}
              >
                <label>
                  Priority
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                  >
                    {PRIORITIES.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Category
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <label>
                Duration (minutes)
                <input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  min={1}
                  max={1440}
                />
              </label>
              <label>
                Travel time (minutes)
                <input
                  type="number"
                  value={travelTime}
                  onChange={(e) => setTravelTime(Number(e.target.value))}
                  min={0}
                  max={240}
                />
              </label>
              <label
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <input
                  type="checkbox"
                  checked={isRecurring}
                  onChange={(e) => setIsRecurring(e.target.checked)}
                  style={{ width: 'auto' }}
                />
                Recurring task
              </label>
              {isRecurring && (
                <label>
                  Recurrence
                  <select
                    value={recurrence}
                    onChange={(e) =>
                      setRecurrence(
                        e.target.value as
                          'daily' | 'weekly' | 'monthly' | 'custom',
                      )
                    }
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="custom">Custom</option>
                  </select>
                </label>
              )}
              <label
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <input
                  type="checkbox"
                  checked={isFixed}
                  onChange={(e) => setIsFixed(e.target.checked)}
                  style={{ width: 'auto' }}
                />
                Fixed time slot
              </label>
              {isFixed && (
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '12px',
                  }}
                >
                  <label>
                    Start
                    <input
                      type="time"
                      value={fixedStart}
                      onChange={(e) => setFixedStart(e.target.value)}
                    />
                  </label>
                  <label>
                    End
                    <input
                      type="time"
                      value={fixedEnd}
                      onChange={(e) => setFixedEnd(e.target.value)}
                    />
                  </label>
                </div>
              )}
              <button
                type="submit"
                className="button button-primary full-width"
              >
                {editingTask ? 'Save Changes' : 'Create Task'}
              </button>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
