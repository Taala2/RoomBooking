import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { register } from '../api/auth'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../context/AuthContext'

const MIN_PASSWORD_LENGTH = 8

// Mirrors backend rules: login 3+ chars without "@", password 8+ chars.
function validate({ login, password, passwordRepeat }) {
  if (login.trim().length < 3) {
    return 'Логин — не короче 3 символов'
  }

  if (login.includes('@')) {
    return 'Логин не может содержать «@»'
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
    <section className="card narrow">
      <h1>Регистрация</h1>

      <form onSubmit={handleSubmit} className="form" noValidate>
        <label>
          Логин
          <input name="login" value={form.login} onChange={updateField} required autoComplete="username" />
        </label>

        <label>
          Email
          <input name="email" type="email" value={form.email} onChange={updateField} required autoComplete="email" />
        </label>

        <label>
          Пароль
          <input name="password" type="password" value={form.password} onChange={updateField} required autoComplete="new-password" />
        </label>

        <label>
          Повторите пароль
          <input name="passwordRepeat" type="password" value={form.passwordRepeat} onChange={updateField} required autoComplete="new-password" />
        </label>

        <ErrorMessage error={error} />

        <button type="submit" disabled={submitting}>
          {submitting ? 'Создаём аккаунт…' : 'Зарегистрироваться'}
        </button>
      </form>

      <p className="muted">
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </section>
  )
}
