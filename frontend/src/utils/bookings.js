// Display state of a booking: active bookings that already ended count as "past".
export function bookingState(booking, now = new Date()) {
  if (booking.status === 'canceled') {
    return 'canceled'
  }

  return new Date(booking.end_time) > now ? 'active' : 'past'
}

export function isUpcoming(booking) {
  return bookingState(booking) === 'active'
}
