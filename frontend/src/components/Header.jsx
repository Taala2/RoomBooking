import { useEffect } from 'react'
import { LogOut, Menu } from 'lucide-react'
import { matchPath, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { Button } from './Button'

const PAGE_TITLES = [
  ['/', 'Главная'],
  ['/rooms', 'Комнаты'],
  ['/rooms/:roomId', 'Бронирование'],
  ['/bookings', 'Мои брони'],
  ['/admin/rooms', 'Управление комнатами'],
  ['/admin/users', 'Пользователи'],
]

function pageTitle(pathname) {
  const found = PAGE_TITLES.find(([pattern]) => matchPath(pattern, pathname))
  return found ? found[1] : 'Страница не найдена'
}

export function Header({ menuOpen, onMenuClick }) {
  const { user, isAdmin, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const title = pageTitle(location.pathname)

  useEffect(() => {
    document.title = `${title} — RoomBooking`
  }, [title])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <Button
        variant="ghost"
        iconOnly
        icon={Menu}
        className="header-menu"
        onClick={onMenuClick}
        aria-expanded={menuOpen}
        aria-controls="sidebar"
      >
        Открыть меню
      </Button>

      <h1>{title}</h1>

      <div className="header-user">
        <span className="avatar" aria-hidden="true">
          {user.login.slice(0, 1)}
        </span>
        <div className="header-user-name">
          <span>{user.login}</span>
          <span>{isAdmin ? 'Администратор' : 'Пользователь'}</span>
        </div>
        <Button variant="ghost" iconOnly icon={LogOut} onClick={handleLogout} title="Выйти">
          Выйти
        </Button>
      </div>
    </header>
  )
}
