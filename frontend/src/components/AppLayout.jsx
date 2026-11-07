import { useCallback, useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { ErrorBoundary } from './ErrorBoundary'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

// Sidebar + header + content for signed-in pages. On small screens the sidebar is a drawer.
export function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()
  const closeMenu = useCallback(() => setMenuOpen(false), [])

  useEffect(() => {
    if (!menuOpen) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        closeMenu()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [menuOpen, closeMenu])

  return (
    <div className="app">
      <Sidebar open={menuOpen} onClose={closeMenu} />
      {menuOpen && <div className="backdrop" onClick={closeMenu} aria-hidden="true" />}

      <div className="app-main">
        <Header menuOpen={menuOpen} onMenuClick={() => setMenuOpen(true)} />
        <main className="content">
          {/* key: navigating away from a broken page resets the boundary */}
          <ErrorBoundary key={location.pathname}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
