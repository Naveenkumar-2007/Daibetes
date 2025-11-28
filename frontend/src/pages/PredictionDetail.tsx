import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { User, Activity, FileText, Download, BarChart3, ArrowLeft, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { motion } from 'framer-motion'
import { predictionAPI, reportAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'

// const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

const featureImportance = [
  { name: 'Glucose', value: 90, color: '#3b82f6' },
  { name: 'BMI', value: 65, color: '#10b981' },
  { name: 'Age', value: 45, color: '#f59e0b' },
  { name: 'Insulin', value: 60, color: '#ef4444' },
  { name: 'Blood Pressure', value: 30, color: '#8b5cf6' },
]

export default function PredictionDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [prediction, setPrediction] = useState<any>(null)
  // const [glucoseTrendData, setGlucoseTrendData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [generatingReport, setGeneratingReport] = useState(false)

  useEffect(() => {
    fetchPrediction()
  }, [id])

  const fetchPrediction = async () => {
    try {
      const response = await predictionAPI.getPredictionById(id!)
      if (response.data.success) {
        setPrediction(response.data.prediction)
        
        // Generate glucose trend
        // const glucose = response.data.prediction.features?.Glucose || 110
        // const trend = Array.from({ length: 8 }, (_, i) => ({
        //   time: String(i + 1),
        //   value: Math.round(glucose - 40 + (i * 10) + (Math.random() * 10))
        // }))
        // setGlucoseTrendData(trend)
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
      const response = await reportAPI.generateReport(id!)
      
      if (response.data.success) {
        // Download the report
        const reportResponse = await reportAPI.downloadReport(response.data.report_id)
        
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center" pb-24 lg:pb-8>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!prediction) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center" pb-24 lg:pb-8>
        <div>Prediction not found</div>
      </div>
    )
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50" pb-24 lg:pb-8>
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Glucose', value: prediction.features?.Glucose?.toFixed(1) || 'N/A', unit: 'mg/dL', icon: '🩸' },
            { label: 'BMI', value: prediction.features?.BMI?.toFixed(1) || 'N/A', unit: '', icon: '⚖️' },
            { label: 'Age', value: prediction.features?.Age?.toString() || 'N/A', unit: 'years', icon: '👤' },
            { label: 'Blood Pressure', value: prediction.features?.BloodPressure?.toFixed(0) || 'N/A', unit: 'mm Hg', icon: '❤️' },
            { label: 'Insulin', value: prediction.features?.Insulin?.toFixed(1) || 'N/A', unit: 'μU/mL', icon: '💉' },
            { label: 'Skin Thickness', value: prediction.features?.SkinThickness?.toFixed(1) || 'N/A', unit: 'mm', icon: '📏' },
            { label: 'Pregnancies', value: prediction.features?.Pregnancies?.toString() || 'N/A', unit: '', icon: '👶' },
            { label: 'Diabetes Pedigree', value: prediction.features?.DiabetesPedigreeFunction?.toFixed(3) || 'N/A', unit: '', icon: '🧬' },
          ].map((metric, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-white rounded-xl p-4 shadow-md border border-gray-100 hover:shadow-lg transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-600">{metric.label}</div>
                <span className="text-xl">{metric.icon}</span>
              </div>
              <div className="text-2xl font-extrabold text-gray-900">{metric.value}</div>
              {metric.unit && <div className="text-xs text-gray-500 mt-1">{metric.unit}</div>}
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* All Features Comparison */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Health Metrics Overview
            </h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={[
                    { name: 'Glucose', value: prediction.features?.Glucose || 0, normal: 100, unit: 'mg/dL' },
                    { name: 'BMI', value: prediction.features?.BMI || 0, normal: 25, unit: '' },
                    { name: 'BP', value: prediction.features?.BloodPressure || 0, normal: 80, unit: 'mmHg' },
                    { name: 'Insulin', value: prediction.features?.Insulin || 0, normal: 80, unit: 'μU/mL' },
                    { name: 'Skin', value: prediction.features?.SkinThickness || 0, normal: 20, unit: 'mm' },
                    { name: 'Preg', value: prediction.features?.Pregnancies || 0, normal: 3, unit: '' },
                    { name: 'DPF', value: (prediction.features?.DiabetesPedigreeFunction || 0) * 100, normal: 50, unit: '' },
                    { name: 'Age', value: prediction.features?.Age || 0, normal: 30, unit: 'yrs' },
                  ]}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="name" 
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
                      padding: '8px'
                    }}
                    formatter={(value: any, name: string, props: any) => {
                      return [`${Number(value).toFixed(1)} ${props.payload.unit}`, name === 'value' ? 'Your Value' : 'Normal Range']
                    }}
                  />
                  <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="normal" fill="#10b981" opacity={0.3} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="flex items-center justify-center gap-6 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-600 rounded"></div>
                <span className="text-gray-600">Your Values</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-600 opacity-30 rounded"></div>
                <span className="text-gray-600">Normal Range</span>
              </div>
            </div>
          </motion.div>

          {/* Feature Importance Pie Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Feature Impact Analysis</h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={featureImportance}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {featureImportance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-4 text-sm text-gray-600 text-center">
              Relative importance of each factor in diabetes risk prediction
            </div>
          </motion.div>
        </div>

        {/* Diabetes Risk Gauge - Full Width */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card mt-8"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Diabetes Risk Assessment</h3>
            
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="relative flex items-center justify-center h-64">
              <svg className="w-64 h-64" viewBox="0 0 100 100">
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
                  stroke={prediction.result === 'Diabetic' ? '#ef4444' : '#10b981'}
                  strokeWidth="12"
                  strokeDasharray="251.2"
                  strokeDashoffset={prediction.result === 'Diabetic' ? '62.8' : '188.4'}
                  transform="rotate(-90 50 50)"
                  strokeLinecap="round"
                />
                {/* Needle */}
                <g transform={`rotate(${prediction.result === 'Diabetic' ? '135' : '-45'} 50 50)`}>
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
                  <div className={`text-4xl font-extrabold ${prediction.result === 'Diabetic' ? 'text-red-600' : 'text-green-600'}`}>
                    {prediction.result === 'Diabetic' ? '85%' : '25%'}
                  </div>
                  <div className="text-sm text-gray-600 mt-2">Risk Level</div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${prediction.result === 'Diabetic' ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
                <div className={`text-lg font-bold ${prediction.result === 'Diabetic' ? 'text-red-900' : 'text-green-900'}`}>
                  Prediction: {prediction.result}
                </div>
                <p className={`text-sm ${prediction.result === 'Diabetic' ? 'text-red-700' : 'text-green-700'} mt-2`}>
                  {prediction.result === 'Diabetic' 
                    ? 'The analysis indicates a high risk of diabetes based on your health metrics. Please consult with a healthcare professional for proper evaluation.'
                    : 'The analysis shows a low risk of diabetes. Continue maintaining a healthy lifestyle with regular exercise and balanced diet.'}
                </p>
              </div>

              <div className="flex justify-between text-sm px-4">
                <span className={`font-semibold ${prediction.result !== 'Diabetic' ? 'text-green-600' : 'text-gray-400'}`}>Low Risk</span>
                <span className="text-gray-500">Moderate</span>
                <span className={`font-semibold ${prediction.result === 'Diabetic' ? 'text-red-600' : 'text-gray-400'}`}>High Risk</span>
              </div>
            </div>
          </div>
        </motion.div>

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
            <h3 className="text-xl font-bold text-gray-900 mb-6">Key Risk Factors</h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={featureImportance} 
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" stroke="#6b7280" />
                  <YAxis type="category" dataKey="name" stroke="#6b7280" width={120} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '8px'
                    }}
                    formatter={(value: any) => [`${value}%`, 'Importance']}
                  />
                  <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                    {featureImportance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <p className="text-sm text-gray-600 mt-4 text-center">
              These factors contribute most significantly to your diabetes risk assessment
            </p>
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
    
      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  )
}
