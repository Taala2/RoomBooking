import { useCallback, useEffect, useState } from 'react'

// Loads data with `load` (wrap it in useCallback) and loads again when it changes
// or when reload() is called. A response that arrives after the inputs changed is ignored.
export function useAsync(load) {
  const [state, setState] = useState({ data: null, error: null, loading: true })
  const [version, setVersion] = useState(0)

  useEffect(() => {
    let current = true

    load().then(
      (data) => current && setState({ data, error: null, loading: false }),
      (error) => current && setState((previous) => ({ ...previous, error, loading: false }))
    )

    return () => {
      current = false
    }
  }, [load, version])

  const reload = useCallback(() => {
    setState((previous) => ({ ...previous, loading: true }))
    setVersion((value) => value + 1)
  }, [])

  return { ...state, reload }
}
