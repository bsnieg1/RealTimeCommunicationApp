import { useState, useEffect } from 'react'
import { login, register, getMe } from './api/auth'

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [me, setMe] = useState(null)
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!token) return
    getMe(token)
      .then(setMe)
      .catch((err) => {
        setError(err.message)
        setToken(null)
        localStorage.removeItem('token')
      })
  }, [token])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      if (mode === 'register') {
        await register(form.username, form.email, form.password)
        setMode('login')
        return
      }
      const { access_token } = await login(form.username, form.password)
      localStorage.setItem('token', access_token)
      setToken(access_token)
    } catch (err) {
      setError(err.message)
    }
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setMe(null)
  }

  if (token && me) {
    return (
      <div style={{ padding: 32, fontFamily: 'sans-serif' }}>
        <h1>Logged in</h1>
        <pre>{JSON.stringify(me, null, 2)}</pre>
        <button onClick={handleLogout}>Log out</button>
      </div>
    )
  }

  return (
    <div style={{ padding: 32, fontFamily: 'sans-serif', maxWidth: 320 }}>
      <h1>{mode === 'login' ? 'Log in' : 'Register'}</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <input
          placeholder={mode === 'login' ? 'username or email' : 'username'}
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        {mode === 'register' && (
          <input
            placeholder="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        )}
        <input
          type="password"
          placeholder="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <button type="submit">{mode === 'login' ? 'Log in' : 'Register'}</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'Need an account? Register' : 'Have an account? Log in'}
      </button>
    </div>
  )
}
