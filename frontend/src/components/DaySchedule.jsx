import { Clock } from 'lucide-react'

import { dayRange, formatTime } from '../utils/dates'

const HOUR_MARKS = [0, 3, 6, 9, 12, 15, 18, 21, 24]

// Position of a busy slot on the day bar, in percent; slots crossing midnight are clipped.
// The real day length is used: days with a clock change have 23 or 25 hours.
function slotPosition(slot, dayStart, dayLength) {
  const start = Math.max(new Date(slot.start_time) - dayStart, 0)
  const end = Math.min(new Date(slot.end_time) - dayStart, dayLength)

  return { left: `${(start / dayLength) * 100}%`, width: `${((end - start) / dayLength) * 100}%` }
}

export function DaySchedule({ date, slots }) {
  const range = dayRange(date)
  const dayStart = new Date(range.start)
  const dayLength = new Date(range.end) - dayStart

  return (
    <div>
      <div className="schedule-bar" aria-hidden="true">
        {slots.map((slot) => (
          <span key={slot.start_time} className="schedule-busy" style={slotPosition(slot, dayStart, dayLength)} />
        ))}
      </div>
      <div className="schedule-hours" aria-hidden="true">
        {HOUR_MARKS.map((hour) => (
          <span key={hour}>{String(hour).padStart(2, '0')}</span>
        ))}
      </div>

      {slots.length === 0 ? (
        <p className="muted">В этот день комната свободна.</p>
      ) : (
        <ul className="slot-chips" aria-label="Занятое время">
          {slots.map((slot) => (
            <li key={slot.start_time} className="slot-chip">
              <Clock size={13} aria-hidden="true" />
              Занято {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
