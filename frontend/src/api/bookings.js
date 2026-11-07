import { request } from './client'

export function listMyBookings() {
  return request('/bookings/')
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
