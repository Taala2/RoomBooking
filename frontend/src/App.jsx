import { SearchX } from 'lucide-react'
import { Link, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/AppLayout'
import { AuthLayout } from './components/AuthLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { EmptyState } from './components/States'
import { AdminRoomsPage } from './pages/admin/AdminRoomsPage'
import { AdminUsersPage } from './pages/admin/AdminUsersPage'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { MyBookingsPage } from './pages/MyBookingsPage'
import { RegisterPage } from './pages/RegisterPage'
import { RoomPage } from './pages/RoomPage'
import { RoomsPage } from './pages/RoomsPage'

function NotFoundPage() {
  return (
    <EmptyState
      icon={SearchX}
      title="Страница не найдена"
      text="Возможно, ссылка устарела."
      action={<Link to="/" className="button">На главную</Link>}
    />
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/rooms" element={<RoomsPage />} />
          <Route path="/rooms/:roomId" element={<RoomPage />} />
          <Route path="/bookings" element={<MyBookingsPage />} />

          <Route element={<ProtectedRoute adminOnly />}>
            <Route path="/admin/rooms" element={<AdminRoomsPage />} />
            <Route path="/admin/users" element={<AdminUsersPage />} />
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  )
}
