import { Building2, CalendarCheck, CalendarClock, DoorOpen, LayoutDashboard, Users, X } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { Button } from './Button'

const MAIN_LINKS = [
  { to: '/', label: 'Главная', icon: LayoutDashboard, end: true },
  { to: '/rooms', label: 'Комнаты', icon: DoorOpen },
  { to: '/bookings', label: 'Мои брони', icon: CalendarCheck },
]

const ADMIN_LINKS = [
  { to: '/admin/rooms', label: 'Управление комнатами', icon: Building2 },
  { to: '/admin/users', label: 'Пользователи', icon: Users },
]

function NavItem({ link, onNavigate }) {
  const Icon = link.icon

  return (
    <NavLink to={link.to} end={link.end} className="nav-link" onClick={onNavigate}>
      <Icon size={18} aria-hidden="true" />
      {link.label}
    </NavLink>
  )
}

export function Logo({ onClick }) {
  return (
    <NavLink to="/" className="logo" onClick={onClick}>
      <span className="logo-mark" aria-hidden="true">
        <CalendarClock size={17} />
      </span>
      RoomBooking
    </NavLink>
  )
}

// On small screens the sidebar is a drawer: `open` shows it, onClose hides it.
export function Sidebar({ open, onClose }) {
  const { isAdmin } = useAuth()

  return (
    <aside id="sidebar" className={`sidebar${open ? ' open' : ''}`}>
      <div className="sidebar-top">
        <Logo onClick={onClose} />
        <Button variant="ghost" iconOnly icon={X} className="sidebar-close" onClick={onClose}>
          Закрыть меню
        </Button>
      </div>

      <nav className="nav-section" aria-label="Основная навигация">
        {MAIN_LINKS.map((link) => (
          <NavItem key={link.to} link={link} onNavigate={onClose} />
        ))}
      </nav>

      {isAdmin && (
        <nav className="nav-section" aria-label="Администрирование">
          <p className="nav-section-title">Администрирование</p>
          {ADMIN_LINKS.map((link) => (
            <NavItem key={link.to} link={link} onNavigate={onClose} />
          ))}
        </nav>
      )}
    </aside>
  )
}
