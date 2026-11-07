import { useCallback, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { createBooking } from '../api/bookings'
import { getBusySlots, getRoom } from '../api/rooms'
import { DaySchedule } from '../components/DaySchedule'
import { ErrorMessage, SuccessMessage } from '../components/ErrorMessage'
import { TimeRangeForm } from '../components/TimeRangeForm'
import { useAsync } from '../hooks/useAsync'
import { dayRange, formatDate, formatTime, todayInput } from '../utils/dates'

export function RoomPage() {
  const { roomId } = useParams()
  const [date, setDate] = useState(todayInput)
  const [success, setSuccess] = useState(null)

  const loadRoom = useCallback(() => getRoom(roomId), [roomId])
  const room = useAsync(loadRoom)

  const loadSlots = useCallback(() => {
    const { start, end } = dayRange(date)
    return getBusySlots(roomId, start, end)
  }, [roomId, date])
  const slots = useAsync(loadSlots)

  async function handleBook(start, end) {
    setSuccess(null)
    const booking = await createBooking(Number(roomId), start.toISOString(), end.toISOString())
    setSuccess(`Забронировано: ${formatDate(booking.start_time)}, ${formatTime(booking.start_time)} – ${formatTime(booking.end_time)}`)
    await slots.reload()
  }

  if (room.error) {
    return (
      <section>
        <ErrorMessage error={room.error} />
        <Link to="/">← К списку комнат</Link>
      </section>
    )
  }

  if (!room.data) {
    return <p className="muted">Загрузка…</p>
  }

  return (
    <section>
      <Link to="/" className="muted">
        ← К списку комнат
      </Link>
      <h1>{room.data.name}</h1>
      <p className="muted">Вместимость: {room.data.capacity} чел.</p>
      {room.data.description && <p>{room.data.description}</p>}

      <div className="card">
        <label className="inline-label">
          День
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
        </label>

        <ErrorMessage error={slots.error} />
        {slots.data && <DaySchedule date={date} slots={slots.data} />}
      </div>

      <div className="card">
        <h2>Забронировать на {formatDate(`${date}T00:00`)}</h2>
        <p className="muted">Не дольше 5 часов. Брони «встык» разрешены.</p>
        {/* key: a new day resets the form to that day */}
        <TimeRangeForm key={date} initialDate={date} showDate={false} submitLabel="Забронировать" onSubmit={handleBook} />
        <SuccessMessage>{success}</SuccessMessage>
      </div>
    </section>
  )
}
