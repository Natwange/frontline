import Link from 'next/link'
import { Shield, Zap, BarChart3, Terminal } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <div className="flex justify-center mb-4">
          <div className="bg-indigo-600 p-3 rounded-2xl">
            <Shield className="w-10 h-10 text-white" />
          </div>
        </div>
        <h1 className="text-5xl font-bold text-slate-900 mb-4">Frontline</h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
          Production-inspired security gateway that protects AI agents from bot attacks,
          prompt injection, and cost abuse before requests reach the model.
        </p>
        <div className="flex justify-center gap-4 mt-8">
          <Link
            href="/chat"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Try the Chat
          </Link>
          <Link
            href="/dashboard"
            className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            View Dashboard
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
        <FeatureCard
          icon={<Zap className="w-6 h-6 text-indigo-600" />}
          title="Layered Protection"
          description="6-layer pipeline: validation, rate limiting, behavior analysis, prompt attack rules, cost protection, and AI risk classification."
        />
        <FeatureCard
          icon={<Shield className="w-6 h-6 text-indigo-600" />}
          title="Cheap Checks First"
          description="Deterministic rules run before expensive AI calls. Obvious attacks are stopped early without spending AI tokens."
        />
        <FeatureCard
          icon={<BarChart3 className="w-6 h-6 text-indigo-600" />}
          title="Analytics Dashboard"
          description="Full visibility into traffic patterns, risk scores, attack categories, and estimated AI cost saved."
        />
        <FeatureCard
          icon={<Terminal className="w-6 h-6 text-indigo-600" />}
          title="Attack Simulator"
          description="Run pre-built attack scenarios — spam bots, slow bots, prompt attacks, cost attacks — and see the pipeline in action."
        />
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Protection Pipeline</h2>
        <div className="space-y-3">
          {[
            { layer: 'Layer 0', name: 'Request Validation', desc: 'Basic integrity checks — message exists, not too long, valid session' },
            { layer: 'Layer 1', name: 'Rate Limit Defense', desc: 'Redis-backed session and IP throttling for bot traffic' },
            { layer: 'Layer 2', name: 'Behavior Analysis', desc: 'Repeated message detection and pattern tracking' },
            { layer: 'Layer 3', name: 'Prompt Attack Rules', desc: 'Regex-based detection of injection and override attempts' },
            { layer: 'Layer 4', name: 'Cost Protection', desc: 'Detection of expensive output requests' },
            { layer: 'Layer 5', name: 'AI Risk Classifier', desc: 'Claude-powered classification for ambiguous borderline cases' },
          ].map((item, i) => (
            <div key={i} className="flex items-start gap-4 p-3 rounded-lg bg-slate-50">
              <span className="text-xs font-mono bg-indigo-100 text-indigo-700 px-2 py-1 rounded whitespace-nowrap">
                {item.layer}
              </span>
              <div>
                <span className="font-semibold text-slate-800">{item.name}</span>
                <span className="text-slate-500 ml-2 text-sm">— {item.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-3">
        <div className="bg-indigo-50 p-2 rounded-lg">{icon}</div>
        <h3 className="font-semibold text-slate-900">{title}</h3>
      </div>
      <p className="text-slate-600 text-sm">{description}</p>
    </div>
  )
}
