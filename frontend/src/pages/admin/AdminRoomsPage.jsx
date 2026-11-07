import { useCallback, useState } from 'react'
import { Building2, Pencil, Plus, Trash2 } from 'lucide-react'

import { createRoom, deleteRoom, listRooms, updateRoom } from '../../api/rooms'
import { Button } from '../../components/Button'
import { ErrorMessage, SuccessMessage } from '../../components/ErrorMessage'
import { RoomForm } from '../../components/RoomForm'
import { EmptyState, LoadingState } from '../../components/States'
import { useAsync } from '../../hooks/useAsync'

const ROOMS_LIMIT = 100
const COLUMNS = 4

function RoomRow({ room, onChanged, onMessage }) {
  const [editing, setEditing] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState(null)

  async function handleUpdate(values) {
    onMessage(null)
    await updateRoom(room.id, values)
    setEditing(false)
    onMessage(`Комната «${values.name}» сохранена`)
    onChanged()
  }

  async function handleDelete() {
    if (!window.confirm(`Удалить комнату «${room.name}»? Прошедшие брони этой комнаты тоже удалятся.`)) {
      return
    }

    setError(null)
    onMessage(null)
    setDeleting(true)

    try {
      await deleteRoom(room.id)
      onMessage(`Комната «${room.name}» удалена`)
      onChanged()
    } catch (err) {
      setError(err)
      setDeleting(false)
    }
  }

  if (editing) {
    return (
      <tr className="admin-edit-row">
        <td colSpan={COLUMNS}>
          <RoomForm initialRoom={room} submitLabel="Сохранить" onSubmit={handleUpdate} onCancel={() => setEditing(false)} />
        </td>
      </tr>
    )
  }

  return (
    <tr>
      <td>
        <strong>{room.name}</strong>
        {error && <ErrorMessage error={error} />}
      </td>
      <td>{room.capacity}</td>
      <td className="cell-secondary">{room.description || '—'}</td>
      <td className="cell-actions">
        <div className="actions">
          <Button size="sm" variant="ghost" iconOnly icon={Pencil} onClick={() => setEditing(true)} title="Изменить">
            Изменить {room.name}
          </Button>
          <Button size="sm" variant="ghost" iconOnly icon={Trash2} loading={deleting} onClick={handleDelete} title="Удалить">
            Удалить {room.name}
          </Button>
        </div>
      </td>
    </tr>
  )
}

export function AdminRoomsPage() {
  const load = useCallback(() => listRooms({ limit: ROOMS_LIMIT }), [])
  const { data, error, loading, reload } = useAsync(load)
  const [message, setMessage] = useState(null)
  const [creating, setCreating] = useState(false)

  async function handleCreate(values) {
    setMessage(null)
    const room = await createRoom(values)
    setMessage(`Комната «${room.name}» создана`)
    setCreating(false)
    reload()
  }

  return (
    <div className="page">
      <div className="page-intro">
        <p className="muted">Комнаты, доступные для бронирования. Удалить можно только комнату без предстоящих броней.</p>
        {!creating && (
          <Button variant="primary" icon={Plus} onClick={() => setCreating(true)}>
            Новая комната
          </Button>
        )}
      </div>

      {creating && (
        <section className="card">
          <h2 className="card-header">Новая комната</h2>
          <RoomForm submitLabel="Создать" onSubmit={handleCreate} onCancel={() => setCreating(false)} />
        </section>
      )}

      <SuccessMessage>{message}</SuccessMessage>
      <ErrorMessage error={error} />
      {loading && !data && <LoadingState />}

      {data && data.items.length === 0 && (
        <div className="card">
          <EmptyState icon={Building2} title="Комнат пока нет" text="Создайте первую комнату." />
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="card card-flush table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Название</th>
                <th scope="col">Мест</th>
                <th scope="col">Описание</th>
                <th scope="col">
                  <span className="visually-hidden">Действия</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((room) => (
                <RoomRow key={room.id} room={room} onChanged={reload} onMessage={setMessage} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total > data.items.length && (
        <p className="muted small">
          Показаны первые {data.items.length} из {data.total}.
        </p>
      )}
    </div>
  )
}
