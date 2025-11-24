import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { motion } from 'framer-motion'
import { TrendingUp, Activity, AlertCircle, Download, ArrowLeft } from 'lucide-react'
import { predictionAPI } from '../lib/api'

interface PredictionData {
  prediction_id: string
  patient_name: string
  prediction: number
  probability: number
  features: {
    Pregnancies: number
    Glucose: number
    BloodPressure: number
    SkinThickness: number
    Insulin: number
    BMI: number
    DiabetesPedigreeFunction: number
    Age: number
  }
}

export default function GraphsPage() {
  const { predictionId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<PredictionData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPredictionData()
  }, [predictionId])

  const fetchPredictionData = async () => {
    try {
      const response = await predictionAPI.getPredictionById(predictionId!)
      if (response.data.success) {
        setData(response.data.prediction)
      }
    } catch (error) {
      console.error('Error fetching prediction data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Prediction Not Found</h2>
          <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  // Prepare comparison data
  const normalRanges = {
    Glucose: 100,
    BloodPressure: 80,
    BMI: 24.9,
    Insulin: 166
  }

  const comparisonData = [
    {
      parameter: 'Glucose',
      'Your Value': data.features.Glucose,
      'Normal Range': normalRanges.Glucose,
      unit: 'mg/dL'
    },
    {
      parameter: 'Blood Pressure',
      'Your Value': data.features.BloodPressure,
      'Normal Range': normalRanges.BloodPressure,
      unit: 'mmHg'
    },
    {
      parameter: 'BMI',
      'Your Value': data.features.BMI,
      'Normal Range': normalRanges.BMI,
      unit: 'kg/m²'
    },
    {
      parameter: 'Insulin',
      'Your Value': data.features.Insulin,
      'Normal Range': normalRanges.Insulin,
      unit: 'μU/mL'
    }
  ]

  // Radar chart data for all features
  const radarData = [
    {
      parameter: 'Glucose',
      value: (data.features.Glucose / 200) * 100,
      fullMark: 100
    },
    {
      parameter: 'BP',
      value: (data.features.BloodPressure / 150) * 100,
      fullMark: 100
    },
    {
      parameter: 'BMI',
      value: (data.features.BMI / 50) * 100,
      fullMark: 100
    },
    {
      parameter: 'Insulin',
      value: (data.features.Insulin / 500) * 100,
      fullMark: 100
    },
    {
      parameter: 'Skin Thickness',
      value: (data.features.SkinThickness / 100) * 100,
      fullMark: 100
    },
    {
      parameter: 'Age',
      value: (data.features.Age / 100) * 100,
      fullMark: 100
    }
  ]

  // Feature importance
  const featureImportance = [
    { feature: 'Glucose', importance: 85 },
    { feature: 'BMI', importance: 75 },
    { feature: 'Age', importance: 65 },
    { feature: 'Insulin', importance: 60 },
    { feature: 'BP', importance: 55 },
    { feature: 'Pregnancies', importance: 45 },
    { feature: 'Skin Thickness', importance: 40 },
    { feature: 'DPF', importance: 50 }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate(`/prediction/${predictionId}`)}
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                <ArrowLeft className="w-5 h-5" />
                Back
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="text-2xl font-extrabold text-blue-900">HEALTH ANALYSIS</div>
            </div>
            <div className="flex items-center gap-6">
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">Overview</Link>
              <Link to={`/prediction/${predictionId}`} className="text-gray-700 hover:text-blue-600 transition-colors">Prediction Details</Link>
              <Link to="/reports" className="text-gray-700 hover:text-blue-600 transition-colors">Reports</Link>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Comprehensive Health Analysis</h1>
          <p className="text-gray-600">Patient: {data.patient_name}</p>
        </motion.div>

        {/* Risk Assessment Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`mb-8 rounded-2xl shadow-lg p-8 ${
            data.prediction === 1 ? 'bg-gradient-to-r from-red-500 to-pink-500' : 'bg-gradient-to-r from-green-500 to-emerald-500'
          }`}
        >
          <div className="text-white">
            <h2 className="text-2xl font-bold mb-2">
              Diabetes Risk: {data.prediction === 1 ? 'Positive' : 'Negative'}
            </h2>
            <p className="text-xl">Probability: {(data.probability * 100).toFixed(1)}%</p>
          </div>
        </motion.div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Comparison Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Your Values vs Normal Range
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="parameter" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Your Value" fill="#3b82f6" />
                <Bar dataKey="Normal Range" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Radar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-6 h-6 text-purple-600" />
              Health Parameters Overview
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="parameter" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Your Values" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Feature Importance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4">Feature Importance in Prediction</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={featureImportance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="feature" type="category" />
                <Tooltip />
                <Bar dataKey="importance" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Detailed Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4">Detailed Metrics</h3>
            <div className="space-y-4">
              {Object.entries(data.features).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center border-b pb-2">
                  <span className="text-gray-700 font-medium">{key}</span>
                  <span className="text-gray-900 font-semibold">{value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex gap-4"
        >
          <Link
            to={`/prediction/${predictionId}`}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-center"
          >
            View Full Report
          </Link>
          <button className="flex items-center gap-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold">
            <Download className="w-5 h-5" />
            Download Analysis
          </button>
        </motion.div>
      </div>
    </div>
  )
}
