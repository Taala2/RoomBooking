import { formatTime, fromInputs } from '../utils/dates'

const DAY_MS = 24 * 60 * 60 * 1000
const HOUR_MARKS = [0, 3, 6, 9, 12, 15, 18, 21, 24]

// Position of a busy slot on the day bar, in percent; slots crossing midnight are clipped.
function slotPosition(slot, dayStart) {
  const start = Math.max(new Date(slot.start_time) - dayStart, 0)
  const end = Math.min(new Date(slot.end_time) - dayStart, DAY_MS)

  return { left: `${(start / DAY_MS) * 100}%`, width: `${((end - start) / DAY_MS) * 100}%` }
}

export function DaySchedule({ date, slots }) {
  const dayStart = fromInputs(date, '00:00')

  return (
    <div className="schedule">
      <div className="day-bar" aria-hidden="true">
        {slots.map((slot) => (
          <span key={slot.start_time} className="day-bar-busy" style={slotPosition(slot, dayStart)} />
        ))}
      </div>
      <div className="day-bar-hours" aria-hidden="true">
        {HOUR_MARKS.map((hour) => (
          <span key={hour}>{String(hour).padStart(2, '0')}</span>
        ))}
      </div>

      {slots.length === 0 ? (
        <p className="muted">В этот день комната свободна.</p>
      ) : (
        <ul className="slot-list" aria-label="Занятое время">
          {slots.map((slot) => (
            <li key={slot.start_time}>
              Занято: {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
