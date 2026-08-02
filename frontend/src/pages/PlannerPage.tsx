import { useEffect, useState, type FormEvent } from 'react';
import { NavLink } from 'react-router-dom';
import {
  createTask,
  deleteTask,
  getTasks,
  getTodaySchedule,
  updateTask,
} from '../api';
import type { PaginatedResponse, ScheduleResponse, Task } from '../types';

const CATEGORIES = ['work', 'study', 'health', 'personal', 'meal', 'sleep', 'other'] as const;
const PRIORITIES = ['low', 'medium', 'high', 'urgent'] as const;

export default function PlannerPage() {
  // Shared state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Timeline state
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [tasks, setTasks] = useState<PaginatedResponse<Task> | null>(null);

  // Form state
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<string>('medium');
  const [category, setCategory] = useState<string>('other');
  const [duration, setDuration] = useState(60);
  const [isFixed, setIsFixed] = useState(false);
  const [fixedStart, setFixedStart] = useState('');
  const [fixedEnd, setFixedEnd] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [scheduleData, tasksData] = await Promise.all([
        getTodaySchedule().catch(() => null),
        getTasks(1, 100), // load up to 100 tasks for today's lookup
      ]);
      setSchedule(scheduleData);
      setTasks(tasksData);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openCreate = () => {
    setEditingTask(null);
    setTitle('');
    setDescription('');
    setPriority('medium');
    setCategory('other');
    setDuration(60);
    setIsFixed(false);
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
    setIsFixed(task.is_fixed);
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
        is_fixed: isFixed,
        fixed_start: isFixed ? fixedStart : undefined,
        fixed_end: isFixed ? fixedEnd : undefined,
      };
      if (editingTask) {
        await updateTask(editingTask.id, data);
      } else {
        await createTask(data);
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await deleteTask(taskId);
      loadData();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleToggleComplete = async (taskId: string, isCompleted: boolean) => {
    try {
      const newCompleted = !isCompleted;
      await updateTask(taskId, {
        completed: newCompleted,
        status: newCompleted ? 'completed' : 'pending',
      });
      loadData();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const getStatusDisplay = (task?: Task, blockStart?: string) => {
    if (task?.completed) return 'Complete';
    if (task?.status === 'skipped') return 'Skipped';
    
    // Check if upcoming
    if (blockStart) {
      const now = new Date();
      const currentHours = now.getHours();
      const currentMinutes = now.getMinutes();
      const [blockHours, blockMinutes] = blockStart.split(':').map(Number);
      
      if (blockHours > currentHours || (blockHours === currentHours && blockMinutes > currentMinutes)) {
        return 'Upcoming';
      }
    }
    
    return 'Pending';
  };

  const blocks = schedule?.generated_schedule?.blocks ?? [];

  return (
    <section className="screen animate-fade-in">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Planner</span>
          <h1>Daily Timeline</h1>
          <p>Review and edit today's AI-generated schedule.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <NavLink to="/tasks" className="button button-secondary">
            View Backlog
          </NavLink>
          <button className="button button-primary" onClick={openCreate}>
            + New Task
          </button>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
        <div className="card-header">
          <div>
            <p className="card-eyebrow">Timeline</p>
            <h2>Today's schedule</h2>
          </div>
        </div>

        {loading && !schedule ? (
          <div className="timeline-list">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: '72px', borderRadius: 'var(--radius)' }} />
            ))}
          </div>
        ) : blocks.length > 0 ? (
          <div className="timeline-list">
            {blocks.map((block, index) => {
              const matchingTask = tasks?.items.find((t) => t.id === block.task_id);
              const isCompleted = matchingTask?.completed;
              const displayStatus = getStatusDisplay(matchingTask, block.start);

              return (
                <article key={`${block.title}-${index}`} className="timeline-card" style={{ opacity: isCompleted ? 0.6 : 1, padding: '16px', position: 'relative' }}>
                  <div className="timeline-time" style={{ textDecoration: isCompleted ? 'line-through' : 'none' }}>
                    {block.start}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, textDecoration: isCompleted ? 'line-through' : 'none' }}>
                        {block.title}
                      </h3>
                      {matchingTask && (
                         <span className={`status-chip status-${matchingTask.status === 'skipped' ? 'skipped' : isCompleted ? 'completed' : displayStatus === 'Upcoming' ? 'upcoming' : 'pending'}`} style={{ fontSize: '0.75rem', padding: '2px 6px', textTransform: 'capitalize' }}>
                           {displayStatus}
                         </span>
                      )}
                    </div>
                    <div className="task-meta" style={{ marginTop: '8px' }}>
                      <span>→ {block.end}</span>
                      {block.category && (
                        <span className={`badge badge-${block.category}`}>
                          {block.category}
                        </span>
                      )}
                      {block.is_fixed && (
                        <span className="badge badge-other">Fixed</span>
                      )}
                    </div>
                    <div className="timeline-actions" style={{ marginTop: '12px' }}>
                      {block.task_id && (
                        <>
                          <button
                            className={`button button-sm ${isCompleted ? 'button-ghost' : 'button-primary'}`}
                            onClick={() => handleToggleComplete(block.task_id!, !!isCompleted)}
                          >
                            {isCompleted ? 'Undo Complete' : '✓ Complete'}
                          </button>
                          {matchingTask && (
                             <button
                               className="button button-sm button-ghost"
                               onClick={() => openEdit(matchingTask)}
                             >
                               Edit
                             </button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <div className="empty-state calendar-empty-state" style={{ height: '100%', marginTop: '32px' }}>
            <h3>No schedule for today</h3>
            <p>Go to the Dashboard to generate your daily AI Routine.</p>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingTask ? 'Edit Task' : 'New Task'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form className="stacked-form" onSubmit={handleSubmit}>
              <label>
                Title
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
              </label>
              <label>
                Description
                <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <label>
                  Priority
                  <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                    {PRIORITIES.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Category
                  <select value={category} onChange={(e) => setCategory(e.target.value)}>
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </label>
              </div>
              <label>
                Duration (minutes)
                <input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} min={1} max={1440} />
              </label>
              <label style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
                <input type="checkbox" checked={isFixed} onChange={(e) => setIsFixed(e.target.checked)} style={{ width: 'auto' }} />
                Fixed time slot
              </label>
              {isFixed && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <label>
                    Start
                    <input type="time" value={fixedStart} onChange={(e) => setFixedStart(e.target.value)} />
                  </label>
                  <label>
                    End
                    <input type="time" value={fixedEnd} onChange={(e) => setFixedEnd(e.target.value)} />
                  </label>
                </div>
              )}
              <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                <button type="submit" className="button button-primary" style={{ flex: 1 }}>
                  {editingTask ? 'Save Changes' : 'Create Task'}
                </button>
                {editingTask && (
                  <button type="button" className="button button-danger" onClick={() => { handleDelete(editingTask.id); setShowModal(false); }}>
                    Delete
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
