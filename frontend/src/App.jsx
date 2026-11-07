import { Link, Route, Routes } from 'react-router-dom'

import { ErrorBoundary } from './components/ErrorBoundary'
import { Header } from './components/Header'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AdminRoomsPage } from './pages/admin/AdminRoomsPage'
import { AdminUsersPage } from './pages/admin/AdminUsersPage'
import { LoginPage } from './pages/LoginPage'
import { MyBookingsPage } from './pages/MyBookingsPage'
import { RegisterPage } from './pages/RegisterPage'
import { RoomPage } from './pages/RoomPage'
import { RoomsPage } from './pages/RoomsPage'

function NotFoundPage() {
  return (
    <section>
      <h1>Страница не найдена</h1>
      <Link to="/">На главную</Link>
    </section>
  )
}

export default function App() {
  return (
    <>
      <Header />
      <main className="container">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<RoomsPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/rooms/:roomId" element={<RoomPage />} />
              <Route path="/bookings" element={<MyBookingsPage />} />
            </Route>

            <Route element={<ProtectedRoute adminOnly />}>
              <Route path="/admin/rooms" element={<AdminRoomsPage />} />
              <Route path="/admin/users" element={<AdminUsersPage />} />
            </Route>

            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </>
  )
}
