import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { listRooms } from '../api/rooms'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../context/AuthContext'
import { useAsync } from '../hooks/useAsync'

const PAGE_SIZE = 12

export function RoomsPage() {
  const { user } = useAuth()
  const [offset, setOffset] = useState(0)
  const load = useCallback(() => listRooms({ limit: PAGE_SIZE, offset }), [offset])
  const { data, error, loading } = useAsync(load)

  const total = data?.total ?? 0
  const hasPrevious = offset > 0
  const hasNext = offset + PAGE_SIZE < total

  return (
    <section>
      <h1>Комнаты</h1>
      {!user && (
        <p className="muted">
          Чтобы посмотреть расписание и забронировать, <Link to="/login">войдите</Link>.
        </p>
      )}

      <ErrorMessage error={error} />
      {loading && !data && <p className="muted">Загрузка…</p>}
      {data && data.items.length === 0 && <p className="muted">Комнат пока нет.</p>}

      <ul className="room-grid">
        {data?.items.map((room) => (
          <li key={room.id} className="card">
            <h2>{room.name}</h2>
            <p className="muted">Вместимость: {room.capacity} чел.</p>
            {room.description && <p>{room.description}</p>}
            <Link to={`/rooms/${room.id}`} className="button-link">
              Расписание и бронь
            </Link>
          </li>
        ))}
      </ul>

      {(hasPrevious || hasNext) && (
        <div className="pagination">
          <button type="button" className="button-secondary" disabled={!hasPrevious} onClick={() => setOffset(offset - PAGE_SIZE)}>
            ← Назад
          </button>
          <span className="muted">
            {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} из {total}
          </span>
          <button type="button" className="button-secondary" disabled={!hasNext} onClick={() => setOffset(offset + PAGE_SIZE)}>
            Вперёд →
          </button>
        </div>
      )}
    </section>
  )
}
