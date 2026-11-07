import { useCallback, useState } from 'react'

import { createRoom, deleteRoom, listRooms, updateRoom } from '../../api/rooms'
import { ErrorMessage, SuccessMessage } from '../../components/ErrorMessage'
import { RoomForm } from '../../components/RoomForm'
import { useAsync } from '../../hooks/useAsync'

const ROOMS_LIMIT = 100

function AdminRoomItem({ room, onChanged, onMessage }) {
  const [editing, setEditing] = useState(false)
  const [error, setError] = useState(null)

  async function handleUpdate(values) {
    onMessage(null)
    await updateRoom(room.id, values)
    setEditing(false)
    onMessage(`Комната «${values.name}» сохранена`)
    await onChanged()
  }

  async function handleDelete() {
    if (!window.confirm(`Удалить комнату «${room.name}»? Прошедшие брони этой комнаты тоже удалятся.`)) {
      return
    }

    setError(null)
    onMessage(null)

    try {
      await deleteRoom(room.id)
      onMessage(`Комната «${room.name}» удалена`)
      await onChanged()
    } catch (err) {
      setError(err)
    }
  }

  if (editing) {
    return (
      <li className="card">
        <RoomForm initialRoom={room} submitLabel="Сохранить" onSubmit={handleUpdate} onCancel={() => setEditing(false)} />
      </li>
    )
  }

  return (
    <li className="card admin-row">
      <div>
        <strong>{room.name}</strong>
        <span className="muted"> · {room.capacity} чел.</span>
        {room.description && <p className="muted">{room.description}</p>}
      </div>
      <div className="form-actions">
        <button type="button" className="button-secondary" onClick={() => setEditing(true)}>
          Изменить
        </button>
        <button type="button" className="button-danger" onClick={handleDelete}>
          Удалить
        </button>
      </div>
      <ErrorMessage error={error} />
    </li>
  )
}

export function AdminRoomsPage() {
  const load = useCallback(() => listRooms({ limit: ROOMS_LIMIT }), [])
  const { data, error, loading, reload } = useAsync(load)
  const [message, setMessage] = useState(null)
  // Changing the key remounts the create form, clearing it after success.
  const [createFormKey, setCreateFormKey] = useState(0)

  async function handleCreate(values) {
    setMessage(null)
    const room = await createRoom(values)
    setMessage(`Комната «${room.name}» создана`)
    setCreateFormKey((key) => key + 1)
    await reload()
  }

  return (
    <section>
      <h1>Управление комнатами</h1>

      <div className="card">
        <h2>Новая комната</h2>
        <RoomForm key={createFormKey} submitLabel="Создать" onSubmit={handleCreate} />
      </div>

      <SuccessMessage>{message}</SuccessMessage>
      <ErrorMessage error={error} />
      {loading && !data && <p className="muted">Загрузка…</p>}

      <ul className="admin-list">
        {data?.items.map((room) => (
          <AdminRoomItem key={room.id} room={room} onChanged={reload} onMessage={setMessage} />
        ))}
      </ul>
      {data && data.total > data.items.length && (
        <p className="muted">
          Показаны первые {data.items.length} из {data.total}.
        </p>
      )}
    </section>
  )
}
