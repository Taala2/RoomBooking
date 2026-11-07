import { useCallback, useState } from 'react'

import { changeRole, listUsers } from '../../api/users'
import { ErrorMessage, SuccessMessage } from '../../components/ErrorMessage'
import { LoadingState } from '../../components/States'
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
    <div className="page">
      <p className="muted">Администраторы могут управлять комнатами и ролями. Свою роль изменить нельзя.</p>

      <ErrorMessage error={error ?? actionError} />
      <SuccessMessage>{message}</SuccessMessage>
      {loading && !data && <LoadingState />}

      {data && (
        <div className="card card-flush table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Пользователь</th>
                <th scope="col">Email</th>
                <th scope="col">Роль</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((user) => (
                <tr key={user.id}>
                  <td>
                    <span className="person">
                      <span className="avatar" aria-hidden="true">
                        {user.login.slice(0, 1)}
                      </span>
                      <span>
                        {user.login}
                        {user.id === currentUser.id && <span className="muted small"> (вы)</span>}
                      </span>
                    </span>
                  </td>
                  <td className="cell-secondary">{user.email}</td>
                  <td>
                    {/* The backend forbids admins to change their own role, so the control is disabled. */}
                    <select
                      className="input role-select"
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
