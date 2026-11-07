import { request } from './client'
import { listRooms } from './rooms'

const ROOMS_LIMIT = 100

export function listMyBookings() {
  return request('/bookings/')
}

// Bookings only carry room_id, so room names come from the room list.
export async function listMyBookingsWithRooms() {
  const [bookings, rooms] = await Promise.all([listMyBookings(), listRooms({ limit: ROOMS_LIMIT })])
  const roomNames = Object.fromEntries(rooms.items.map((room) => [room.id, room.name]))

  return { bookings, roomNames, roomsTotal: rooms.total }
}

export function createBooking(roomId, startTime, endTime) {
  return request('/bookings/', {
    method: 'POST',
    body: { room_id: roomId, start_time: startTime, end_time: endTime },
  })
}

export function cancelBooking(bookingId) {
  return request('/bookings/cancel', {
    method: 'POST',
    body: { booking_id: bookingId },
  })
}

export function changeBooking(bookingId, startTime, endTime) {
  return request('/bookings/change', {
    method: 'POST',
    body: { booking_id: bookingId, start_time: startTime, end_time: endTime },
  })
}
