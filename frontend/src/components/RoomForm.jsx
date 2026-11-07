import { useState } from 'react'

import { ErrorMessage } from './ErrorMessage'

const EMPTY_ROOM = { name: '', capacity: 10, description: '' }

// Same limits as the backend schema: name 3-100, capacity 1-100, description up to 1000.
// capacity is kept as the input string, so the field can be cleared while typing.
function validate({ name, capacity, description }) {
  if (name.trim().length < 3 || name.trim().length > 100) {
    return 'Название — от 3 до 100 символов'
  }

  const capacityNumber = Number(capacity)

  if (capacity === '' || !Number.isInteger(capacityNumber) || capacityNumber < 1 || capacityNumber > 100) {
    return 'Вместимость — целое число от 1 до 100'
  }

  if (description.length > 1000) {
    return 'Описание — не длиннее 1000 символов'
  }

  return null
}

// onSubmit receives {name, capacity, description}; an empty description is sent as null.
export function RoomForm({ initialRoom = EMPTY_ROOM, submitLabel, onSubmit, onCancel }) {
  const [values, setValues] = useState({
    name: initialRoom.name,
    capacity: String(initialRoom.capacity),
    description: initialRoom.description ?? '',
  })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setValues((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const validationError = validate(values)
    setError(validationError)

    if (validationError) {
      return
    }

    setSubmitting(true)

    try {
      await onSubmit({
        name: values.name.trim(),
        capacity: Number(values.capacity),
        description: values.description.trim() || null,
      })
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form" noValidate>
      <div className="form-row">
        <label>
          Название
          <input name="name" value={values.name} onChange={updateField} required />
        </label>
        <label>
          Вместимость
          <input name="capacity" type="number" min={1} max={100} value={values.capacity} onChange={updateField} required />
        </label>
      </div>
      <label>
        Описание
        <textarea name="description" rows={2} value={values.description} onChange={updateField} />
      </label>

      <ErrorMessage error={error} />

      <div className="form-actions">
        <button type="submit" disabled={submitting}>
          {submitting ? 'Сохраняем…' : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="button-secondary" onClick={onCancel}>
            Отмена
          </button>
        )}
      </div>
    </form>
  )
}
