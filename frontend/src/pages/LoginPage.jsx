import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

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
    <section className="card narrow">
      <h1>Вход</h1>

      <form onSubmit={handleSubmit} className="form">
        <label>
          Логин или email
          <input name="loginOrEmail" value={form.loginOrEmail} onChange={updateField} required minLength={3} autoComplete="username" />
        </label>

        <label>
          Пароль
          <input name="password" type="password" value={form.password} onChange={updateField} required autoComplete="current-password" />
        </label>

        <ErrorMessage error={error} />

        <button type="submit" disabled={submitting}>
          {submitting ? 'Входим…' : 'Войти'}
        </button>
      </form>

      <p className="muted">
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </section>
  )
}
