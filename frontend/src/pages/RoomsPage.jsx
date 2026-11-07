import { useCallback, useState } from 'react'
import { ArrowLeft, ArrowRight, DoorOpen, UsersRound } from 'lucide-react'
import { Link } from 'react-router-dom'

import { listRooms } from '../api/rooms'
import { Button } from '../components/Button'
import { ErrorMessage } from '../components/ErrorMessage'
import { EmptyState, LoadingState } from '../components/States'
import { useAsync } from '../hooks/useAsync'

const PAGE_SIZE = 12

function RoomCard({ room }) {
  return (
    <li className="card room-card">
      <span className="icon-tile" aria-hidden="true">
        <DoorOpen size={20} />
      </span>
      <div>
        <h2 className="next-booking-title">{room.name}</h2>
        <span className="room-meta">
          <UsersRound size={14} aria-hidden="true" />
          до {room.capacity} чел.
        </span>
      </div>
      <p className="room-description">{room.description || 'Без описания'}</p>
      <Link to={`/rooms/${room.id}`} className="button button-sm">
        Расписание и бронь
        <ArrowRight size={14} aria-hidden="true" />
      </Link>
    </li>
  )
}

export function RoomsPage() {
  const [offset, setOffset] = useState(0)
  const load = useCallback(() => listRooms({ limit: PAGE_SIZE, offset }), [offset])
  const { data, error, loading } = useAsync(load)

  const total = data?.total ?? 0
  const hasPrevious = offset > 0
  const hasNext = offset + PAGE_SIZE < total

  return (
    <div className="page">
      <div className="page-intro">
        <div>
          <p className="greeting">Выберите комнату</p>
          <p className="muted">Откройте расписание, чтобы увидеть свободное время и забронировать.</p>
        </div>
      </div>

      <ErrorMessage error={error} />
      {loading && !data && <LoadingState />}
      {data && data.items.length === 0 && (
        <EmptyState icon={DoorOpen} title="Комнат пока нет" text="Администратор ещё не добавил ни одной комнаты." />
      )}

      {data && data.items.length > 0 && (
        <ul className="room-grid">
          {data.items.map((room) => (
            <RoomCard key={room.id} room={room} />
          ))}
        </ul>
      )}

      {(hasPrevious || hasNext) && (
        <div className="pagination">
          <Button size="sm" icon={ArrowLeft} disabled={!hasPrevious} onClick={() => setOffset(offset - PAGE_SIZE)}>
            Назад
          </Button>
          <span className="muted small">
            {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} из {total}
          </span>
          <Button size="sm" disabled={!hasNext} onClick={() => setOffset(offset + PAGE_SIZE)}>
            Вперёд
            <ArrowRight size={14} aria-hidden="true" />
          </Button>
        </div>
      )}
    </div>
  )
}
