import { request } from './client'

export function register({ login, email, password }) {
  return request('/users/auth/register', {
    method: 'POST',
    body: { login, email, password },
  })
}

export function login(loginOrEmail, password) {
  return request('/users/auth/login', {
    method: 'POST',
    body: { login_or_email: loginOrEmail, password },
  })
}

export function getMe() {
  return request('/users/me')
}
