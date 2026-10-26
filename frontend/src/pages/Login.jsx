import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Login() {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleLogin(event) {
    event.preventDefault()
    setMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Nie udało się zalogować.'
        )
      }

      if (!data.access_token) {
  throw new Error('Serwer nie zwrócił tokenu logowania.')
}

localStorage.setItem('access_token', data.access_token)
localStorage.setItem('username', data.username)

setMessage('Logowanie zakończone pomyślnie!')

navigate('/dashboard')
    } catch (error) {
      setMessage(error.message || 'Nie udało się połączyć z serwerem.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <Link to="/" className="brand auth-brand">
          <span className="brand-icon">S</span>
          <span>
            SmartLead<span className="brand-accent"> AI</span>
          </span>
        </Link>

        <h1>Witaj ponownie!</h1>

        <p className="auth-description">
          Zaloguj się, aby przejść do swojego panelu.
        </p>

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-field">
            <label htmlFor="username">Nazwa użytkownika</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              placeholder="Wpisz nazwę użytkownika"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">Hasło</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="Wpisz hasło"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button
            className="button button-primary auth-submit"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
        </form>

        {message && (
          <p role="status" aria-live="polite">
            {message}
          </p>
        )}

        <p className="auth-switch">
          Nie masz jeszcze konta? <Link to="/register">Utwórz konto</Link>
        </p>

        <Link to="/" className="auth-back">
          ← Powrót na stronę główną
        </Link>
      </section>
    </main>
  )
}

export default Login
