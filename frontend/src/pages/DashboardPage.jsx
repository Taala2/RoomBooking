import { useCallback, useState } from 'react'
import { Building2, CalendarCheck, CalendarPlus, Clock, DoorOpen, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

import { listMyBookingsWithRooms } from '../api/bookings'
import { listUsers } from '../api/users'
import { DateTile } from '../components/DateTile'
import { ErrorMessage } from '../components/ErrorMessage'
import { EmptyState, LoadingState } from '../components/States'
import { useAuth } from '../context/AuthContext'
import { useAsync } from '../hooks/useAsync'
import { isUpcoming } from '../utils/bookings'
import { formatDate, formatTime, toDateInput } from '../utils/dates'

const UPCOMING_PREVIEW = 4

function greeting(now) {
  const hour = now.getHours()

  if (hour < 12) {
    return 'Доброе утро'
  }

  return hour < 18 ? 'Добрый день' : 'Добрый вечер'
}

function StatCard({ icon: Icon, value, label }) {
  return (
    <div className="card stat">
      <span className="icon-tile" aria-hidden="true">
        <Icon size={20} />
      </span>
      <div>
        <p className="stat-value">{value}</p>
        <p className="stat-label">{label}</p>
      </div>
    </div>
  )
}

function NextBooking({ booking, roomName }) {
  if (!booking) {
    return (
      <EmptyState
        icon={CalendarCheck}
        title="Предстоящих броней нет"
        text="Выберите комнату и свободное время."
        action={<Link to="/rooms" className="button button-primary">Забронировать</Link>}
      />
    )
  }

  return (
    <div className="next-booking">
      <div className="next-booking-info">
        <DateTile iso={booking.start_time} />
        <div>
          <p className="next-booking-title">{roomName}</p>
          <p className="muted">
            {formatDate(booking.start_time)}, {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
          </p>
        </div>
      </div>
      <Link to={`/rooms/${booking.room_id}`} className="button">
        Расписание комнаты
      </Link>
    </div>
  )
}

function QuickActions({ isAdmin }) {
  const actions = [
    { to: '/rooms', icon: DoorOpen, label: 'Найти свободную комнату' },
    { to: '/bookings', icon: CalendarCheck, label: 'Мои брони' },
    ...(isAdmin
      ? [
          { to: '/admin/rooms', icon: Building2, label: 'Управление комнатами' },
          { to: '/admin/users', icon: Users, label: 'Пользователи' },
        ]
      : []),
  ]

  return (
    <section className="card">
      <h2 className="card-header">Быстрые действия</h2>
      <div className="quick-actions">
        {actions.map(({ to, icon: Icon, label }) => (
          <Link key={to} to={to} className="button">
            <Icon size={16} aria-hidden="true" />
            {label}
          </Link>
        ))}
      </div>
    </section>
  )
}

export function DashboardPage() {
  const { user, isAdmin } = useAuth()
  // Fixed when the page opens: greeting and "today" do not change between renders.
  const [now] = useState(() => new Date())

  const load = useCallback(async () => {
    const [mine, users] = await Promise.all([listMyBookingsWithRooms(), isAdmin ? listUsers({ limit: 1 }) : null])
    return { ...mine, usersTotal: users?.total }
  }, [isAdmin])
  const { data, error, loading } = useAsync(load)

  if (error) {
    return <ErrorMessage error={error} />
  }

  if (loading && !data) {
    return <LoadingState />
  }

  const upcoming = data.bookings.filter(isUpcoming)
  const today = toDateInput(now)
  const todayCount = upcoming.filter((booking) => toDateInput(new Date(booking.start_time)) === today).length
  const roomName = (booking) => data.roomNames[booking.room_id] ?? `Комната #${booking.room_id}`

  return (
    <div className="page">
      <div className="page-intro">
        <div>
          <p className="greeting">
            {greeting(now)}, {user.login}
          </p>
          <p className="muted">{now.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
        </div>
        <Link to="/rooms" className="button button-primary">
          <CalendarPlus size={16} aria-hidden="true" />
          Забронировать
        </Link>
      </div>

      <div className="stats">
        <StatCard icon={CalendarCheck} value={upcoming.length} label="Предстоящие брони" />
        <StatCard icon={Clock} value={todayCount} label="Брони на сегодня" />
        <StatCard icon={DoorOpen} value={data.roomsTotal} label="Комнат доступно" />
        {isAdmin && <StatCard icon={Users} value={data.usersTotal} label="Пользователей" />}
      </div>

      <div className="dashboard-grid">
        <div className="stack">
          <section className="card">
            <h2 className="card-header">Ближайшая бронь</h2>
            <NextBooking booking={upcoming[0]} roomName={upcoming[0] && roomName(upcoming[0])} />
          </section>

          {upcoming.length > 1 && (
            <section className="card">
              <div className="card-header">
                <h2>Дальше по расписанию</h2>
                <Link to="/bookings" className="small">
                  Все брони
                </Link>
              </div>
              <ul className="mini-list">
                {upcoming.slice(1, UPCOMING_PREVIEW + 1).map((booking) => (
                  <li key={booking.id}>
                    <span>{roomName(booking)}</span>
                    <span className="muted small">
                      {formatDate(booking.start_time)}, {formatTime(booking.start_time)}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        <QuickActions isAdmin={isAdmin} />
      </div>
    </div>
  )
}
