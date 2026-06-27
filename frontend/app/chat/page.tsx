'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Shield, AlertTriangle, Ban, Gauge, RefreshCw, Flag } from 'lucide-react'
import { sendChat, reportFalsePositive } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  decision?: string
  riskScore?: number
  reasonCodes?: string[]
  requestLogId?: number
}

function generateSessionId() {
  return `session_${Math.random().toString(36).slice(2, 10)}`
}

const ACTION_STYLES: Record<string, { bg: string; text: string; icon: React.ReactNode; label: string }> = {
  ALLOW: { bg: 'bg-green-50 border-green-200', text: 'text-green-700', icon: <Shield className="w-3 h-3" />, label: 'Allowed' },
  BLOCK: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', icon: <Ban className="w-3 h-3" />, label: 'Blocked' },
  THROTTLE: { bg: 'bg-orange-50 border-orange-200', text: 'text-orange-700', icon: <Gauge className="w-3 h-3" />, label: 'Throttled' },
  RESTRICT: { bg: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-700', icon: <AlertTriangle className="w-3 h-3" />, label: 'Restricted' },
  LOG_ONLY: { bg: 'bg-blue-50 border-blue-200', text: 'text-blue-700', icon: <Shield className="w-3 h-3" />, label: 'Logged' },
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(generateSessionId)
  const [reportingId, setReportingId] = useState<number | null>(null)
  const [reportReason, setReportReason] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')

    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const data = await sendChat(sessionId, msg)
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || '',
        decision: data.decision,
        riskScore: data.risk_score,
        reasonCodes: data.reason_codes,
        requestLogId: data.request_log_id,
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (e: any) {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'system',
        content: `Error: ${e.message}`,
      }])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  async function submitFalsePositive() {
    if (!reportingId || !reportReason.trim()) return
    try {
      await reportFalsePositive(reportingId, reportReason)
      setReportingId(null)
      setReportReason('')
      alert('False positive report submitted.')
    } catch {
      alert('Failed to submit report.')
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">CloudDesk AI Support</h1>
        <p className="text-slate-500 text-sm mt-1">Protected by Frontline Security Gateway · Session: <code className="font-mono text-xs bg-slate-100 px-1 rounded">{sessionId}</code></p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl min-h-96 max-h-[60vh] overflow-y-auto p-4 mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 py-12">
            <Shield className="w-12 h-12 mx-auto mb-3 text-slate-200" />
            <p>Ask a support question to get started.</p>
            <p className="text-xs mt-2">Try: "How do I reset my password?" or "What payment methods do you accept?"</p>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
              {msg.role === 'user' && (
                <div className="bg-indigo-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm">
                  {msg.content}
                </div>
              )}
              {msg.role === 'assistant' && (
                <div>
                  <div className={`px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm border ${
                    msg.decision && ACTION_STYLES[msg.decision]
                      ? ACTION_STYLES[msg.decision].bg
                      : 'bg-slate-50 border-slate-200'
                  }`}>
                    {msg.content}
                  </div>
                  {msg.decision && (
                    <div className="mt-1.5 flex items-center gap-2 flex-wrap">
                      <span className={`flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border ${
                        msg.decision && ACTION_STYLES[msg.decision]
                          ? `${ACTION_STYLES[msg.decision].bg} ${ACTION_STYLES[msg.decision].text}`
                          : ''
                      }`}>
                        {msg.decision && ACTION_STYLES[msg.decision]?.icon}
                        {msg.decision && ACTION_STYLES[msg.decision]?.label}
                      </span>
                      <span className="text-xs text-slate-400">Risk: {msg.riskScore}/100</span>
                      {msg.reasonCodes && msg.reasonCodes.length > 0 && (
                        <span className="text-xs text-slate-400 truncate max-w-40">{msg.reasonCodes[0]}</span>
                      )}
                      {msg.requestLogId && msg.decision !== 'ALLOW' && (
                        <button
                          onClick={() => setReportingId(msg.requestLogId!)}
                          className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-0.5"
                        >
                          <Flag className="w-3 h-3" />
                          Report false positive
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
              {msg.role === 'system' && (
                <div className="text-xs text-red-500 px-2">{msg.content}</div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm text-slate-400 flex items-center gap-2">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Processing through security pipeline…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your support question..."
          rows={2}
          className="flex-1 border border-slate-200 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white p-3 rounded-xl transition-colors self-end"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>

      {reportingId && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="font-bold text-slate-900 mb-2">Report False Positive</h3>
            <p className="text-sm text-slate-500 mb-4">Tell us why this request should have been allowed.</p>
            <textarea
              value={reportReason}
              onChange={e => setReportReason(e.target.value)}
              placeholder="This was a normal support question about..."
              rows={3}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-4"
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setReportingId(null)} className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900">Cancel</button>
              <button onClick={submitFalsePositive} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm">Submit</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
