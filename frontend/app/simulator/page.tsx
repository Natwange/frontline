'use client'
import { useState } from 'react'
import { Play, Terminal, CheckCircle, XCircle, AlertTriangle, Gauge, Shield } from 'lucide-react'
import { runSimulator } from '@/lib/api'

const SCENARIOS = [
  {
    id: 'normal_user',
    label: 'Normal User',
    desc: 'Sends typical support questions about billing, account, and product features.',
    color: 'bg-green-50 border-green-200 text-green-800',
    expected: 'Should be mostly ALLOWED',
  },
  {
    id: 'spam_bot',
    label: 'Spam Bot',
    desc: 'Sends the same request at high speed to overwhelm the system.',
    color: 'bg-red-50 border-red-200 text-red-800',
    expected: 'Should be THROTTLED or BLOCKED',
  },
  {
    id: 'repeated_message',
    label: 'Repeated Message',
    desc: 'Sends the same message over and over.',
    color: 'bg-orange-50 border-orange-200 text-orange-800',
    expected: 'Should escalate to THROTTLE/BLOCK',
  },
  {
    id: 'prompt_attack',
    label: 'Prompt Attack',
    desc: 'Attempts to override AI instructions or extract system prompts.',
    color: 'bg-red-50 border-red-200 text-red-800',
    expected: 'Should be BLOCKED or RESTRICTED',
  },
  {
    id: 'cost_attack',
    label: 'Cost Attack',
    desc: 'Requests extremely long outputs to drain AI token usage.',
    color: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    expected: 'Should be RESTRICTED or BLOCKED',
  },
  {
    id: 'slow_bot',
    label: 'Slow Bot',
    desc: 'Sends requests at human-like intervals but with suspicious patterns.',
    color: 'bg-orange-50 border-orange-200 text-orange-800',
    expected: 'Should be detected via behavior analysis',
  },
]

const DECISION_ICONS: Record<string, React.ReactNode> = {
  ALLOW: <CheckCircle className="w-4 h-4 text-green-500" />,
  BLOCK: <XCircle className="w-4 h-4 text-red-500" />,
  THROTTLE: <Gauge className="w-4 h-4 text-orange-500" />,
  RESTRICT: <AlertTriangle className="w-4 h-4 text-yellow-500" />,
  LOG_ONLY: <Shield className="w-4 h-4 text-blue-500" />,
}

const ACTION_COLORS: Record<string, string> = {
  ALLOW: 'text-green-700 bg-green-50',
  BLOCK: 'text-red-700 bg-red-50',
  THROTTLE: 'text-orange-700 bg-orange-50',
  RESTRICT: 'text-yellow-700 bg-yellow-50',
  LOG_ONLY: 'text-blue-700 bg-blue-50',
}

export default function SimulatorPage() {
  const [selected, setSelected] = useState('normal_user')
  const [count, setCount] = useState(10)
  const [result, setResult] = useState<any>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  async function run() {
    setRunning(true)
    setError('')
    setResult(null)
    try {
      const data = await runSimulator(selected, count)
      setResult(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const selectedScenario = SCENARIOS.find(s => s.id === selected)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Attack Simulator</h1>
        <p className="text-slate-500 text-sm mt-1">Run attack scenarios against the Frontline security pipeline and observe how requests are handled.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <h2 className="font-semibold text-slate-800 mb-3">Select Scenario</h2>
          <div className="space-y-2">
            {SCENARIOS.map(s => (
              <button
                key={s.id}
                onClick={() => setSelected(s.id)}
                className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                  selected === s.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-slate-900 text-sm">{s.label}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${s.color}`}>
                    {s.expected}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{s.desc}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h2 className="font-semibold text-slate-800 mb-4">Configure Run</h2>
            <div className="mb-4">
              <label className="text-sm text-slate-600 mb-2 block">Scenario</label>
              <div className={`p-3 rounded-lg border ${selectedScenario?.color}`}>
                <div className="font-semibold text-sm">{selectedScenario?.label}</div>
                <div className="text-xs mt-0.5">{selectedScenario?.desc}</div>
              </div>
            </div>
            <div className="mb-6">
              <label className="text-sm text-slate-600 mb-2 block">Request Count: <span className="font-semibold text-slate-900">{count}</span></label>
              <input
                type="range"
                min={1}
                max={50}
                value={count}
                onChange={e => setCount(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>1</span><span>50</span>
              </div>
            </div>
            <button
              onClick={run}
              disabled={running}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              {running ? (
                <><Terminal className="w-4 h-4 animate-pulse" />Running {count} requests…</>
              ) : (
                <><Play className="w-4 h-4" />Run Simulation</>
              )}
            </button>
          </div>

          {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>}

          {result && (
            <div className="bg-white border border-slate-200 rounded-xl p-5">
              <h3 className="font-semibold text-slate-800 mb-3">Results Summary</h3>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-slate-50 rounded-lg p-3 text-center">
                  <div className="text-xl font-bold text-slate-900">{result.total_sent}</div>
                  <div className="text-xs text-slate-500">Total Sent</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3 text-center">
                  <div className="text-xl font-bold text-slate-900">{result.summary.avg_risk_score}</div>
                  <div className="text-xs text-slate-500">Avg Risk Score</div>
                </div>
              </div>
              <div className="space-y-2">
                {Object.entries(result.summary.by_action || {}).map(([action, count]: [string, any]) => (
                  <div key={action} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      {DECISION_ICONS[action]}
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ACTION_COLORS[action] || ''}`}>{action}</span>
                    </div>
                    <span className="font-semibold text-slate-700">{count} <span className="text-slate-400 font-normal">requests</span></span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {result && result.results.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl">
          <div className="p-5 border-b border-slate-100">
            <h2 className="font-semibold text-slate-800">Request-by-Request Results</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 text-xs border-b border-slate-100">
                  <th className="px-5 py-3 font-medium">#</th>
                  <th className="px-5 py-3 font-medium">Message</th>
                  <th className="px-5 py-3 font-medium">Decision</th>
                  <th className="px-5 py-3 font-medium">Risk</th>
                  <th className="px-5 py-3 font-medium">Reason</th>
                </tr>
              </thead>
              <tbody>
                {result.results.map((r: any) => (
                  <tr key={r.index} className="border-b border-slate-50 hover:bg-slate-50">
                    <td className="px-5 py-3 text-slate-400 font-mono text-xs">{r.index}</td>
                    <td className="px-5 py-3 text-slate-600 max-w-xs">
                      <span className="truncate block max-w-64" title={r.message}>{r.message}</span>
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1.5">
                        {DECISION_ICONS[r.decision]}
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ACTION_COLORS[r.decision] || ''}`}>{r.decision}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 font-mono text-xs text-slate-600">{r.risk_score}</td>
                    <td className="px-5 py-3 font-mono text-xs text-slate-400 max-w-40 truncate">{r.reason_codes?.[0] || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
