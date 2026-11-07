import { NavLink, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

export function Header() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <NavLink to="/" className="logo">
        RoomBooking
      </NavLink>

      <nav className="nav" aria-label="Основная навигация">
        <NavLink to="/" end>
          Комнаты
        </NavLink>
        {user && <NavLink to="/bookings">Мои брони</NavLink>}
        {isAdmin && <NavLink to="/admin/rooms">Управление комнатами</NavLink>}
        {isAdmin && <NavLink to="/admin/users">Пользователи</NavLink>}
      </nav>

      <div className="header-user">
        {user ? (
          <>
            <span className="muted">
              {user.login}
              {isAdmin && ' (админ)'}
            </span>
            <button type="button" className="button-secondary" onClick={handleLogout}>
              Выйти
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Вход</NavLink>
            <NavLink to="/register">Регистрация</NavLink>
          </>
        )}
      </div>
    </header>
  )
}
