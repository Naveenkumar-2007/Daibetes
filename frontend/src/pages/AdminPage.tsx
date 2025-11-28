import { useState, useEffect } from 'react'
import { Users, FileText, TrendingUp, Activity, Upload, Database, Trash2, RefreshCw, FileUp, Link as LinkIcon, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { useNavigate, Link } from 'react-router-dom'
import { adminAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'

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
  const { user, logout } = useAuth()
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
  const [training, setTraining] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadType, setUploadType] = useState<'file' | 'url' | 'text'>('file')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [textTitle, setTextTitle] = useState('')

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

    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf', 'text/markdown', 
                          'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(txt|pdf|md|doc|docx)$/i)) {
      alert('Please upload a valid document (TXT, PDF, MD, DOC, DOCX)')
      return
    }

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
        alert(`✅ ${data.message}\n\n📊 Total documents: ${data.total_documents}`)
        fetchDocuments()
        setShowUploadModal(false)
      } else {
        alert('❌ Upload failed: ' + data.error)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('❌ Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleUrlUpload = async () => {
    if (!urlInput.trim()) {
      alert('Please enter a URL')
      return
    }

    // Basic URL validation
    try {
      new URL(urlInput)
    } catch {
      alert('Please enter a valid URL')
      return
    }

    setUploading(true)
    try {
      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ url: urlInput })
      })
      const data = await response.json()
      if (data.success) {
        alert(`✅ ${data.message}\n\n📊 Total documents: ${data.total_documents}`)
        fetchDocuments()
        setShowUploadModal(false)
        setUrlInput('')
      } else {
        alert('❌ Failed: ' + data.error)
      }
    } catch (error) {
      alert('❌ Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleTextUpload = async () => {
    if (!textInput.trim() || !textTitle.trim()) {
      alert('Please enter both title and text content')
      return
    }

    setUploading(true)
    try {
      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ text: textInput, title: textTitle })
      })
      const data = await response.json()
      if (data.success) {
        alert(`✅ ${data.message}\n\n📊 Total documents: ${data.total_documents}`)
        fetchDocuments()
        setShowUploadModal(false)
        setTextInput('')
        setTextTitle('')
      } else {
        alert('❌ Failed: ' + data.error)
      }
    } catch (error) {
      alert('❌ Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleTrainChatbot = async () => {
    if (!confirm('Train chatbot with all uploaded documents?\n\nThis will reload the knowledge base from the database.')) {
      return
    }

    setTraining(true)
    try {
      const response = await fetch('/api/admin/chatbot/train', {
        method: 'POST',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        alert(`✅ ${data.message}`)
        fetchDocuments()
      } else {
        alert('❌ Training failed: ' + data.error)
      }
    } catch (error) {
      alert('❌ Training failed. Please try again.')
    } finally {
      setTraining(false)
    }
  }

  const handleDeleteDocument = async (docId: string, filename: string) => {
    if (!confirm(`Delete "${filename}"?\n\nThis will remove the document and retrain the chatbot.`)) {
      return
    }

    try {
      const response = await fetch(`/api/admin/chatbot/documents/${docId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        alert(`✅ ${data.message}`)
        fetchDocuments()
      } else {
        alert('❌ Delete failed: ' + data.error)
      }
    } catch (error) {
      alert('❌ Delete failed. Please try again.')
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

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString()
    } catch {
      return dateString
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

          {/* Tabs */}
          <div className="flex gap-4 mt-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('users')}
              className={`pb-3 px-2 font-medium text-sm transition-colors relative ${
                activeTab === 'users'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Users ({users.length})
            </button>
            <button
              onClick={() => setActiveTab('chatbot')}
              className={`pb-3 px-2 font-medium text-sm transition-colors relative ${
                activeTab === 'chatbot'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Database className="w-4 h-4 inline mr-2" />
              AI Chatbot ({documents.length})
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 pb-24">
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
                            <button
                              onClick={() => handleDeleteUser(user.user_id, user.username, user.full_name)}
                              className="inline-flex items-center gap-1 px-2 sm:px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 active:bg-red-100 rounded-lg transition-colors touch-target"
                              title="Delete user"
                            >
                              <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                              <span className="hidden sm:inline">Delete</span>
                            </button>
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

        {activeTab === 'chatbot' && (
          <>
            {/* Chatbot Controls */}
            <div className="card mb-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">AI Chatbot Knowledge Base</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Upload documents to train your AI health assistant • {documents.length} documents loaded
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setShowUploadModal(true)}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    Upload Document
                  </button>
                  <button
                    onClick={handleTrainChatbot}
                    disabled={training || documents.length === 0}
                    className="btn-secondary flex items-center gap-2 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${training ? 'animate-spin' : ''}`} />
                    {training ? 'Training...' : 'Train Chatbot'}
                  </button>
                </div>
              </div>
            </div>

            {/* Documents List */}
            <div className="space-y-3">
              {documents.length === 0 ? (
                <div className="card text-center py-12">
                  <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No documents uploaded</h3>
                  <p className="text-gray-600 mb-4">Upload medical documents, articles, or FAQs to train your AI chatbot</p>
                  <button
                    onClick={() => setShowUploadModal(true)}
                    className="btn-primary inline-flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    Upload First Document
                  </button>
                </div>
              ) : (
                documents.map((doc) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <FileText className="w-5 h-5 text-blue-600 flex-shrink-0" />
                          <h3 className="font-medium text-gray-900 truncate">{doc.filename || 'Untitled'}</h3>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            doc.type === 'file' ? 'bg-blue-100 text-blue-700' :
                            doc.type === 'url' ? 'bg-green-100 text-green-700' :
                            'bg-purple-100 text-purple-700'
                          }`}>
                            {doc.type.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                          <span>📊 {formatFileSize(doc.size)}</span>
                          <span>📅 {formatDate(doc.uploaded_at)}</span>
                          {doc.url && (
                            <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                              <LinkIcon className="w-3 h-3" />
                              View source
                            </a>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id, doc.filename || 'this document')}
                        className="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </>
        )}
      </main>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => !uploading && setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Upload Document</h2>
                  <button
                    onClick={() => !uploading && setShowUploadModal(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    disabled={uploading}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Upload Type Selector */}
                <div className="flex gap-2 mb-6">
                  <button
                    onClick={() => setUploadType('file')}
                    className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
                      uploadType === 'file'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <FileUp className="w-4 h-4 inline mr-2" />
                    File
                  </button>
                  <button
                    onClick={() => setUploadType('url')}
                    className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
                      uploadType === 'url'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <LinkIcon className="w-4 h-4 inline mr-2" />
                    URL
                  </button>
                  <button
                    onClick={() => setUploadType('text')}
                    className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
                      uploadType === 'text'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <FileText className="w-4 h-4 inline mr-2" />
                    Text
                  </button>
                </div>

                {/* Upload Content */}
                {uploadType === 'file' && (
                  <div>
                    <p className="text-sm text-gray-600 mb-4">
                      Upload PDF, TXT, MD, DOC, or DOCX files. The content will be automatically extracted and used to train the chatbot.
                    </p>
                    <label className="block w-full">
                      <input
                        type="file"
                        accept=".txt,.pdf,.md,.doc,.docx"
                        onChange={handleFileUpload}
                        disabled={uploading}
                        className="hidden"
                        id="fileInput"
                      />
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-sm font-medium text-gray-900">
                          {uploading ? 'Uploading and training...' : 'Click to select file'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">TXT, PDF, MD, DOC, DOCX (max 10MB)</p>
                      </div>
                    </label>
                  </div>
                )}

                {uploadType === 'url' && (
                  <div>
                    <p className="text-sm text-gray-600 mb-4">
                      Enter a URL to fetch and extract content. Works best with articles and documentation pages.
                    </p>
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="https://example.com/article"
                      className="input-field mb-4"
                      disabled={uploading}
                    />
                    <button
                      onClick={handleUrlUpload}
                      disabled={uploading || !urlInput.trim()}
                      className="btn-primary w-full disabled:opacity-50"
                    >
                      {uploading ? 'Uploading and training...' : 'Upload URL'}
                    </button>
                  </div>
                )}

                {uploadType === 'text' && (
                  <div>
                    <p className="text-sm text-gray-600 mb-4">
                      Paste or type text content directly. Useful for FAQs, guidelines, or custom knowledge.
                    </p>
                    <input
                      type="text"
                      value={textTitle}
                      onChange={(e) => setTextTitle(e.target.value)}
                      placeholder="Document title..."
                      className="input-field mb-3"
                      disabled={uploading}
                    />
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Paste your text content here..."
                      rows={8}
                      className="input-field mb-4 resize-none"
                      disabled={uploading}
                    />
                    <button
                      onClick={handleTextUpload}
                      disabled={uploading || !textInput.trim() || !textTitle.trim()}
                      className="btn-primary w-full disabled:opacity-50"
                    >
                      {uploading ? 'Uploading and training...' : 'Upload Text'}
                    </button>
                  </div>
                )}

                {uploading && (
                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />
                      <div>
                        <p className="text-sm font-medium text-blue-900">Processing...</p>
                        <p className="text-xs text-blue-700">Uploading and training chatbot automatically</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  )
}
