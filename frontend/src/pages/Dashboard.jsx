import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

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
  const priorityChartData = [
  { name: 'Wysoki priorytet', value: stats?.high_priority ?? 0 },
  { name: 'Normalny priorytet', value: stats?.normal_priority ?? 0 },
]
  const categoryChartData = Object.entries(stats?.categories ?? {}).map(
  ([name, value]) => ({
    name,
    value,
  }),
)
const statusChartData = Object.entries(stats?.statuses ?? {}).map(
  ([name, value]) => ({
    name,
    value,
  }),
)

  const [leads, setLeads] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [message, setMessage] = useState('Ładowanie danych...')
  const [error, setError] = useState('')
  const [updatingLeadId, setUpdatingLeadId] = useState(null)

  const [expandedLeadId, setExpandedLeadId] = useState(null)
  const [notes, setNotes] = useState({})
  const [notesLoadingLeadId, setNotesLoadingLeadId] = useState(null)
  const [noteDrafts, setNoteDrafts] = useState({})
  const [savingNoteLeadId, setSavingNoteLeadId] = useState(null)

  const filteredLeads = leads.filter((lead) => {
  const query = searchTerm.trim().toLowerCase()

  const matchesSearch =
    (lead.name || '').toLowerCase().includes(query) ||
    (lead.email || '').toLowerCase().includes(query) ||
    (lead.category || '').toLowerCase().includes(query)

  const matchesStatus =
    statusFilter === 'all' || (lead.status || 'new') === statusFilter

  return matchesSearch && matchesStatus
})

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

  async function handleToggleNotes(leadId) {
    if (expandedLeadId === leadId) {
      setExpandedLeadId(null)
      return
    }

    setExpandedLeadId(leadId)

    if (notes[leadId] !== undefined) {
      return
    }

    const token = localStorage.getItem('access_token')

    if (!token) {
      navigate('/login', { replace: true })
      return
    }

    setError('')
    setNotesLoadingLeadId(leadId)

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/leads/${leadId}/notes`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('username')
        navigate('/login', { replace: true })
        return
      }

      if (!response.ok) {
        throw new Error('Nie udało się pobrać notatek klienta.')
      }

      const data = await response.json()
      setNotes((currentNotes) => ({
        ...currentNotes,
        [leadId]: data.notes || [],
      }))
    } catch (err) {
      setError(err.message || 'Wystąpił błąd podczas pobierania notatek.')
    } finally {
      setNotesLoadingLeadId(null)
    }
  }

  async function handleAddNote(leadId) {
    const content = (noteDrafts[leadId] || '').trim()

    if (!content) {
      setError('Wpisz treść notatki przed zapisaniem.')
      return
    }

    const token = localStorage.getItem('access_token')

    if (!token) {
      navigate('/login', { replace: true })
      return
    }

    setError('')
    setSavingNoteLeadId(leadId)

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/leads/${leadId}/notes`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content }),
        },
      )

      if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('username')
        navigate('/login', { replace: true })
        return
      }

      if (!response.ok) {
        throw new Error('Nie udało się zapisać notatki.')
      }

      const data = await response.json()

      setNotes((currentNotes) => ({
        ...currentNotes,
        [leadId]: [...(currentNotes[leadId] || []), data.note],
      }))

      setNoteDrafts((currentDrafts) => ({
        ...currentDrafts,
        [leadId]: '',
      }))
    } catch (err) {
      setError(err.message || 'Wystąpił błąd podczas zapisywania notatki.')
    } finally {
      setSavingNoteLeadId(null)
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
      <strong>{stats.total ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>Wysoki priorytet</span>
      <strong>{stats.high_priority ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>Normalny priorytet</span>
      <strong>{stats.normal_priority ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>Nowe</span>
      <strong>{stats.statuses?.new ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>Skontaktowano się</span>
      <strong>{stats.statuses?.contacted ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>W trakcie realizacji</span>
      <strong>{stats.statuses?.in_progress ?? '—'}</strong>
    </article>

    <article className="dashboard-stat-card">
      <span>Zamknięte</span>
      <strong>{stats.statuses?.closed ?? '—'}</strong>
    </article>
  </div>
)}

  {/* Wykres przedstawiający priorytety leadów */}
<div className="dashboard-chart-card">
  <h2>Priorytety leadów</h2>

  <ResponsiveContainer width="100%" height={300}>
    <PieChart>
      <Pie
        data={priorityChartData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
      >
        {priorityChartData.map((entry, index) => (
          <Cell
            key={`priority-${index}`}
            fill={index === 0 ? '#ef4444' : '#3b82f6'}
          />
        ))}
      </Pie>

      <Tooltip />
      <Legend />
    </PieChart>
  </ResponsiveContainer>
</div>


{/* Wykres przedstawiający kategorie leadów */}
<div className="dashboard-chart-card">
  <h2>Kategorie leadów</h2>

  <ResponsiveContainer width="100%" height={300}>
    <PieChart>
      <Pie
        data={categoryChartData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
      >
        {categoryChartData.map((entry, index) => (
          <Cell
            key={`category-${entry.name}`}
            fill={['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981'][index % 4]}
          />
        ))}
      </Pie>

      <Tooltip />
      <Legend />
    </PieChart>
  </ResponsiveContainer>
</div>


{/* Wykres przedstawiający statusy leadów */}
<div className="dashboard-chart-card">
  <h2>Statusy leadów</h2>

  <ResponsiveContainer width="100%" height={300}>
    <PieChart>
      <Pie
        data={statusChartData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
      >
        {statusChartData.map((entry, index) => (
          <Cell
            key={`status-${entry.name}`}
            fill={['#0ea5e9', '#f59e0b', '#10b981', '#ef4444'][index % 4]}
          />
        ))}
      </Pie>

      <Tooltip />
      <Legend />
    </PieChart>
  </ResponsiveContainer>
</div>


        <section className="dashboard-leads">
          <h2>Lista leadów</h2>

            <div className="leads-filters">
  <label htmlFor="lead-search">Szukaj klienta</label>
  <input
    id="lead-search"
    type="text"
    value={searchTerm}
    onChange={(event) => setSearchTerm(event.target.value)}
    placeholder="Imię, e-mail lub kategoria..."
  />

  <label htmlFor="lead-status-filter">Filtruj według statusu</label>
  <select
    id="lead-status-filter"
    value={statusFilter}
    onChange={(event) => setStatusFilter(event.target.value)}
  >
    <option value="all">Wszystkie statusy</option>
    {STATUS_OPTIONS.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>
</div>

<p>
  Liczba znalezionych leadów: {filteredLeads.length}
</p>

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
                    <th>Notatki</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredLeads.map((lead) => (
                    <>
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
                        <td>
                          <button
                            className="button button-login"
                            type="button"
                            onClick={() => handleToggleNotes(lead.id)}
                          >
                            {expandedLeadId === lead.id
                              ? 'Ukryj notatki'
                              : 'Pokaż notatki'}
                          </button>
                        </td>
                      </tr>

                      {expandedLeadId === lead.id && (
                        <tr key={`notes-${lead.id}`}>
                          <td colSpan="6">
                            <section aria-label={`Notatki klienta ${lead.name}`}>
                              <h3>Notatki: {lead.name}</h3>

                              {notesLoadingLeadId === lead.id && (
                                <p role="status">Ładowanie notatek...</p>
                              )}

                              {notes[lead.id] && notes[lead.id].length === 0 && (
                                <p>Ten klient nie ma jeszcze notatek.</p>
                              )}

                              {notes[lead.id]?.map((note) => (
                                <article key={note.id}>
                                  <p>{note.content}</p>
                                  <small>
                                    {note.created_at
                                      ? new Date(note.created_at).toLocaleString('pl-PL')
                                      : ''}
                                  </small>
                                </article>
                              ))}

                              <label htmlFor={`note-${lead.id}`}>
                                Dodaj notatkę
                              </label>
                              <textarea
                                id={`note-${lead.id}`}
                                rows="3"
                                value={noteDrafts[lead.id] || ''}
                                onChange={(event) =>
                                  setNoteDrafts((currentDrafts) => ({
                                    ...currentDrafts,
                                    [lead.id]: event.target.value,
                                  }))
                                }
                                placeholder="Wpisz treść notatki..."
                              />

                              <button
                                className="button button-login"
                                type="button"
                                disabled={savingNoteLeadId === lead.id}
                                onClick={() => handleAddNote(lead.id)}
                              >
                                {savingNoteLeadId === lead.id
                                  ? 'Zapisywanie...'
                                  : 'Zapisz notatkę'}
                              </button>
                            </section>
                          </td>
                        </tr>
                      )}
                    </>
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
