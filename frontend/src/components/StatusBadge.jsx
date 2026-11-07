import { bookingState } from '../utils/bookings'

const STATES = {
  active: { label: 'Активна', tone: 'success' },
  past: { label: 'Завершена', tone: 'neutral' },
  canceled: { label: 'Отменена', tone: 'warning' },
}

export function StatusBadge({ booking }) {
  const { label, tone } = STATES[bookingState(booking)]

  return <span className={`badge badge-${tone}`}>{label}</span>
}
