import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

import { Button } from '../components/Button'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ loginOrEmail: '', password: '' })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const redirectTo = location.state?.from ?? '/'

  if (user) {
    return <Navigate to={redirectTo} replace />
  }

  function updateField(event) {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      await login(form.loginOrEmail.trim(), form.password)
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card auth-card">
      <h1>Вход</h1>
      <p className="muted">Войдите, чтобы бронировать комнаты.</p>

      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          Логин или email
          <input className="input" name="loginOrEmail" value={form.loginOrEmail} onChange={updateField} required minLength={3} autoComplete="username" />
        </label>

        <label className="field">
          Пароль
          <input className="input" name="password" type="password" value={form.password} onChange={updateField} required autoComplete="current-password" />
        </label>

        <ErrorMessage error={error} />

        <Button type="submit" variant="primary" block loading={submitting}>
          Войти
        </Button>
      </form>

      <p className="auth-footer muted">
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </section>
  )
}
