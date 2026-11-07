import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { Logo } from './Sidebar'

// Login and registration: a centered card without the app navigation.
export function AuthLayout() {
  const { pathname } = useLocation()

  useEffect(() => {
    document.title = `${pathname === '/register' ? 'Регистрация' : 'Вход'} — RoomBooking`
  }, [pathname])

  return (
    <main className="auth">
      <Logo />
      <Outlet />
    </main>
  )
}
