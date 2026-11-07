import { request } from './client'

export function listRooms({ limit = 20, offset = 0 } = {}) {
  return request('/rooms/list', { query: { limit, offset } })
}

export function getRoom(roomId) {
  return request(`/rooms/${roomId}`)
}

// start/end: ISO strings with timezone; the backend allows up to 7 days.
export function getBusySlots(roomId, start, end) {
  return request(`/rooms/${roomId}/bookings`, { query: { start, end } })
}

export function createRoom({ name, capacity, description }) {
  return request('/rooms/create', {
    method: 'POST',
    body: { name, capacity, description },
  })
}

// changes: only the fields that should change; description: null clears it.
export function updateRoom(roomId, changes) {
  return request(`/rooms/change/${roomId}`, { method: 'PATCH', body: changes })
}

export function deleteRoom(roomId) {
  return request(`/rooms/delete/${roomId}`, { method: 'DELETE' })
}
