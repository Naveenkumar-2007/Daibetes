import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { User, Activity, FileText, Download, BarChart3, ArrowLeft } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { motion } from 'framer-motion'
import axios from 'axios'

const featureImportance = [
  { name: 'Glucose', value: 90 },
  { name: 'BMI', value: 65 },
  { name: 'Age', value: 45 },
  { name: 'Blood Pressure', value: 30 },
]

export default function PredictionDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [prediction, setPrediction] = useState<any>(null)
  const [glucoseTrendData, setGlucoseTrendData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [generatingReport, setGeneratingReport] = useState(false)

  useEffect(() => {
    fetchPrediction()
  }, [id])

  const fetchPrediction = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/user/prediction/${id}`, {
        withCredentials: true
      })
      if (response.data.success) {
        setPrediction(response.data.prediction)
        
        // Generate glucose trend
        const glucose = response.data.prediction.features?.Glucose || 110
        const trend = Array.from({ length: 8 }, (_, i) => ({
          time: String(i + 1),
          value: Math.round(glucose - 40 + (i * 10) + (Math.random() * 10))
        }))
        setGlucoseTrendData(trend)
      }
    } catch (error) {
      console.error('Error fetching prediction:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    try {
      const response = await axios.post('http://localhost:5000/api/generate_report', {
        prediction_id: id
      }, {
        withCredentials: true
      })
      
      if (response.data.success) {
        // Download the report
        const reportResponse = await axios.get(`http://localhost:5000/download_report/${response.data.report_id}`, {
          withCredentials: true,
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([reportResponse.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `diabetes_report_${id}.txt`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report')
    } finally {
      setGeneratingReport(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!prediction) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div>Prediction not found</div>
      </div>
    )
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Dashboard
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="text-2xl font-extrabold text-blue-900">Diabetes Prediction</div>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">Overview</Link>
              <Link to="/reports" className="text-gray-700 hover:text-blue-600 transition-colors">Reports</Link>
              <button className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Health Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {[
            { label: 'Glucose', value: '125', unit: 'mg/dL' },
            { label: 'BMI', value: '31,2', unit: '' },
            { label: 'Age', value: '45', unit: '' },
            { label: 'Age', value: '45', unit: '' },
            { label: 'Blood Pressure', value: '82', unit: 'mm Hg' },
          ].map((metric, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white rounded-xl p-4 shadow-md border border-gray-100"
            >
              <div className="text-sm text-gray-600 mb-2">{metric.label}</div>
              <div className="text-3xl font-extrabold text-gray-900">{metric.value}</div>
              {metric.unit && <div className="text-xs text-gray-500 mt-1">{metric.unit}</div>}
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Glucose Level Over Time */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2 card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Glucose Level Over Time</h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={glucoseTrendData}>
                  <defs>
                    <linearGradient id="colorGlucoseTrend" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#6b7280"
                    label={{ value: 'Time', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    domain={[50, 150]}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '8px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fill="url(#colorGlucoseTrend)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Diabetes Risk Gauge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Diabetes Risk</h3>
            
            <div className="relative flex items-center justify-center h-64">
              <svg className="w-48 h-48" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="12"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="12"
                  strokeDasharray="251.2"
                  strokeDashoffset="62.8"
                  transform="rotate(-90 50 50)"
                  strokeLinecap="round"
                />
                {/* Needle */}
                <g transform="rotate(135 50 50)">
                  <line
                    x1="50"
                    y1="50"
                    x2="50"
                    y2="20"
                    stroke="#1e40af"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                  <circle cx="50" cy="50" r="4" fill="#1e40af" />
                </g>
              </svg>
              
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center mt-8">
                  <div className="text-4xl font-extrabold text-blue-600">87%</div>
                </div>
              </div>
            </div>

            <div className="flex justify-between text-sm text-gray-600 mt-4">
              <div>Low</div>
              <div className="font-semibold text-blue-600">High</div>
              <div>High</div>
            </div>
          </motion.div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          {/* Summary */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Summary</h3>
            
            <div className="flex items-start gap-4">
              <div className="bg-blue-500 rounded-xl p-4 flex-shrink-0">
                <FileText className="w-8 h-8 text-white" />
              </div>
              
              <div className="flex-1">
                <div className="text-lg font-semibold text-gray-900 mb-2">Result:</div>
                <p className="text-gray-600 leading-relaxed">
                  Predicts that the patient is at risk of diabetes based on the input data.
                </p>
              </div>

              <div className="bg-blue-500 rounded-xl p-4 flex-shrink-0">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 4.97 5.89 11.05 6.32 11.49.38.4 1.0.4 1.38 0C13.11 20.05 19 14.97 19 10c0-4.87-3.13-8-7-8zm-1 13.5v-3H8.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5H11v-3h2v3h2.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5H13v3h-2z"/>
                </svg>
              </div>
            </div>
          </motion.div>

          {/* Feature Importance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Feature Importance</h3>
            
            <div className="space-y-4">
              {featureImportance.map((feature, idx) => (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-700 font-medium">{feature.name}</span>
                    <span className="text-gray-600 text-sm">{feature.value}%</span>
                  </div>
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${feature.value}%` }}
                      transition={{ delay: 0.7 + idx * 0.1, duration: 0.8 }}
                      className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex flex-wrap gap-4 mt-8"
        >
          <Link to="/predict" className="btn-primary flex items-center gap-2">
            <Activity className="w-5 h-5" />
            New Prediction
          </Link>
          <button 
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold flex items-center gap-2 disabled:opacity-50"
          >
            <Download className="w-5 h-5" />
            {generatingReport ? 'Generating...' : 'Download Report'}
          </button>
          <Link 
            to={`/graphs/${id}`}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold flex items-center gap-2"
          >
            <BarChart3 className="w-5 h-5" />
            View Graphs
          </Link>
        </motion.div>
      </div>
    </div>
  )
}
