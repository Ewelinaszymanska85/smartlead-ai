function Login() {
  return (
    <main>
      <h1>Logowanie do SmartLead AI</h1>
      <p>Zaloguj się, aby przejść do swojego panelu.</p>

      <form>
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
            autoComplete="current-password"
            placeholder="Wpisz hasło"
            required
          />
        </div>

        <button type="submit">Zaloguj się</button>
      </form>
    </main>
  )
}

export default Login