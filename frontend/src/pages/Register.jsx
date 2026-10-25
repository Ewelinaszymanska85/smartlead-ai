function Register() {
  return (
    <main>
      <h1>Utwórz konto SmartLead AI</h1>
      <p>Zarejestruj się, aby rozpocząć pracę z potencjalnymi klientami.</p>

      <form>
        <div>
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

        <div>
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

        <div>
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

        <button type="submit">Utwórz konto</button>
      </form>
    </main>
  )
}

export default Register