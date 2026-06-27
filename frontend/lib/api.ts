const API_BASE = '/api'

export async function sendChat(sessionId: string, message: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export async function getDashboardMetrics() {
  const res = await fetch(`${API_BASE}/dashboard/metrics`)
  if (!res.ok) throw new Error('Failed to fetch metrics')
  return res.json()
}

export async function getDashboardLogs(limit = 50, action?: string) {
  const params = new URLSearchParams({ limit: String(limit) })
  if (action) params.set('action', action)
  const res = await fetch(`${API_BASE}/dashboard/logs?${params}`)
  if (!res.ok) throw new Error('Failed to fetch logs')
  return res.json()
}

export async function getAttackCategories() {
  const res = await fetch(`${API_BASE}/dashboard/attack-categories`)
  if (!res.ok) throw new Error('Failed to fetch attack categories')
  return res.json()
}

export async function getRiskDistribution() {
  const res = await fetch(`${API_BASE}/dashboard/risk-distribution`)
  if (!res.ok) throw new Error('Failed to fetch risk distribution')
  return res.json()
}

export async function runSimulator(scenario: string, requestCount: number, sessionId?: string) {
  const res = await fetch(`${API_BASE}/simulator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, request_count: requestCount, session_id: sessionId }),
  })
  if (!res.ok) throw new Error('Simulator failed')
  return res.json()
}

export async function reportFalsePositive(requestLogId: number, reason: string) {
  const res = await fetch(`${API_BASE}/false-positive-reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_log_id: requestLogId, reason }),
  })
  if (!res.ok) throw new Error('Failed to submit report')
  return res.json()
}
