// Shows an API/validation error; role="alert" makes screen readers announce it.
export function ErrorMessage({ error }) {
  if (!error) {
    return null
  }

  const text = typeof error === 'string' ? error : error.message

  return (
    <p className="message message-error" role="alert">
      {text}
    </p>
  )
}

export function SuccessMessage({ children }) {
  if (!children) {
    return null
  }

  return (
    <p className="message message-success" role="status">
      {children}
    </p>
  )
}
