import api from './index'

export function login(email, password) {
  return api.post('/auth/login', {
    email,
    password
  })
}

export function register(userData) {
  return api.post('/auth/register', userData)
}

export function getUserInfo() {
  return api.get('/auth/me')
}
