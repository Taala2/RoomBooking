import { useState } from 'react'
import { CalendarCheck, Clock, Pencil, X } from 'lucide-react'
import { Link } from 'react-router-dom'

import { cancelBooking, changeBooking, listMyBookingsWithRooms } from '../api/bookings'
import { Button } from '../components/Button'
import { DateTile } from '../components/DateTile'
import { ErrorMessage } from '../components/ErrorMessage'
import { EmptyState, LoadingState } from '../components/States'
import { StatusBadge } from '../components/StatusBadge'
import { TimeRangeForm } from '../components/TimeRangeForm'
import { useAsync } from '../hooks/useAsync'
import { isUpcoming } from '../utils/bookings'
import { formatDate, formatTime, toDateInput, toTimeInput } from '../utils/dates'

function BookingItem({ booking, roomName, onChanged }) {
  const [moving, setMoving] = useState(false)
  const [canceling, setCanceling] = useState(false)
  const [error, setError] = useState(null)
  const start = new Date(booking.start_time)
  const end = new Date(booking.end_time)
  const upcoming = isUpcoming(booking)

  async function handleCancel() {
    if (!window.confirm(`Отменить бронь «${roomName}» ${formatDate(booking.start_time)}?`)) {
      return
    }

    setError(null)
    setCanceling(true)

    try {
      await cancelBooking(booking.id)
      onChanged()
    } catch (err) {
      setError(err)
    } finally {
      setCanceling(false)
    }
  }

  async function handleMove(newStart, newEnd) {
    await changeBooking(booking.id, newStart.toISOString(), newEnd.toISOString())
    setMoving(false)
    onChanged()
  }

  return (
    <li className={`card booking-row${upcoming ? '' : ' is-past'}`}>
      <DateTile iso={booking.start_time} />

      <div className="booking-main">
        <Link to={`/rooms/${booking.room_id}`} className="booking-room">
          {roomName}
        </Link>
        <span className="booking-time">
          <Clock size={13} aria-hidden="true" />
          {formatDate(booking.start_time)}, {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
        </span>
      </div>

      <StatusBadge booking={booking} />

      {upcoming && !moving && (
        <div className="actions">
          <Button size="sm" icon={Pencil} onClick={() => setMoving(true)}>
            Перенести
          </Button>
          <Button size="sm" variant="danger" icon={X} loading={canceling} onClick={handleCancel}>
            Отменить
          </Button>
        </div>
      )}

      {moving && (
        <TimeRangeForm
          inline
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

function BookingSection({ title, bookings, roomNames, onChanged, empty }) {
  return (
    <section>
      <div className="section-title">
        <h2>{title}</h2>
        <span className="count">{bookings.length}</span>
      </div>

      {bookings.length === 0 ? (
        empty
      ) : (
        <ul className="booking-list">
          {bookings.map((booking) => (
            <BookingItem
              key={booking.id}
              booking={booking}
              roomName={roomNames[booking.room_id] ?? `Комната #${booking.room_id}`}
              onChanged={onChanged}
            />
          ))}
        </ul>
      )}
    </section>
  )
}

export function MyBookingsPage() {
  const { data, error, loading, reload } = useAsync(listMyBookingsWithRooms)

  if (error) {
    return <ErrorMessage error={error} />
  }

  if (loading && !data) {
    return <LoadingState />
  }

  const upcoming = data.bookings.filter(isUpcoming)
  const history = data.bookings.filter((booking) => !isUpcoming(booking)).reverse()

  return (
    <div className="page">
      <BookingSection
        title="Предстоящие"
        bookings={upcoming}
        roomNames={data.roomNames}
        onChanged={reload}
        empty={
          <div className="card">
            <EmptyState
              icon={CalendarCheck}
              title="Предстоящих броней нет"
              text="Выберите комнату и свободное время."
              action={<Link to="/rooms" className="button button-primary">Забронировать</Link>}
            />
          </div>
        }
      />

      <BookingSection
        title="История"
        bookings={history}
        roomNames={data.roomNames}
        onChanged={reload}
        empty={<p className="muted">Прошедших и отменённых броней пока нет.</p>}
      />
    </div>
  )
}
