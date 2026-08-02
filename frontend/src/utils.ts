export function formatTime(value?: string) {
  if (!value) return '--:--';
  const date = new Date(`${value}`);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function toLocalDate(value?: string) {
  if (!value) return '';
  return new Date(value).toLocaleDateString();
}
