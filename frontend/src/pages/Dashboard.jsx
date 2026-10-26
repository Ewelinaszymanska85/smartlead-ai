import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const STATUS_OPTIONS = [
  { value: 'new', label: 'Nowy' },
  { value: 'contacted', label: 'Skontaktowano się' },
  { value: 'in_progress', label: 'W trakcie realizacji' },
  { value: 'closed', label: 'Zamknięty' },
]

function getStatusLabel(status) {
  return STATUS_OPTIONS.find((option) => option.value === status)?.label || status || '—'
}

function Dashboard() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [stats, setStats] = useState(null)
  const [leads, setLeads] = useState([])
  const [message, setMessage] = useState('Ładowanie danych...')
  const [error, setError] = useState('')
  const [updatingLeadId, setUpdatingLeadId] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const savedUsername = localStorage.getItem('username')

    if (!token) {
      navigate('/login', { replace: true })
      return
    }

    setUsername(savedUsername || '')

    async function loadDashboard() {
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        }

        const [statsResponse, leadsResponse] = await Promise.all([
          fetch('http://127.0.0.1:8000/stats', { headers }),
          fetch('http://127.0.0.1:8000/leads', { headers }),
        ])

        if (statsResponse.status === 401 || leadsResponse.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('username')
          navigate('/login', { replace: true })
          return
        }

        if (!statsResponse.ok || !leadsResponse.ok) {
          throw new Error('Nie udało się pobrać danych z serwera.')
        }

        const statsData = await statsResponse.json()
        const leadsData = await leadsResponse.json()

        setStats(statsData)
        setLeads(Array.isArray(leadsData) ? leadsData : leadsData.leads || [])
        setMessage('')
      } catch (err) {
        setError(err.message || 'Wystąpił błąd połączenia z serwerem.')
        setMessage('')
      }
    }

    loadDashboard()
  }, [navigate])

  async function handleStatusChange(leadId, newStatus) {
    const token = localStorage.getItem('access_token')
    const previousLead = leads.find((lead) => lead.id === leadId)

    if (!token || !previousLead) {
      navigate('/login', { replace: true })
      return
    }

    setError('')
    setUpdatingLeadId(leadId)

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/leads/${leadId}/status`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        },
      )

      if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('username')
        navigate('/login', { replace: true })
        return
      }

      if (!response.ok) {
        throw new Error('Nie udało się zapisać nowego statusu.')
      }

      const updatedLead = await response.json()

      setLeads((currentLeads) =>
        currentLeads.map((lead) =>
          lead.id === leadId ? updatedLead : lead,
        ),
      )
    } catch (err) {
      setError(err.message || 'Wystąpił błąd podczas zmiany statusu.')
    } finally {
      setUpdatingLeadId(null)
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    navigate('/login', { replace: true })
  }

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <a href="/" className="brand">
          <span className="brand-icon">S</span>
          <span>
            SmartLead<span className="brand-accent"> AI</span>
          </span>
        </a>

        <div className="dashboard-user">
          <span>{username || 'Użytkownik'}</span>
          <button
            className="button button-login"
            type="button"
            onClick={handleLogout}
          >
            Wyloguj się
          </button>
        </div>
      </header>

      <section className="dashboard-content">
        <span className="section-label">SMARTLEAD AI</span>
        <h1>Panel główny</h1>
        <p className="dashboard-description">
          Witaj{username ? `, ${username}` : ''}! Oto podsumowanie Twoich leadów.
        </p>

        {message && <p role="status">{message}</p>}
        {error && <p role="alert">{error}</p>}

        {stats && (
          <div className="dashboard-stats">
            <article className="dashboard-stat-card">
              <span>Wszyscy klienci</span>
              <strong>
                {stats.total_leads ?? stats.total ?? stats.count ?? '—'}
              </strong>
            </article>

            <article className="dashboard-stat-card">
              <span>Wysoki priorytet</span>
              <strong>
                {stats.high_priority ?? stats.high_priority_leads ?? '—'}
              </strong>
            </article>
          </div>
        )}

        <section className="dashboard-leads">
          <h2>Lista leadów</h2>

          {leads.length === 0 && !message && !error && (
            <p>Nie ma jeszcze żadnych leadów.</p>
          )}

          {leads.length > 0 && (
            <div className="dashboard-table-wrapper">
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>Klient</th>
                    <th>E-mail</th>
                    <th>Kategoria</th>
                    <th>Priorytet</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {leads.map((lead) => (
                    <tr key={lead.id}>
                      <td>{lead.name || '—'}</td>
                      <td>{lead.email || '—'}</td>
                      <td>{lead.category || '—'}</td>
                      <td>{lead.priority || '—'}</td>
                      <td>
                        <select
                          aria-label={`Status leada: ${lead.name}`}
                          value={lead.status || 'new'}
                          disabled={updatingLeadId === lead.id}
                          onChange={(event) =>
                            handleStatusChange(lead.id, event.target.value)
                          }
                        >
                          {STATUS_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                        <span className="sr-only">
                          Aktualny status: {getStatusLabel(lead.status)}
                        </span>
                        {updatingLeadId === lead.id && (
                          <span role="status"> Zapisywanie...</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  )
}

export default Dashboard
