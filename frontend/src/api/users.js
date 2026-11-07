import { request } from './client'

export function listUsers({ limit = 100, offset = 0 } = {}) {
  return request('/users/list', { query: { limit, offset } })
}

export function changeRole(userId, role) {
  return request(`/users/${encodeURIComponent(userId)}/role`, {
    method: 'PATCH',
    body: { role },
  })
}
