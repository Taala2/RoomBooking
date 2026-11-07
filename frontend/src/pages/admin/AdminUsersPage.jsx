import { useCallback, useState } from 'react'

import { changeRole, listUsers } from '../../api/users'
import { ErrorMessage, SuccessMessage } from '../../components/ErrorMessage'
import { useAuth } from '../../context/AuthContext'
import { useAsync } from '../../hooks/useAsync'

const ROLE_LABELS = { user: 'Пользователь', admin: 'Администратор' }

export function AdminUsersPage() {
  const { user: currentUser } = useAuth()
  const load = useCallback(() => listUsers(), [])
  const { data, error, loading, reload } = useAsync(load)
  const [actionError, setActionError] = useState(null)
  const [message, setMessage] = useState(null)

  async function handleRoleChange(user, role) {
    setActionError(null)
    setMessage(null)

    try {
      await changeRole(user.id, role)
      setMessage(`${user.login}: роль изменена на «${ROLE_LABELS[role]}»`)
      await reload()
    } catch (err) {
      setActionError(err)
    }
  }

  return (
    <section>
      <h1>Пользователи</h1>

      <ErrorMessage error={error ?? actionError} />
      <SuccessMessage>{message}</SuccessMessage>
      {loading && !data && <p className="muted">Загрузка…</p>}

      {data && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Логин</th>
                <th scope="col">Email</th>
                <th scope="col">Роль</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((user) => (
                <tr key={user.id}>
                  <td>{user.login}</td>
                  <td>{user.email}</td>
                  <td>
                    {/* The backend forbids admins to change their own role, so the control is disabled. */}
                    <select
                      aria-label={`Роль пользователя ${user.login}`}
                      value={user.role}
                      disabled={user.id === currentUser.id}
                      onChange={(event) => handleRoleChange(user, event.target.value)}
                    >
                      {Object.entries(ROLE_LABELS).map(([role, label]) => (
                        <option key={role} value={role}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.total > data.items.length && (
            <p className="muted">
              Показаны первые {data.items.length} из {data.total}.
            </p>
          )}
        </div>
      )}
    </section>
  )
}
