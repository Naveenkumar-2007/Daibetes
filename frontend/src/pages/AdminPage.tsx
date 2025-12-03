import { useState, useEffect } from 'react'
import { Users, FileText, TrendingUp, Activity, Trash2, Bot } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { useNavigate, Link } from 'react-router-dom'
import { adminAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'
import ChatbotTrainingPage from './ChatbotTrainingPage'

interface User {
  user_id: string
  username: string
  full_name: string
  email: string
  created_at: string
  prediction_count: number
  report_count: number
}

interface Stats {
  total_users: number
  total_predictions: number
  total_reports: number
  positive_predictions: number
}

export default function AdminPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'users' | 'chatbot'>('users')
  const [users, setUsers] = useState<User[]>([])
  const [stats, setStats] = useState<Stats>({
    total_users: 0,
    total_predictions: 0,
    total_reports: 0,
    positive_predictions: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is admin
    if (user?.role !== 'admin') {
      navigate('/dashboard')
      return
    }
    fetchAdminData()
  }, [user, navigate])

  const fetchAdminData = async () => {
    try {
      const [usersResponse, statsResponse] = await Promise.all([
        adminAPI.getUsers(),
        adminAPI.getStats()
      ])

      if (usersResponse.data.success) {
        setUsers(usersResponse.data.users || [])
      }
      if (statsResponse.data.success) {
        setStats(statsResponse.data.stats)
      }
    } catch (error) {
      console.error('Error fetching admin data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteUser = async (userId: string, username: string, fullName: string) => {
    if (!confirm(`⚠️ Delete user "${fullName}" (@${username})?\n\nThis will permanently remove:\n• User account\n• All predictions\n• All reports\n• Chat history\n\nThis action CANNOT be undone!`)) {
      return
    }

    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        alert(`✅ User "${fullName}" deleted successfully`)
        fetchAdminData() // Refresh user list
      } else {
        alert('❌ Delete failed: ' + data.error)
      }
    } catch (error) {
      alert('❌ Delete failed. Please try again.')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">Manage users and AI chatbot</p>
            </div>
            <div className="flex items-center gap-3">
              <Link to="/dashboard" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                Back to Dashboard
              </Link>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Logout
              </button>
            </div>
          </div>


        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 pb-24">
        {/* Tab Navigation */}
        <div className="mb-6 border-b border-gray-200">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('users')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'users'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                <span>User Management</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('chatbot')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'chatbot'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                <span>Chatbot Training</span>
              </div>
            </button>
          </div>
        </div>

        {/* Conditional Content Based on Active Tab */}
        {activeTab === 'users' && (
          <>
        {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card"
              >
                <Users className="w-8 h-8 text-blue-600 mb-2" />
                <p className="text-sm text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card"
              >
                <Activity className="w-8 h-8 text-green-600 mb-2" />
                <p className="text-sm text-gray-600">Predictions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_predictions}</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card"
              >
                <FileText className="w-8 h-8 text-purple-600 mb-2" />
                <p className="text-sm text-gray-600">Reports</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_reports}</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="card"
              >
                <TrendingUp className="w-8 h-8 text-red-600 mb-2" />
                <p className="text-sm text-gray-600">High Risk</p>
                <p className="text-2xl font-bold text-gray-900">{stats.positive_predictions}</p>
              </motion.div>
            </div>

            {/* Users Table */}
            <div className="card overflow-hidden">
              <h2 className="text-lg font-bold text-gray-900 mb-4">All Users</h2>
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                        <th className="hidden sm:table-cell px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                        <th className="hidden md:table-cell px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                        <th className="px-3 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stats</th>
                        <th className="px-3 sm:px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Action</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.user_id} className="hover:bg-gray-50">
                          <td className="px-3 sm:px-4 py-3">
                            <div>
                              <p className="text-sm font-medium text-gray-900 truncate max-w-[150px] sm:max-w-none">{user.full_name}</p>
                              <p className="text-xs text-gray-500">@{user.username}</p>
                            </div>
                          </td>
                          <td className="hidden sm:table-cell px-4 py-3 text-sm text-gray-600 truncate max-w-[200px]">{user.email}</td>
                          <td className="hidden md:table-cell px-4 py-3 text-sm text-gray-600">
                            {new Date(user.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-3 sm:px-4 py-3">
                            <div className="flex flex-col gap-1">
                              <span className="text-xs text-gray-600">
                                📊 {user.prediction_count} predictions
                              </span>
                              <span className="text-xs text-gray-600">
                                📄 {user.report_count} reports
                              </span>
                            </div>
                          </td>
                          <td className="px-3 sm:px-4 py-3 text-right">
                            <div className="flex justify-end gap-2">
                              <button
                                onClick={() => {
                                  // Open user predictions in a modal or navigate to React page
                                  alert(`Viewing predictions for user: ${user.full_name}\n\nPredictions: ${user.prediction_count}\nReports: ${user.report_count}`)
                                  // TODO: Navigate to user detail page or open modal
                                }}
                                className="inline-flex items-center gap-1 px-2 sm:px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 active:bg-blue-100 rounded-lg transition-colors touch-target"
                                title="View user predictions"
                              >
                                <FileText className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                                <span className="hidden sm:inline">View</span>
                              </button>
                              <button
                                onClick={() => handleDeleteUser(user.user_id, user.username, user.full_name)}
                                className="inline-flex items-center gap-1 px-2 sm:px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 active:bg-red-100 rounded-lg transition-colors touch-target"
                                title="Delete user"
                              >
                                <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                                <span className="hidden sm:inline">Delete</span>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Chatbot Training Tab */}
        {activeTab === 'chatbot' && (
          <ChatbotTrainingPage />
        )}
      </main>

      <MobileNav />
    </div>
  )
}
