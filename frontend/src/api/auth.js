import { apiFetch } from './client'

export function register(username, email, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

export function login(identifier, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  })
}

export function getMe(token) {
  return apiFetch('/me', { headers: { Authorization: `Bearer ${token}` } })
}
