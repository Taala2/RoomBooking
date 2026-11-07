import { Component } from 'react'

// Catches render errors so one broken page does not blank the whole app.
export class ErrorBoundary extends Component {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('Render error:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card">
          <h2>Что-то пошло не так</h2>
          <p className="muted">Обновите страницу. Если ошибка повторяется — сообщите администратору.</p>
          <button type="button" onClick={() => window.location.reload()}>
            Обновить
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
