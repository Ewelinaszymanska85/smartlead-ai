import './App.css'

function App() {
  return (
    <div className="app">
      <header className="navbar">
        <a href="#home" className="brand">
          <span className="brand-icon">S</span>
          <span>SmartLead<span className="brand-accent"> AI</span></span>
        </a>

        <nav className="nav-links">
          <a href="#features">Możliwości</a>
          <a href="#how-it-works">Jak to działa?</a>
          <a href="#about">O projekcie</a>
        </nav>

        <div className="nav-actions">
          <button className="button button-login" type="button">
            Zaloguj się
          </button>
          <button className="button button-primary" type="button">
            Rozpocznij
            <span aria-hidden="true"> →</span>
          </button>
        </div>
      </header>

      <main>
        <section className="hero-section" id="home">
          <div className="hero-content">
            <div className="eyebrow">
              <span className="status-dot"></span>
              INTELIGENTNE ZARZĄDZANIE SPRZEDAŻĄ
            </div>

            <h1>
              Zamieniaj zapytania
              <br />
              klientów w <span>nowe możliwości.</span>
            </h1>

            <p className="hero-description">
              Zarządzaj potencjalnymi klientami w jednym miejscu.
              Porządkuj zapytania, kontroluj priorytety i usprawniaj
              codzienną pracę swojego zespołu sprzedaży.
            </p>

            <div className="hero-actions">
              <button className="button button-primary button-large" type="button">
                Poznaj SmartLead AI
                <span aria-hidden="true"> →</span>
              </button>

              <a href="#features" className="secondary-link">
                Odkryj możliwości
              </a>
            </div>

            <div className="hero-benefits">
              <div>
                <span className="benefit-check">✓</span>
                Przejrzysta baza klientów
              </div>
              <div>
                <span className="benefit-check">✓</span>
                Kontrola priorytetów
              </div>
            </div>
          </div>

          <div className="dashboard-preview">
            <div className="preview-glow"></div>

            <div className="preview-window">
              <div className="preview-header">
                <div className="preview-brand">
                  <span className="mini-brand-icon">S</span>
                  <span>SmartLead AI</span>
                </div>

                <div className="preview-user">
                  <span className="online-dot"></span>
                  Panel sprzedaży
                </div>
              </div>

              <div className="preview-body">
                <div className="preview-sidebar">
                  <div className="sidebar-item active">
                    <span>▦</span> Dashboard
                  </div>
                  <div className="sidebar-item">
                    <span>♙</span> Klienci
                  </div>
                  <div className="sidebar-item">
                    <span>◷</span> Historia
                  </div>
                  <div className="sidebar-item">
                    <span>⚙</span> Ustawienia
                  </div>
                </div>

                <div className="preview-main">
                  <div className="preview-welcome">
                    <div>
                      <span className="preview-overline">PANEL GŁÓWNY</span>
                      <h2>Witaj w swoim CRM</h2>
                      <p>Przegląd potencjalnych klientów</p>
                    </div>

                    <span className="preview-date">Ten miesiąc</span>
                  </div>

                  <div className="stat-grid">
                    <div className="stat-card">
                      <span>Wszyscy klienci</span>
                      <strong>128</strong>
                      <small className="stat-positive">Baza kontaktów</small>
                    </div>

                    <div className="stat-card">
                      <span>Wysoki priorytet</span>
                      <strong>12</strong>
                      <small className="stat-warning">Wymagają uwagi</small>
                    </div>
                  </div>

                  <div className="preview-list">
                    <div className="list-heading">
                      <strong>Ostatnie zapytania</strong>
                      <span>Podgląd</span>
                    </div>

                    <div className="lead-row">
                      <div className="lead-avatar avatar-purple">AK</div>
                      <div className="lead-info">
                        <strong>Anna Kowalska</strong>
                        <span>Strona internetowa</span>
                      </div>
                      <span className="priority priority-high">Wysoki</span>
                    </div>

                    <div className="lead-row">
                      <div className="lead-avatar avatar-blue">PN</div>
                      <div className="lead-info">
                        <strong>Piotr Nowak</strong>
                        <span>Sklep internetowy</span>
                      </div>
                      <span className="priority priority-normal">Normalny</span>
                    </div>

                    <div className="lead-row">
                      <div className="lead-avatar avatar-green">MW</div>
                      <div className="lead-info">
                        <strong>Marta Wiśniewska</strong>
                        <span>Aplikacja mobilna</span>
                      </div>
                      <span className="priority priority-normal">Normalny</span>
                    </div>
                  </div>

                  <div className="ai-notice">
                    <span className="ai-icon">✦</span>
                    <div>
                      <strong>Asystent SmartLead</strong>
                      <p>Wspieraj analizę zapytań i organizację pracy.</p>
                    </div>
                    <span className="ai-arrow">→</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="floating-badge">
              <span className="floating-icon">✦</span>
              <div>
                <strong>Wszystko pod kontrolą</strong>
                <span>Klienci i priorytety w jednym miejscu</span>
              </div>
            </div>
          </div>
        </section>

        <section className="features-section" id="features">
          <div className="section-heading">
            <span className="section-label">TWOJE CENTRUM SPRZEDAŻY</span>
            <h2>Więcej porządku. Więcej możliwości.</h2>
            <p>
              Wszystkie najważniejsze informacje o klientach w jednym,
              uporządkowanym miejscu.
            </p>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <div className="feature-icon icon-violet">♙</div>
              <h3>Baza klientów</h3>
              <p>
                Przechowuj dane potencjalnych klientów i zarządzaj
                kontaktami z jednego panelu.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon icon-blue">◎</div>
              <h3>Priorytety i analiza</h3>
              <p>
                Porządkuj zapytania według ważności i szybciej
                odnajduj sprawy wymagające uwagi.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon icon-green">◷</div>
              <h3>Historia i notatki</h3>
              <p>
                Zapisuj ustalenia i sprawdzaj historię działań
                związanych z potencjalnymi klientami.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon icon-orange">✦</div>
              <h3>Asystent AI</h3>
              <p>
                Przygotuj aplikację do rozbudowy o inteligentne
                podsumowania i wsparcie pracy handlowca.
              </p>
            </article>
          </div>
        </section>

        <section className="how-section" id="how-it-works">
          <div className="how-content">
            <span className="section-label">PROSTY PROCES</span>
            <h2>Od pierwszego zapytania do uporządkowanej bazy.</h2>
            <p>
              SmartLead AI łączy dane klientów, analizę zapytań
              i historię kontaktów w jednej aplikacji.
            </p>
          </div>

          <div className="steps-list">
            <div className="step">
              <span className="step-number">01</span>
              <div>
                <h3>Dodaj zapytanie</h3>
                <p>Zapisz dane klienta i treść jego wiadomości.</p>
              </div>
            </div>

            <div className="step">
              <span className="step-number">02</span>
              <div>
                <h3>Uporządkuj informacje</h3>
                <p>Korzystaj z kategorii, priorytetów i historii.</p>
              </div>
            </div>

            <div className="step">
              <span className="step-number">03</span>
              <div>
                <h3>Kontroluj kolejne działania</h3>
                <p>Wykorzystuj CRM do organizowania pracy z klientami.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="about-section" id="about">
          <div>
            <span className="section-label">SMARTLEAD AI</span>
            <h2>Technologia, która pomaga odzyskać kontrolę.</h2>
          </div>

          <p>
            SmartLead AI to rozwijany projekt łączący nowoczesny
            interfejs React z backendem FastAPI. Jego celem jest
            usprawnienie zarządzania potencjalnymi klientami
            i codziennymi zadaniami sprzedażowymi.
          </p>
        </section>
      </main>

      <footer className="footer">
        <a href="#home" className="brand">
          <span className="brand-icon">S</span>
          <span>SmartLead<span className="brand-accent"> AI</span></span>
        </a>

        <p>Inteligentniejsze zarządzanie relacjami z klientami.</p>
        <span className="footer-copy">© 2026 SmartLead AI</span>
      </footer>
    </div>
  )
}

export default App