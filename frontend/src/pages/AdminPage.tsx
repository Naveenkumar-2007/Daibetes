import { useState, useEffect } from 'react'
import { Users, FileText, TrendingUp, Activity, Upload, Database, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { useNavigate } from 'react-router-dom'
import { adminAPI } from '../lib/api'

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

interface ChatbotDocument {
  id: string
  filename?: string
  type: string
  url?: string
  uploaded_at: string
  size: number
}

export default function AdminPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [users, setUsers] = useState<User[]>([])
  const [stats, setStats] = useState<Stats>({
    total_users: 0,
    total_predictions: 0,
    total_reports: 0,
    positive_predictions: 0
  })
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'users' | 'chatbot'>('users')
  const [documents, setDocuments] = useState<ChatbotDocument[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showUserModal, setShowUserModal] = useState(false)

  useEffect(() => {
    // Check if user is admin
    if (user?.role !== 'admin') {
      navigate('/dashboard')
      return
    }
    fetchAdminData()
    if (activeTab === 'chatbot') {
      fetchDocuments()
    }
  }, [user, navigate, activeTab])

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

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/admin/chatbot/documents', {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setDocuments(data.documents || [])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        credentials: 'include',
        body: formData
      })
      const data = await response.json()
      if (data.success) {
        alert('Document uploaded successfully!')
        fetchDocuments()
      } else {
        alert('Upload failed: ' + data.error)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleUrlUpload = async () => {
    const url = prompt('Enter URL:')
    if (!url) return

    setUploading(true)
    try {
      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ url })
      })
      const data = await response.json()
      if (data.success) {
        alert('URL content added successfully!')
        fetchDocuments()
      } else {
        alert('Failed: ' + data.error)
      }
    } catch (error) {
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleTextUpload = async () => {
    const title = prompt('Enter title:')
    if (!title) return
    const text = prompt('Enter text content:')
    if (!text) return

    setUploading(true)
    try {
      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title, text })
      })
      const data = await response.json()
      if (data.success) {
        alert('Text added successfully!')
        fetchDocuments()
      } else {
        alert('Failed: ' + data.error)
      }
    } catch (error) {
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Delete this document?')) return

    try {
      const response = await fetch(`/api/admin/chatbot/documents/${docId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        alert('Document deleted!')
        fetchDocuments()
      }
    } catch (error) {
      alert('Delete failed')
    }
  }

  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!confirm(`Are you sure you want to delete user "${userName}"? This will delete all their predictions and reports. This action cannot be undone.`)) return

    try {
      const response = await adminAPI.deleteUser(userId)
      if (response.data.success) {
        alert('User deleted successfully!')
        fetchAdminData()
      } else {
        alert('Failed to delete user: ' + (response.data.error || 'Unknown error'))
      }
    } catch (error: any) {
      console.error('Delete user error:', error)
      alert('Failed to delete user: ' + (error.response?.data?.error || error.message || 'Network error'))
    }
  }

  if (user?.role !== 'admin') {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-extrabold text-purple-900">ADMIN DASHBOARD</div>
            <div className="flex items-center gap-6">
              <a href="/dashboard" className="text-gray-700 hover:text-purple-600 transition-colors">User Dashboard</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">System Overview</h1>
          <p className="text-gray-600">Monitor users, predictions, and chatbot knowledge base</p>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'users'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Users className="inline w-5 h-5 mr-2" />
            Users & Stats
          </button>
          <button
            onClick={() => setActiveTab('chatbot')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'chatbot'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Database className="inline w-5 h-5 mr-2" />
            Chatbot Knowledge Base
          </button>
        </div>

        {activeTab === 'users' ? (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <Users className="w-8 h-8" />
              <span className="text-3xl font-bold">{stats.total_users}</span>
            </div>
            <p className="text-blue-100 font-medium">Total Users</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <Activity className="w-8 h-8" />
              <span className="text-3xl font-bold">{stats.total_predictions}</span>
            </div>
            <p className="text-green-100 font-medium">Total Predictions</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <FileText className="w-8 h-8" />
              <span className="text-3xl font-bold">{stats.total_reports}</span>
            </div>
            <p className="text-purple-100 font-medium">Total Reports</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8" />
              <span className="text-3xl font-bold">{stats.positive_predictions}</span>
            </div>
            <p className="text-red-100 font-medium">Positive Cases</p>
          </motion.div>
        </div>

        {/* Users Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl shadow-lg overflow-hidden"
        >
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">All Users</h2>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Predictions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reports</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.user_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 font-semibold">
                              {user.full_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-sm text-gray-500">@{user.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full font-semibold">
                          {user.prediction_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full font-semibold">
                          {user.report_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center gap-3">
                          <button 
                            onClick={() => {
                              setSelectedUser(user)
                              setShowUserModal(true)
                            }}
                            className="text-purple-600 hover:text-purple-900 hover:underline"
                          >
                            View Details
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user.user_id, user.full_name)}
                            className="text-red-600 hover:text-red-900 transition-colors"
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
          </>
        ) : (
          /* Chatbot Knowledge Base Tab */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Upload Section */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                <Upload className="inline w-6 h-6 mr-2" />
                Upload Health Documents
              </h2>
              <p className="text-gray-600 mb-6">
                Add diabetes and health-related documents, URLs, or text to enhance the chatbot's knowledge base.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <button
                  onClick={() => document.getElementById('file-upload')?.click()}
                  disabled={uploading}
                  className="p-6 border-2 border-dashed border-purple-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all disabled:opacity-50"
                >
                  <FileText className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                  <div className="font-semibold text-gray-900">Upload File</div>
                  <div className="text-sm text-gray-500">PDF, TXT, DOC, PPT</div>
                </button>
                <input
                  id="file-upload"
                  type="file"
                  accept=".txt,.pdf,.doc,.docx,.ppt,.pptx,.md"
                  onChange={handleFileUpload}
                  className="hidden"
                />

                <button
                  onClick={handleUrlUpload}
                  disabled={uploading}
                  className="p-6 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all disabled:opacity-50"
                >
                  <Database className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <div className="font-semibold text-gray-900">Add URL</div>
                  <div className="text-sm text-gray-500">Web article or page</div>
                </button>

                <button
                  onClick={handleTextUpload}
                  disabled={uploading}
                  className="p-6 border-2 border-dashed border-green-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all disabled:opacity-50"
                >
                  <FileText className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <div className="font-semibold text-gray-900">Add Text</div>
                  <div className="text-sm text-gray-500">Custom content</div>
                </button>
              </div>

              {uploading && (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2">Uploading...</p>
                </div>
              )}
            </div>

            {/* Documents List */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Knowledge Base Documents</h2>
              <div className="space-y-3">
                {documents.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No documents uploaded yet</p>
                ) : (
                  documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-purple-600" />
                        <div>
                          <div className="font-semibold text-gray-900">
                            {doc.filename || doc.url || 'Document'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {doc.type} • {(doc.size / 1024).toFixed(1)} KB • {new Date(doc.uploaded_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* User Details Modal */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowUserModal(false)}>
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">User Details</h2>
              <button onClick={() => setShowUserModal(false)} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Full Name</p>
                  <p className="text-lg font-semibold text-gray-900">{selectedUser.full_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Username</p>
                  <p className="text-lg font-semibold text-gray-900">@{selectedUser.username}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="text-lg font-semibold text-gray-900">{selectedUser.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">User ID</p>
                  <p className="text-lg font-semibold text-gray-900 text-xs">{selectedUser.user_id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Joined Date</p>
                  <p className="text-lg font-semibold text-gray-900">{new Date(selectedUser.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Account Age</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {Math.floor((Date.now() - new Date(selectedUser.created_at).getTime()) / (1000 * 60 * 60 * 24))} days
                  </p>
                </div>
              </div>
              <div className="border-t pt-4 mt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Activity Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-600 font-medium">Total Predictions</p>
                    <p className="text-3xl font-bold text-green-700">{selectedUser.prediction_count}</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-purple-600 font-medium">Reports Generated</p>
                    <p className="text-3xl font-bold text-purple-700">{selectedUser.report_count}</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <button 
                onClick={() => setShowUserModal(false)}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

