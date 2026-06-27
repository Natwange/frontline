'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Shield } from 'lucide-react'

const links = [
  { href: '/', label: 'Home' },
  { href: '/chat', label: 'Chat' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/simulator', label: 'Simulator' },
]

export default function Navbar() {
  const pathname = usePathname()
  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-slate-900">
          <Shield className="w-5 h-5 text-indigo-600" />
          Frontline
        </Link>
        <div className="flex items-center gap-1 ml-4">
          {links.map(l => (
            <Link
              key={l.href}
              href={l.href}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                pathname === l.href
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <div className="ml-auto">
          <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
            CloudDesk Protected
          </span>
        </div>
      </div>
    </nav>
  )
}
