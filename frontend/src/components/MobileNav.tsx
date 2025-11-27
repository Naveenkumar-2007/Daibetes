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
      <div className="grid grid-cols-4 sm:grid-cols-5 gap-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center py-2 px-2 rounded-lg transition-all ${
                isActive
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
              }`}
            >
              <Icon className={`w-5 h-5 sm:w-6 sm:h-6 ${isActive ? 'scale-110' : ''}`} />
              <span className="text-xs mt-1 font-medium">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
