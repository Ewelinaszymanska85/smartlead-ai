import { useState } from 'react'
import { Link } from 'react-router-dom'

function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleRegister(event) {
    event.preventDefault()
    setMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/register', {
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
            : 'Nie udało się utworzyć konta.'
        )
      }

      setMessage('Konto zostało utworzone. Możesz się zalogować.')
      setUsername('')
      setPassword('')
    } catch (error) {
      setMessage(
        error.message || 'Nie udało się połączyć z serwerem.'
      )
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

        <h1>Utwórz konto</h1>

        <p className="auth-description">
          Załóż konto i zacznij zarządzać potencjalnymi klientami.
        </p>

        <form className="auth-form" onSubmit={handleRegister}>
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
              autoComplete="new-password"
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
            {isLoading ? 'Tworzenie konta...' : 'Utwórz konto'}
          </button>
        </form>

        {message && (
          <p role="status" aria-live="polite">
            {message}
          </p>
        )}

        <p className="auth-switch">
          Masz już konto? <Link to="/login">Zaloguj się</Link>
        </p>

        <Link to="/" className="auth-back">
          ← Powrót na stronę główną
        </Link>
      </section>
    </main>
  )
}

export default Register