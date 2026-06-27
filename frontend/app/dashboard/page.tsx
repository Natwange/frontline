'use client'
import { useState, useEffect } from 'react'
import { RefreshCw, Shield, Ban, AlertTriangle, Gauge, DollarSign, Brain } from 'lucide-react'
import { getDashboardMetrics, getDashboardLogs, getAttackCategories, getRiskDistribution } from '@/lib/api'

function MetricCard({ label, value, sub, icon, color }: {
  label: string
  value: string | number
  sub?: string
  icon: React.ReactNode
  color: string
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-slate-500">{label}</span>
        <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
      </div>
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      {sub && <div className="text-xs text-slate-400 mt-1">{sub}</div>}
    </div>
  )
}

const ACTION_COLORS: Record<string, string> = {
  ALLOW: 'text-green-600 bg-green-50',
  BLOCK: 'text-red-600 bg-red-50',
  THROTTLE: 'text-orange-600 bg-orange-50',
  RESTRICT: 'text-yellow-700 bg-yellow-50',
  LOG_ONLY: 'text-blue-600 bg-blue-50',
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null)
  const [logs, setLogs] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [riskDist, setRiskDist] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [actionFilter, setActionFilter] = useState('')
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [m, l, c, r] = await Promise.all([
        getDashboardMetrics(),
        getDashboardLogs(50, actionFilter || undefined),
        getAttackCategories(),
        getRiskDistribution(),
      ])
      setMetrics(m)
      setLogs(l)
      setCategories(c)
      setRiskDist(r)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [actionFilter])

  const maxCat = categories.reduce((m, c) => Math.max(m, c.count), 1)
  const maxDist = riskDist.reduce((m: number, r: any) => Math.max(m, r.count), 1)

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Security Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">Request logs, risk analysis, and security metrics</p>
        </div>
        <button onClick={load} disabled={loading} className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-3 py-2 rounded-lg">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg mb-6">{error}</div>}

      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <MetricCard label="Total Requests" value={metrics.total_requests} icon={<Shield className="w-4 h-4 text-slate-600" />} color="bg-slate-100" />
          <MetricCard label="Allowed" value={metrics.allowed_requests} icon={<Shield className="w-4 h-4 text-green-600" />} color="bg-green-100" />
          <MetricCard label="Blocked" value={metrics.blocked_requests} icon={<Ban className="w-4 h-4 text-red-600" />} color="bg-red-100" />
          <MetricCard label="Throttled" value={metrics.throttled_requests} icon={<Gauge className="w-4 h-4 text-orange-600" />} color="bg-orange-100" />
          <MetricCard label="Restricted" value={metrics.restricted_requests} icon={<AlertTriangle className="w-4 h-4 text-yellow-600" />} color="bg-yellow-100" />
          <MetricCard label="Avg Risk Score" value={`${metrics.average_risk_score}/100`} icon={<Shield className="w-4 h-4 text-indigo-600" />} color="bg-indigo-100" />
          <MetricCard label="Cost Saved (est)" value={`$${metrics.estimated_cost_saved_usd?.toFixed(4)}`} icon={<DollarSign className="w-4 h-4 text-emerald-600" />} color="bg-emerald-100" sub="Estimated AI cost avoided" />
          <MetricCard label="AI Classifier Usage" value={`${(metrics.ai_classifier_usage_rate * 100).toFixed(1)}%`} icon={<Brain className="w-4 h-4 text-purple-600" />} color="bg-purple-100" sub="Of total requests" />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-800 mb-4">Attack Categories</h2>
          {categories.length === 0 && <p className="text-sm text-slate-400">No attack categories detected yet.</p>}
          <div className="space-y-3">
            {categories.map((cat: any) => (
              <div key={cat.category}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700 font-mono text-xs">{cat.category}</span>
                  <span className="text-slate-500">{cat.count}</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(cat.count / maxCat) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-800 mb-4">Risk Score Distribution</h2>
          {riskDist.every((r: any) => r.count === 0) && <p className="text-sm text-slate-400">No requests logged yet.</p>}
          <div className="space-y-3">
            {riskDist.map((r: any) => (
              <div key={r.range}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Score {r.range}</span>
                  <span className="text-slate-500">{r.count}</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${
                    r.range === '0-20' ? 'bg-green-400' :
                    r.range === '21-40' ? 'bg-lime-400' :
                    r.range === '41-60' ? 'bg-yellow-400' :
                    r.range === '61-80' ? 'bg-orange-400' : 'bg-red-500'
                  }`} style={{ width: `${(r.count / maxDist) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">Recent Requests</h2>
          <select
            value={actionFilter}
            onChange={e => setActionFilter(e.target.value)}
            className="text-sm border border-slate-200 rounded-lg px-2 py-1 focus:outline-none"
          >
            <option value="">All actions</option>
            <option value="ALLOW">Allowed</option>
            <option value="BLOCK">Blocked</option>
            <option value="THROTTLE">Throttled</option>
            <option value="RESTRICT">Restricted</option>
          </select>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 text-xs border-b border-slate-100">
                <th className="px-5 py-3 font-medium">Session</th>
                <th className="px-5 py-3 font-medium">Message</th>
                <th className="px-5 py-3 font-medium">Decision</th>
                <th className="px-5 py-3 font-medium">Risk</th>
                <th className="px-5 py-3 font-medium">Reason</th>
                <th className="px-5 py-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 && (
                <tr><td colSpan={6} className="px-5 py-8 text-center text-slate-400">No requests logged yet.</td></tr>
              )}
              {logs.map((log: any) => (
                <tr key={log.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3 font-mono text-xs text-slate-500">{log.session_id?.slice(0, 12)}…</td>
                  <td className="px-5 py-3 text-slate-700 max-w-xs">
                    <span className="truncate block max-w-48" title={log.redacted_message || ''}>
                      {log.redacted_message?.slice(0, 60) || '—'}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ACTION_COLORS[log.final_action] || 'text-slate-600 bg-slate-100'}`}>
                      {log.final_action}
                    </span>
                  </td>
                  <td className="px-5 py-3 font-mono text-xs text-slate-600">{log.risk_score}</td>
                  <td className="px-5 py-3 font-mono text-xs text-slate-400">{log.reason_codes?.[0] || '—'}</td>
                  <td className="px-5 py-3 text-xs text-slate-400">{new Date(log.created_at).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
