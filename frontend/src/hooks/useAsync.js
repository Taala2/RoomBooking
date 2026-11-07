import { useCallback, useEffect, useState } from 'react'

// Loads data with `load` (wrap it in useCallback) and loads again when it changes
// or when reload() is called.
// - Results are tied to the `load` that produced them: after the inputs change
//   (e.g. another day) old data is not shown while the new request is running.
// - A response that arrives after the inputs changed is ignored.
// - Errors thrown synchronously by `load` are reported like rejected promises.
export function useAsync(load) {
  const [result, setResult] = useState({ data: null, error: null, source: null })
  const [version, setVersion] = useState(0)
  const [reloading, setReloading] = useState(false)

  useEffect(() => {
    let current = true

    Promise.resolve()
      .then(load)
      .then(
        (data) => current && setResult({ data, error: null, source: load }),
        (error) => current && setResult({ data: null, error, source: load })
      )
      .finally(() => current && setReloading(false))

    return () => {
      current = false
    }
  }, [load, version])

  const reload = useCallback(() => {
    setReloading(true)
    setVersion((value) => value + 1)
  }, [])

  const fresh = result.source === load

  return {
    data: fresh ? result.data : null,
    error: fresh ? result.error : null,
    loading: !fresh || reloading,
    reload,
  }
}
