import { Link } from 'react-router-dom'

function Register() {
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

        <form className="auth-form">
          <div className="form-field">
            <label htmlFor="name">Imię</label>
            <input
              id="name"
              name="name"
              type="text"
              autoComplete="given-name"
              placeholder="Twoje imię"
              required
            />
          </div>

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
              autoComplete="new-password"
              minLength={8}
              placeholder="Minimum 8 znaków"
              required
            />
          </div>

          <button className="button button-primary auth-submit" type="submit">
            Utwórz konto
          </button>
        </form>

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
