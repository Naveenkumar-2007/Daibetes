import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Settings, Brain, TrendingUp, User as UserIcon, Activity, LogOut, Shield, Menu, X } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { dashboardAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'

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
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [stats, setStats] = useState({
    totalPredictions: 0,
    highRiskCount: 0,
    lowRiskCount: 0,
    reportsGenerated: 0
  })

  useEffect(() => {
    console.log('Dashboard mounted, user:', user)
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setError(null)
      setLoading(true)
      console.log('Fetching dashboard data...')
      
      // Fetch all predictions first (most important data)
      try {
        const allResponse = await dashboardAPI.getAllPredictions()
        console.log('All predictions response:', allResponse.data)
        
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
            const glucoseTrend = predictions.slice(0, 10).reverse().map((p: AllPrediction) => ({
              date: new Date(p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
              glucose: p.glucose,
              bmi: p.bmi,
              insulin: p.insulin,
              bloodPressure: p.blood_pressure,
              skinThickness: p.skin_thickness,
              pregnancies: p.pregnancies,
              dpf: p.dpf
            }))
            setGlucoseData(glucoseTrend)
            
            // Set latest prediction from the list
            if (predictions.length > 0) {
              setLatestPrediction(predictions[0])
            }
          }
        }
      } catch (err: any) {
        console.error('Error fetching predictions:', err)
        // Only show error if it's critical (not just empty data)
        if (err.response?.status !== 404) {
          setError('Unable to load predictions. Please refresh the page.')
        }
      }
    } catch (error: any) {
      console.error('Dashboard error:', error)
      // Don't show error to user, just log it
      console.error('Error details:', error.message)
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 max-w-md w-full">
          <div className="text-red-500 text-5xl sm:text-6xl mb-4 text-center">⚠️</div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 text-center">Error Loading Dashboard</h2>
          <p className="text-sm sm:text-base text-gray-600 mb-4 text-center">{error}</p>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 pb-20 lg:pb-8">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <Menu className="w-6 h-6" />
              </button>
              <div className="text-xl sm:text-2xl font-extrabold text-blue-900">DASHBOARD</div>
            </div>
            <div className="hidden lg:flex items-center gap-6">
              <Link to="/" className="text-sm text-gray-700 hover:text-blue-600 transition-colors">Home</Link>
              <Link to="/predict" className="text-sm text-gray-700 hover:text-blue-600 transition-colors">Predict</Link>
              <Link to="/settings" className="text-sm text-gray-700 hover:text-blue-600 transition-colors">Settings</Link>
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
            <div className="lg:hidden flex items-center gap-2">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <UserIcon className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
              </div>
              <button 
                onClick={handleLogout}
                className="text-gray-700 hover:text-red-600 transition-colors p-2"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mobile-sidebar lg:hidden"
              onClick={() => setMobileSidebarOpen(false)}
            />
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'tween', duration: 0.3 }}
              className="mobile-menu"
            >
              <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">Menu</h2>
                <button onClick={() => setMobileSidebarOpen(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="p-4 space-y-2">
                <Link
                  to="/dashboard"
                  onClick={() => setMobileSidebarOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-100 text-blue-700 font-semibold"
                >
                  <LayoutDashboard className="w-5 h-5" />
                  <span>Overview</span>
                </Link>
                <Link
                  to="/reports"
                  onClick={() => setMobileSidebarOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  <FileText className="w-5 h-5" />
                  <span>Reports</span>
                </Link>
                <Link
                  to="/settings"
                  onClick={() => setMobileSidebarOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  <Settings className="w-5 h-5" />
                  <span>Settings</span>
                </Link>
                {user?.role === 'admin' && (
                  <Link
                    to="/admin"
                    onClick={() => setMobileSidebarOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-purple-700 hover:bg-purple-50 border-t border-gray-200 mt-4 pt-4"
                  >
                    <Shield className="w-5 h-5" />
                    <span>Admin</span>
                  </Link>
                )}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8">
          {/* Sidebar - Desktop Only */}
          <aside className="hidden lg:block lg:col-span-1 space-y-2">
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
          <main className="lg:col-span-3 space-y-4 sm:space-y-6">
            {/* Prediction Cards */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : latestPrediction ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                {/* Diabetes Prediction Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card"
                >
                  <div className="text-xs sm:text-sm text-gray-600 font-medium mb-2">DIABETES PREDICTION</div>
                  <div className={`text-3xl sm:text-4xl md:text-5xl font-extrabold mb-3 sm:mb-4 ${latestPrediction.prediction === 1 ? 'text-red-600' : 'text-green-600'}`}>
                    {latestPrediction.prediction === 1 ? 'Positive' : 'Negative'}
                  </div>
                  <div className={`flex items-center gap-2 ${latestPrediction.prediction === 1 ? 'text-red-600' : 'text-green-600'}`}>
                    <Activity className="w-4 h-4 sm:w-5 sm:h-5" />
                    <span className="text-sm sm:text-base font-medium">{latestPrediction.prediction === 1 ? 'High Risk' : 'Low Risk'}</span>
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
                    <div className="text-xs sm:text-sm text-gray-600 font-medium">PROBABILITY</div>
                    <div className="bg-blue-500 text-white rounded-full p-2 sm:p-3">
                      <Brain className="w-5 h-5 sm:w-6 sm:h-6" />
                    </div>
                  </div>
                  <div className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-blue-600">
                    {(latestPrediction.probability * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs sm:text-sm text-gray-600 mt-2">Confidence Score</div>
                </motion.div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-8 sm:p-12 text-center">
                <Activity className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">No Predictions Yet</h3>
                <p className="text-sm sm:text-base text-gray-600 mb-6">Start by making your first diabetes risk prediction</p>
                <Link to="/predict" className="btn-primary inline-block">
                  Make Prediction
                </Link>
              </div>
            )}

            {/* Statistics Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg sm:rounded-xl p-4 sm:p-6 text-white"
              >
                <div className="text-xs sm:text-sm opacity-90 mb-1 sm:mb-2">Total Predictions</div>
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold">{stats.totalPredictions}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg sm:rounded-xl p-4 sm:p-6 text-white"
              >
                <div className="text-xs sm:text-sm opacity-90 mb-1 sm:mb-2">High Risk</div>
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold">{stats.highRiskCount}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg sm:rounded-xl p-4 sm:p-6 text-white"
              >
                <div className="text-xs sm:text-sm opacity-90 mb-1 sm:mb-2">Low Risk</div>
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold">{stats.lowRiskCount}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.35 }}
                className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg sm:rounded-xl p-4 sm:p-6 text-white"
              >
                <div className="text-xs sm:text-sm opacity-90 mb-1 sm:mb-2">Reports</div>
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold">{stats.reportsGenerated}</div>
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
                  <h3 className="text-xl font-bold text-gray-900">Health Metrics Trend - All Features</h3>
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                
                <div className="h-96">
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
                        strokeWidth={2}
                        dot={{ fill: '#3b82f6', r: 4 }}
                        name="Glucose (mg/dL)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="bmi" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        dot={{ fill: '#10b981', r: 4 }}
                        name="BMI"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="insulin" 
                        stroke="#f59e0b" 
                        strokeWidth={2}
                        dot={{ fill: '#f59e0b', r: 4 }}
                        name="Insulin (μU/mL)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="bloodPressure" 
                        stroke="#ef4444" 
                        strokeWidth={2}
                        dot={{ fill: '#ef4444', r: 4 }}
                        name="Blood Pressure (mmHg)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="skinThickness" 
                        stroke="#8b5cf6" 
                        strokeWidth={2}
                        dot={{ fill: '#8b5cf6', r: 4 }}
                        name="Skin Thickness (mm)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="pregnancies" 
                        stroke="#ec4899" 
                        strokeWidth={2}
                        dot={{ fill: '#ec4899', r: 4 }}
                        name="Pregnancies"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="dpf" 
                        stroke="#06b6d4" 
                        strokeWidth={2}
                        dot={{ fill: '#06b6d4', r: 4 }}
                        name="Diabetes Pedigree Function"
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
                
                <div className="bg-blue-50 rounded-lg p-4 mb-4">
                  <p className="text-gray-600 text-sm mb-1">Patient Name</p>
                  <p className="text-2xl font-bold text-gray-900">{latestPrediction.patient_name}</p>
                  <div className="mt-3 flex items-center gap-2">
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                      latestPrediction.prediction === 1 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {latestPrediction.prediction === 1 ? 'High Risk' : 'Low Risk'}
                    </span>
                    <span className="text-sm text-gray-600">
                      • {(latestPrediction.probability * 100).toFixed(0)}% Confidence
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Age</span>
                    <div className="text-2xl font-bold text-gray-900">{latestPrediction.age}</div>
                    <span className="text-gray-500 text-xs">years</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">BMI</span>
                    <div className="text-2xl font-bold text-gray-900">{latestPrediction.bmi?.toFixed(1)}</div>
                    <span className="text-gray-500 text-xs">kg/m²</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Glucose</span>
                    <div className="text-2xl font-bold text-gray-900">{latestPrediction.glucose}</div>
                    <span className="text-gray-500 text-xs">mg/dL</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Blood Pressure</span>
                    <div className="text-2xl font-bold text-gray-900">{latestPrediction.blood_pressure}</div>
                    <span className="text-gray-500 text-xs">mmHg</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Insulin</span>
                    <div className="text-2xl font-bold text-gray-900">{latestPrediction.insulin}</div>
                    <span className="text-gray-500 text-xs">μU/mL</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Skin Thickness</span>
                    <div className="text-2xl font-bold text-gray-900">{allPredictions[0]?.skin_thickness || 0}</div>
                    <span className="text-gray-500 text-xs">mm</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">Pregnancies</span>
                    <div className="text-2xl font-bold text-gray-900">{allPredictions[0]?.pregnancies || 0}</div>
                    <span className="text-gray-500 text-xs">count</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <span className="text-gray-600 text-xs">DPF</span>
                    <div className="text-2xl font-bold text-gray-900">{allPredictions[0]?.dpf?.toFixed(3) || '0.000'}</div>
                    <span className="text-gray-500 text-xs">value</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    <strong>Overall Assessment:</strong> {latestPrediction.prediction === 1 
                      ? 'This patient shows elevated diabetes risk factors. Immediate medical consultation and lifestyle modifications are recommended.' 
                      : 'This patient shows normal diabetes risk levels. Continue maintaining a healthy lifestyle and regular check-ups.'}
                  </p>
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
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Insulin</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">BP</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Skin</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Preg</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">DPF</th>
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
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.insulin}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.blood_pressure}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.skin_thickness}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.pregnancies}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{pred.dpf.toFixed(3)}</td>
                          <td className="px-4 py-3 flex gap-2">
                            <Link 
                              to={`/prediction/${pred.prediction_id}`}
                              className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                            >
                              Details
                            </Link>
                            <Link 
                              to={`/graphs/${pred.prediction_id}`}
                              className="text-purple-600 hover:text-purple-700 text-xs font-medium"
                            >
                              Graphs
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

      {/* Mobile Bottom Navigation */}
      <MobileNav />
    </div>
  )
}
