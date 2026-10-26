import { Link } from 'react-router-dom'

function Login() {
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

        <form className="auth-form">
          <div className="form-field">
            <label htmlFor="email">Adres e-mail</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="twoj@email.pl"
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
              required
            />
          </div>

          <button className="button button-primary auth-submit" type="submit">
            Zaloguj się
          </button>
        </form>

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
