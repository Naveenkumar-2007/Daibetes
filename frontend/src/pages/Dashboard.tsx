import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Settings, Brain, TrendingUp, User as UserIcon, Activity, LogOut, Shield } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { dashboardAPI } from '../lib/api'

interface LatestPrediction {
  prediction_id: string
  prediction: number
  probability: number
  patient_name: string
  age: number
  bmi: number
  glucose: number
  blood_pressure: number
  insulin: number
  created_at: string
}

interface AllPrediction {
  prediction_id: string
  patient_name: string
  prediction: number
  probability: number
  risk_level: string
  age: number
  bmi: number
  glucose: number
  blood_pressure: number
  insulin: number
  skin_thickness: number
  pregnancies: number
  dpf: number
  created_at: string
  has_report: boolean
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [latestPrediction, setLatestPrediction] = useState<LatestPrediction | null>(null)
  const [allPredictions, setAllPredictions] = useState<AllPrediction[]>([])
  const [glucoseData, setGlucoseData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    totalPredictions: 0,
    highRiskCount: 0,
    lowRiskCount: 0,
    reportsGenerated: 0
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setError(null)
      // Fetch latest prediction
      const latestResponse = await dashboardAPI.getLatestPrediction()
      if (latestResponse.data.success && latestResponse.data.prediction) {
        setLatestPrediction(latestResponse.data.prediction)
      }

      // Fetch all predictions for comprehensive overview
      const allResponse = await dashboardAPI.getAllPredictions()
      if (allResponse.data.success && allResponse.data.predictions) {
        const predictions = allResponse.data.predictions
        setAllPredictions(predictions)
        
        // Calculate statistics
        const highRisk = predictions.filter((p: AllPrediction) => p.prediction === 1).length
        const lowRisk = predictions.filter((p: AllPrediction) => p.prediction === 0).length
        const withReports = predictions.filter((p: AllPrediction) => p.has_report).length
        
        setStats({
          totalPredictions: predictions.length,
          highRiskCount: highRisk,
          lowRiskCount: lowRisk,
          reportsGenerated: withReports
        })

        // Generate glucose trend from all predictions
        if (predictions.length > 0) {
          const glucoseTrend = predictions.slice(0, 7).reverse().map((p: AllPrediction) => ({
            date: new Date(p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            glucose: p.glucose,
            bmi: p.bmi,
            insulin: p.insulin
          }))
          setGlucoseData(glucoseTrend)
        }
      }
    } catch (error: any) {
      console.error('Error fetching dashboard data:', error)
      setError(error.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => {
              setError(null)
              setLoading(true)
              fetchDashboardData()
            }}
            className="btn-primary w-full"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-extrabold text-blue-900">DASHBOARD</div>
            <div className="flex items-center gap-6">
              <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">Home</Link>
              <Link to="/predict" className="text-gray-700 hover:text-blue-600 transition-colors">Predict</Link>
              <Link to="/settings" className="text-gray-700 hover:text-blue-600 transition-colors">Settings</Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <UserIcon className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-sm font-medium text-gray-700">{user?.username || 'User'}</span>
                <button 
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-red-600 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <aside className="lg:col-span-1 space-y-2">
            <motion.div whileHover={{ x: 4 }}>
              <Link
                to="/dashboard"
                className="w-full flex items-center gap-3 px-6 py-3 rounded-lg transition-all bg-blue-100 text-blue-700 font-semibold"
              >
                <LayoutDashboard className="w-5 h-5" />
                <span>Overview</span>
              </Link>
            </motion.div>

            <motion.div whileHover={{ x: 4 }}>
              <Link
                to="/reports"
                className="w-full flex items-center gap-3 px-6 py-3 rounded-lg transition-all text-gray-700 hover:bg-gray-50"
              >
                <FileText className="w-5 h-5" />
                <span>Reports</span>
              </Link>
            </motion.div>

            <motion.div whileHover={{ x: 4 }}>
              <Link
                to="/settings"
                className="w-full flex items-center gap-3 px-6 py-3 rounded-lg transition-all text-gray-700 hover:bg-gray-50"
              >
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </Link>
            </motion.div>

            {user?.role === 'admin' && (
              <motion.div whileHover={{ x: 4 }}>
                <Link
                  to="/admin"
                  className="w-full flex items-center gap-3 px-6 py-3 rounded-lg transition-all text-purple-700 hover:bg-purple-50 border-t border-gray-200 mt-4 pt-4"
                >
                  <Shield className="w-5 h-5" />
                  <span>Admin</span>
                </Link>
              </motion.div>
            )}
          </aside>

          {/* Main Content */}
          <main className="lg:col-span-3 space-y-6">
            {/* Prediction Cards */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : latestPrediction ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Diabetes Prediction Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card"
                >
                  <div className="text-sm text-gray-600 font-medium mb-2">DIABETES PREDICTION</div>
                  <div className={`text-5xl font-extrabold mb-4 ${latestPrediction.prediction === 1 ? 'text-red-600' : 'text-green-600'}`}>
                    {latestPrediction.prediction === 1 ? 'Positive' : 'Negative'}
                  </div>
                  <div className={`flex items-center gap-2 ${latestPrediction.prediction === 1 ? 'text-red-600' : 'text-green-600'}`}>
                    <Activity className="w-5 h-5" />
                    <span className="font-medium">{latestPrediction.prediction === 1 ? 'High Risk' : 'Low Risk'}</span>
                  </div>
                </motion.div>

                {/* Probability Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="card"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm text-gray-600 font-medium">PROBABILITY</div>
                    <div className="bg-blue-500 text-white rounded-full p-3">
                      <Brain className="w-6 h-6" />
                    </div>
                  </div>
                  <div className="text-5xl font-extrabold text-blue-600">
                    {(latestPrediction.probability * 100).toFixed(0)}%
                  </div>
                  <div className="text-sm text-gray-600 mt-2">Confidence Score</div>
                </motion.div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Predictions Yet</h3>
                <p className="text-gray-600 mb-6">Start by making your first diabetes risk prediction</p>
                <Link to="/predict" className="btn-primary inline-block">
                  Make Prediction
                </Link>
              </div>
            )}

            {/* Statistics Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white"
              >
                <div className="text-sm opacity-90 mb-2">Total Predictions</div>
                <div className="text-4xl font-bold">{stats.totalPredictions}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white"
              >
                <div className="text-sm opacity-90 mb-2">High Risk</div>
                <div className="text-4xl font-bold">{stats.highRiskCount}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white"
              >
                <div className="text-sm opacity-90 mb-2">Low Risk</div>
                <div className="text-4xl font-bold">{stats.lowRiskCount}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.35 }}
                className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white"
              >
                <div className="text-sm opacity-90 mb-2">Reports</div>
                <div className="text-4xl font-bold">{stats.reportsGenerated}</div>
              </motion.div>
            </div>

            {/* Health Metrics Trend Chart */}
            {glucoseData.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="card"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Health Metrics Trend</h3>
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={glucoseData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis 
                        dataKey="date" 
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis 
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'white', 
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          padding: '12px'
                        }}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="glucose" 
                        stroke="#3b82f6" 
                        strokeWidth={3}
                        dot={{ fill: '#3b82f6', r: 4 }}
                        name="Glucose (mg/dL)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="bmi" 
                        stroke="#10b981" 
                        strokeWidth={3}
                        dot={{ fill: '#10b981', r: 4 }}
                        name="BMI"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="insulin" 
                        stroke="#f59e0b" 
                        strokeWidth={3}
                        dot={{ fill: '#f59e0b', r: 4 }}
                        name="Insulin (μU/mL)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>
            )}

            {/* Latest Patient Info */}
            {latestPrediction && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="card"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">LATEST PATIENT INFO</h3>
                  <UserIcon className="w-5 h-5 text-gray-400" />
                </div>
                
                <div className="mb-4">
                  <p className="text-gray-600 text-sm">Patient Name</p>
                  <p className="text-xl font-bold text-gray-900">{latestPrediction.patient_name}</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <span className="text-gray-600 text-sm">Age</span>
                    <div className="text-2xl font-extrabold text-gray-900">{latestPrediction.age}</div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-gray-600 text-sm">BMI</span>
                    <div className="text-2xl font-extrabold text-gray-900">{latestPrediction.bmi?.toFixed(1)}</div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-gray-600 text-sm">Glucose</span>
                    <div className="text-2xl font-extrabold text-gray-900">{latestPrediction.glucose}</div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-gray-600 text-sm">BP</span>
                    <div className="text-2xl font-extrabold text-gray-900">{latestPrediction.blood_pressure}</div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* All Predictions History Table */}
            {allPredictions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="card"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">PREDICTIONS HISTORY</h3>
                  <FileText className="w-5 h-5 text-gray-400" />
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b-2 border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Patient</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Risk</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Glucose</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">BMI</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Report</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {allPredictions.slice(0, 10).map((pred) => (
                        <tr key={pred.prediction_id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {new Date(pred.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">
                            {pred.patient_name}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              pred.prediction === 1 
                                ? 'bg-red-100 text-red-700' 
                                : 'bg-green-100 text-green-700'
                            }`}>
                              {pred.risk_level}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.glucose}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.bmi.toFixed(1)}</td>
                          <td className="px-4 py-3">
                            {pred.has_report ? (
                              <span className="text-green-600 text-sm">✓ Generated</span>
                            ) : (
                              <span className="text-gray-400 text-sm">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <Link 
                              to={`/prediction/${pred.prediction_id}`}
                              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                            >
                              View Details
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {allPredictions.length > 10 && (
                  <div className="mt-4 text-center">
                    <Link 
                      to="/reports" 
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      View All {allPredictions.length} Predictions →
                    </Link>
                  </div>
                )}
              </motion.div>
            )}

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex gap-4"
            >
              <Link 
                to="/predict" 
                className="btn-primary flex items-center gap-2"
              >
                <Activity className="w-5 h-5" />
                New Prediction
              </Link>
              <Link 
                to="/reports" 
                className="btn-secondary flex items-center gap-2"
              >
                <FileText className="w-5 h-5" />
                View History & Reports
              </Link>
              {latestPrediction && (
                <Link 
                  to={`/graphs/${latestPrediction.prediction_id}`} 
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold flex items-center gap-2"
                >
                  <TrendingUp className="w-5 h-5" />
                  View Graphs
                </Link>
              )}
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
