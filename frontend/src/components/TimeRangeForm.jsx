import { useState } from 'react'

import { fromInputs, validateInterval } from '../utils/dates'
import { ErrorMessage } from './ErrorMessage'

// Date + start/end time form used for creating and moving bookings.
// onSubmit(start: Date, end: Date) may throw an ApiError, which is shown under the form.
export function TimeRangeForm({ initialDate, initialStart = '10:00', initialEnd = '11:00', submitLabel, onSubmit, onCancel, showDate = true }) {
  const [values, setValues] = useState({ date: initialDate, start: initialStart, end: initialEnd })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const date = showDate ? values.date : initialDate

  function updateField(event) {
    const { name, value } = event.target
    setValues((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const start = fromInputs(date, values.start)
    const end = fromInputs(date, values.end)
    const validationError = validateInterval(start, end)
    setError(validationError)

    if (validationError) {
      return
    }

    setSubmitting(true)

    try {
      await onSubmit(start, end)
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form form-inline" noValidate>
      {showDate && (
        <label>
          Дата
          <input name="date" type="date" value={values.date} onChange={updateField} required />
        </label>
      )}
      <label>
        Начало
        <input name="start" type="time" value={values.start} onChange={updateField} required />
      </label>
      <label>
        Конец
        <input name="end" type="time" value={values.end} onChange={updateField} required />
      </label>

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

      <ErrorMessage error={error} />
    </form>
  )
}
