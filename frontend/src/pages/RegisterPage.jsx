import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { register } from '../api/auth'
import { Button } from '../components/Button'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../context/AuthContext'

const MIN_PASSWORD_LENGTH = 8
// Rough format check for a readable message; the backend validates the address fully.
const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

// Mirrors backend rules: login 3+ chars without "@", password 8+ chars.
function validate({ login, email, password, passwordRepeat }) {
  if (login.trim().length < 3) {
    return 'Логин — не короче 3 символов'
  }

  if (login.includes('@')) {
    return 'Логин не может содержать «@»'
  }

  if (!EMAIL_PATTERN.test(email.trim())) {
    return 'Введите корректный email'
  }

  if (password.length < MIN_PASSWORD_LENGTH) {
    return `Пароль — не короче ${MIN_PASSWORD_LENGTH} символов`
  }

  if (password !== passwordRepeat) {
    return 'Пароли не совпадают'
  }

  return null
}

export function RegisterPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ login: '', email: '', password: '', passwordRepeat: '' })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/" replace />
  }

  function updateField(event) {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const validationError = validate(form)
    setError(validationError)

    if (validationError) {
      return
    }

    setSubmitting(true)

    try {
      await register({ login: form.login.trim(), email: form.email.trim(), password: form.password })
      await login(form.login.trim(), form.password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card auth-card">
      <h1>Регистрация</h1>
      <p className="muted">Создайте аккаунт для бронирования комнат.</p>

      <form onSubmit={handleSubmit} className="form" noValidate>
        <label className="field">
          Логин
          <input className="input" name="login" value={form.login} onChange={updateField} required autoComplete="username" />
          <span className="field-hint">Не короче 3 символов, без «@»</span>
        </label>

        <label className="field">
          Email
          <input className="input" name="email" type="email" value={form.email} onChange={updateField} required autoComplete="email" />
        </label>

        <div className="form-row">
          <label className="field">
            Пароль
            <input className="input" name="password" type="password" value={form.password} onChange={updateField} required autoComplete="new-password" />
          </label>

          <label className="field">
            Повторите пароль
            <input className="input" name="passwordRepeat" type="password" value={form.passwordRepeat} onChange={updateField} required autoComplete="new-password" />
          </label>
        </div>
        <span className="field-hint small">Пароль — не короче 8 символов</span>

        <ErrorMessage error={error} />

        <Button type="submit" variant="primary" block loading={submitting}>
          Зарегистрироваться
        </Button>
      </form>

      <p className="auth-footer muted">
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </section>
  )
}
