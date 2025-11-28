import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FileText, Settings, Shield, Brain } from 'lucide-react'
import { useAuth } from '../lib/auth'

export default function MobileNav() {
  const location = useLocation()
  const { user } = useAuth()

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Home' },
    { path: '/predict', icon: Brain, label: 'Predict' },
    { path: '/reports', icon: FileText, label: 'Reports' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  if (user?.role === 'admin') {
    navItems.push({ path: '/admin', icon: Shield, label: 'Admin' })
  }

  return (
    <nav className="mobile-nav lg:hidden">
      <div className="grid grid-cols-4 sm:grid-cols-5 gap-0.5">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center py-2 px-1 rounded-lg transition-all min-h-[56px] touch-target ${
                isActive
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50 active:bg-gray-100'
              }`}
            >
              <Icon className={`w-6 h-6 mb-1 ${isActive ? 'scale-110' : ''}`} />
              <span className="text-xs font-medium leading-tight">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
