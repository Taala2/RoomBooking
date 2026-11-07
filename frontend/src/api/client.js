const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'roombooking_token'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

// localStorage can throw (private mode, blocked storage): the app then works until reload.
export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // ignore: token stays only in memory for this page
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // ignore
  }
}

let handleUnauthorized = () => {}

// AuthContext registers logout here, so an expired token signs the user out everywhere.
export function setUnauthorizedHandler(handler) {
  handleUnauthorized = handler
}

function errorMessage(body, status) {
  if (typeof body?.detail === 'string') {
    return body.detail
  }

  // FastAPI validation errors (422) come as a list of {msg, loc}.
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg).join('; ')
  }

  return `Ошибка сервера (${status})`
}

function buildUrl(path, query) {
  const url = new URL(path, API_URL)

  Object.entries(query ?? {}).forEach(([key, value]) => {
    url.searchParams.set(key, value)
  })

  return url
}

export async function request(path, { method = 'GET', body, query } = {}) {
  const token = getToken()
  const headers = {}

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  let response

  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'Сервер недоступен. Проверьте, что backend запущен.')
  }

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    if (response.status === 401 && token) {
      handleUnauthorized()
    }

    throw new ApiError(response.status, errorMessage(data, response.status))
  }

  return data
}
