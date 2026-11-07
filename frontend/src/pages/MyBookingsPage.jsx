import { useState } from 'react'
import { Link } from 'react-router-dom'

import { cancelBooking, changeBooking, listMyBookings } from '../api/bookings'
import { listRooms } from '../api/rooms'
import { ErrorMessage } from '../components/ErrorMessage'
import { TimeRangeForm } from '../components/TimeRangeForm'
import { useAsync } from '../hooks/useAsync'
import { formatDate, formatTime, toDateInput, toTimeInput } from '../utils/dates'

const ROOMS_LIMIT = 100

async function loadBookingsWithRooms() {
  const [bookings, rooms] = await Promise.all([listMyBookings(), listRooms({ limit: ROOMS_LIMIT })])
  const roomNames = Object.fromEntries(rooms.items.map((room) => [room.id, room.name]))

  return { bookings, roomNames }
}

function isUpcoming(booking) {
  return booking.status === 'active' && new Date(booking.end_time) > new Date()
}

function BookingItem({ booking, roomName, onChanged }) {
  const [moving, setMoving] = useState(false)
  const [error, setError] = useState(null)
  const start = new Date(booking.start_time)
  const end = new Date(booking.end_time)
  const upcoming = isUpcoming(booking)

  async function handleCancel() {
    if (!window.confirm(`Отменить бронь «${roomName}» ${formatDate(booking.start_time)}?`)) {
      return
    }

    setError(null)

    try {
      await cancelBooking(booking.id)
      await onChanged()
    } catch (err) {
      setError(err)
    }
  }

  async function handleMove(newStart, newEnd) {
    await changeBooking(booking.id, newStart.toISOString(), newEnd.toISOString())
    setMoving(false)
    await onChanged()
  }

  return (
    <li className="card booking">
      <div className="booking-info">
        <Link to={`/rooms/${booking.room_id}`}>
          <strong>{roomName}</strong>
        </Link>
        <span>
          {formatDate(booking.start_time)}, {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
        </span>
        <span className={`badge badge-${booking.status}`}>{booking.status === 'active' ? 'активна' : 'отменена'}</span>
      </div>

      {upcoming && !moving && (
        <div className="form-actions">
          <button type="button" className="button-secondary" onClick={() => setMoving(true)}>
            Перенести
          </button>
          <button type="button" className="button-danger" onClick={handleCancel}>
            Отменить
          </button>
        </div>
      )}

      {moving && (
        <TimeRangeForm
          initialDate={toDateInput(start)}
          initialStart={toTimeInput(start)}
          initialEnd={toTimeInput(end)}
          submitLabel="Сохранить"
          onSubmit={handleMove}
          onCancel={() => setMoving(false)}
        />
      )}

      <ErrorMessage error={error} />
    </li>
  )
}

export function MyBookingsPage() {
  const { data, error, loading, reload } = useAsync(loadBookingsWithRooms)

  if (error) {
    return <ErrorMessage error={error} />
  }

  if (loading && !data) {
    return <p className="muted">Загрузка…</p>
  }

  const upcoming = data.bookings.filter(isUpcoming)
  const history = data.bookings.filter((booking) => !isUpcoming(booking)).reverse()

  function renderList(bookings, emptyText) {
    if (bookings.length === 0) {
      return <p className="muted">{emptyText}</p>
    }

    return (
      <ul className="booking-list">
        {bookings.map((booking) => (
          <BookingItem
            key={booking.id}
            booking={booking}
            roomName={data.roomNames[booking.room_id] ?? `Комната #${booking.room_id}`}
            onChanged={reload}
          />
        ))}
      </ul>
    )
  }

  return (
    <section>
      <h1>Мои брони</h1>

      <h2>Предстоящие</h2>
      {renderList(upcoming, 'Предстоящих броней нет.')}

      <h2>Прошедшие и отменённые</h2>
      {renderList(history, 'Пока пусто.')}
    </section>
  )
}
