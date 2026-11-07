import { useState } from 'react'

import { intervalFromInputs, validateInterval } from '../utils/dates'
import { Button } from './Button'
import { ErrorMessage } from './ErrorMessage'

// Date + start/end time form used for creating and moving bookings.
// onSubmit(start: Date, end: Date) may throw an ApiError, which is shown under the form.
// inline: one row (moving a booking); otherwise stacked with a full-width main button.
export function TimeRangeForm({
  initialDate,
  initialStart = '10:00',
  initialEnd = '11:00',
  submitLabel,
  onSubmit,
  onCancel,
  showDate = true,
  inline = false,
}) {
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
    const { start, end } = intervalFromInputs(date, values.start, values.end)
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

  const fields = (
    <>
      {showDate && (
        <label className="field">
          Дата
          <input className="input" name="date" type="date" value={values.date} onChange={updateField} required />
        </label>
      )}
      <label className="field">
        Начало
        <input className="input" name="start" type="time" value={values.start} onChange={updateField} required />
      </label>
      <label className="field">
        Конец
        <input className="input" name="end" type="time" value={values.end} onChange={updateField} required />
      </label>
    </>
  )

  return (
    <form onSubmit={handleSubmit} className={inline ? 'form-inline' : 'form'} noValidate>
      {inline ? fields : <div className="form-row">{fields}</div>}

      <div className="actions">
        <Button type="submit" variant="primary" block={!inline} loading={submitting}>
          {submitLabel}
        </Button>
        {onCancel && (
          <Button variant="ghost" onClick={onCancel}>
            Отмена
          </Button>
        )}
      </div>

      <ErrorMessage error={error} />
    </form>
  )
}
