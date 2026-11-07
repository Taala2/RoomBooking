// The user picks local date/time; the API receives ISO strings in UTC ("...Z").

const MAX_BOOKING_HOURS = 5
const HOUR_MS = 60 * 60 * 1000

function pad(value) {
  return String(value).padStart(2, '0')
}

// "YYYY-MM-DD" of a Date in local time (for <input type="date">).
export function toDateInput(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

// "HH:MM" of a Date in local time (for <input type="time">).
export function toTimeInput(date) {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function todayInput() {
  return toDateInput(new Date())
}

// Local date + time from inputs -> Date.
export function fromInputs(dateValue, timeValue) {
  return new Date(`${dateValue}T${timeValue}`)
}

// Start/end on one date; an end time not after the start means "next day" (e.g. 22:00-01:00).
export function intervalFromInputs(dateValue, startTime, endTime) {
  const start = fromInputs(dateValue, startTime)
  const end = fromInputs(dateValue, endTime)

  if (end <= start) {
    end.setDate(end.getDate() + 1)
  }

  return { start, end }
}

// Local day [00:00, next 00:00) as ISO strings for the busy-slots request.
export function dayRange(dateValue) {
  const start = fromInputs(dateValue, '00:00')
  const end = new Date(start)
  end.setDate(end.getDate() + 1)

  return { start: start.toISOString(), end: end.toISOString() }
}

export function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

export function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'short' })
}

// Same rules as the backend, checked before sending to give a quick message.
export function validateInterval(start, end) {
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return 'Укажите дату и время'
  }

  if (end <= start) {
    return 'Время окончания должно быть позже начала'
  }

  if (start < new Date()) {
    return 'Нельзя бронировать время в прошлом'
  }

  if (end - start > MAX_BOOKING_HOURS * HOUR_MS) {
    return `Максимальная длительность — ${MAX_BOOKING_HOURS} часов`
  }

  return null
}
