import { useCallback, useState } from 'react'
import { ArrowLeft, DoorOpen, UsersRound } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { createBooking } from '../api/bookings'
import { getBusySlots, getRoom } from '../api/rooms'
import { DaySchedule } from '../components/DaySchedule'
import { ErrorMessage, SuccessMessage } from '../components/ErrorMessage'
import { LoadingState } from '../components/States'
import { TimeRangeForm } from '../components/TimeRangeForm'
import { useAsync } from '../hooks/useAsync'
import { dayRange, formatDate, formatTime, todayInput } from '../utils/dates'

function BackLink() {
  return (
    <Link to="/rooms" className="back-link">
      <ArrowLeft size={14} aria-hidden="true" />
      Все комнаты
    </Link>
  )
}

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

  function handleDateChange(event) {
    // A cleared date input gives "": keep the previous day instead of an invalid date.
    if (event.target.value) {
      setDate(event.target.value)
      setSuccess(null)
    }
  }

  async function handleBook(start, end) {
    setSuccess(null)
    const booking = await createBooking(Number(roomId), start.toISOString(), end.toISOString())
    setSuccess(`Забронировано: ${formatDate(booking.start_time)}, ${formatTime(booking.start_time)} – ${formatTime(booking.end_time)}`)
    slots.reload()
  }

  if (room.error) {
    return (
      <div className="page">
        <BackLink />
        <ErrorMessage error={room.error} />
      </div>
    )
  }

  if (!room.data) {
    return <LoadingState />
  }

  return (
    <div className="page">
      <BackLink />

      <div className="room-hero">
        <span className="icon-tile" aria-hidden="true">
          <DoorOpen size={20} />
        </span>
        <div>
          <h2>{room.data.name}</h2>
          <span className="room-meta">
            <UsersRound size={14} aria-hidden="true" />
            до {room.data.capacity} чел.
            {room.data.description && ` · ${room.data.description}`}
          </span>
        </div>
      </div>

      <div className="booking-layout">
        <section className="card">
          <div className="card-header">
            <h2>Расписание</h2>
            <input
              className="input input-auto"
              type="date"
              aria-label="День расписания"
              value={date}
              onChange={handleDateChange}
              required
            />
          </div>

          <ErrorMessage error={slots.error} />
          {slots.data ? <DaySchedule date={date} slots={slots.data} /> : !slots.error && <LoadingState inline text="Загрузка расписания…" />}
        </section>

        <section className="card">
          <h2>Новая бронь</h2>
          <p className="muted small form-note">
            {formatDate(`${date}T00:00`)} · не дольше 5 часов. Если конец раньше начала — бронь до следующего дня.
          </p>
          {/* key: a new day resets the form to that day */}
          <TimeRangeForm key={date} initialDate={date} showDate={false} submitLabel="Забронировать" onSubmit={handleBook} />
          {success && (
            <div className="after-form">
              <SuccessMessage>{success}</SuccessMessage>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
