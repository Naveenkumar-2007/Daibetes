import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Activity, User, Save, ArrowLeft, Download, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'
import { predictionAPI, reportAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'

export default function PredictPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const [generatingReport, setGeneratingReport] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    age: '',
    sex: 'Male',
    contact: '',
    address: '',
    pregnancies: '',
    glucose: '',
    bloodPressure: '',
    skinThickness: '',
    insulin: '',
    bmi: '',
    diabetesPedigreeFunction: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const payload = {
        name: formData.name,
        age: parseInt(formData.age),
        sex: formData.sex,
        contact: formData.contact,
        address: formData.address,
        pregnancies: parseFloat(formData.pregnancies),
        glucose: parseFloat(formData.glucose),
        bloodPressure: parseFloat(formData.bloodPressure),
        skinThickness: parseFloat(formData.skinThickness),
        insulin: parseFloat(formData.insulin),
        bmi: parseFloat(formData.bmi),
        diabetesPedigreeFunction: parseFloat(formData.diabetesPedigreeFunction)
      }

      const response = await predictionAPI.predict(payload)
      
      if (response.data.success) {
        setResult(response.data)
      } else {
        setError(response.data.error || 'Prediction failed')
      }
    } catch (err: any) {
      console.error('Prediction error:', err)
      if (err.response?.status === 401) {
        setError('Please log in first to make predictions.')
      } else {
        setError(err.response?.data?.error || err.message || 'Failed to make prediction. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50" pb-24 lg:pb-8>
        <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="text-2xl font-extrabold text-blue-900">Prediction Result</div>
              <Link to="/dashboard" className="btn-secondary">Back to Dashboard</Link>
            </div>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto px-6 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="text-center mb-8">
              <div className={`inline-block w-24 h-24 rounded-full ${result.risk_level === 'high' ? 'bg-red-100' : 'bg-green-100'} flex items-center justify-center mb-4`}>
                <Activity className={`w-12 h-12 ${result.risk_level === 'high' ? 'text-red-600' : 'text-green-600'}`} />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">{result.prediction}</h2>
              <p className={`text-xl font-semibold ${result.risk_level === 'high' ? 'text-red-600' : 'text-green-600'}`}>
                Confidence: {result.confidence}%
              </p>
            </div>

            <div className="bg-blue-50 rounded-xl p-6 mb-6">
              <h3 className="font-bold text-gray-900 mb-2">Recommendation:</h3>
              <p className="text-gray-700">{result.recommendation}</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Glucose</div>
                <div className="text-xl font-bold text-gray-900">{result.medical_data?.Glucose}</div>
                <div className="text-xs text-gray-500">mg/dL</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">BMI</div>
                <div className="text-xl font-bold text-gray-900">{result.medical_data?.BMI}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Age</div>
                <div className="text-xl font-bold text-gray-900">{result.patient_info?.age}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Blood Pressure</div>
                <div className="text-xl font-bold text-gray-900">{result.medical_data?.['Blood Pressure']}</div>
                <div className="text-xs text-gray-500">mmHg</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setResult(null)}
                className="btn-primary flex items-center justify-center gap-2"
              >
                <Activity className="w-5 h-5" />
                New Prediction
              </button>
              <button
                onClick={async () => {
                  setGeneratingReport(true)
                  try {
                    const predId = result.firebase_id || result.prediction_id
                    if (!predId) {
                      alert('Prediction ID not found')
                      return
                    }

                    // Generate and download report
                    const reportResponse = await reportAPI.generateReportWithData({
                      prediction_id: predId,
                      patient_info: result.patient_info,
                      prediction: result.risk_level === 'high' ? 1 : 0,
                      probability: result.confidence / 100,
                      risk_level: result.risk_level || 'unknown',
                      confidence: result.confidence || 85,
                      medical_data: {
                        'Glucose': result.medical_data?.Glucose,
                        'Blood Pressure': result.medical_data?.['Blood Pressure'],
                        'BMI': result.medical_data?.BMI,
                        'Insulin': result.medical_data?.Insulin,
                        'Skin Thickness': result.medical_data?.['Skin Thickness'],
                        'Pregnancies': result.medical_data?.Pregnancies,
                        'Diabetes Pedigree Function': result.medical_data?.['Diabetes Pedigree Function']
                      }
                    })
                    
                    if (reportResponse.data.success && reportResponse.data.report_file) {
                      // Download the report file
                      const downloadResponse = await reportAPI.downloadReportFile(reportResponse.data.report_file)
                      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]))
                      const link = document.createElement('a')
                      link.href = url
                      link.setAttribute('download', reportResponse.data.report_file)
                      document.body.appendChild(link)
                      link.click()
                      link.remove()
                      alert('Report downloaded successfully!')
                    } else {
                      alert('Report generated but download link not available')
                    }
                  } catch (error: any) {
                    console.error('Error generating report:', error)
                    alert(error.response?.data?.error || 'Failed to generate report. Please ensure Groq API is configured.')
                  } finally {
                    setGeneratingReport(false)
                  }
                }}
                disabled={generatingReport}
                className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-green-800 transition-all font-semibold flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg"
              >
                <Download className="w-5 h-5" />
                {generatingReport ? 'Generating Report...' : 'Download Report'}
              </button>
              <button
                onClick={() => {
                  const predId = result.firebase_id || result.prediction_id
                  if (predId) {
                    navigate(`/graphs/${predId}`)
                  } else {
                    alert('Prediction ID not found')
                  }
                }}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold flex items-center gap-2"
              >
                <BarChart3 className="w-5 h-5" />
                View Graphs
              </button>
              <Link to="/dashboard" className="btn-secondary flex items-center gap-2">
                View Dashboard
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50" pb-24 lg:pb-8>
      {/* Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-extrabold text-blue-900">Diabetes Prediction</div>
            <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 flex items-center gap-2">
              <ArrowLeft className="w-5 h-5" />
              Back
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Patient Information & Medical Tests</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Patient Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-blue-600" />
                Patient Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Age *</label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="45"
                    min="1"
                    max="120"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sex *</label>
                  <select
                    name="sex"
                    value={formData.sex}
                    onChange={handleChange}
                    className="input-field"
                    required
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Number *</label>
                  <input
                    type="tel"
                    name="contact"
                    value={formData.contact}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="1234567890"
                    pattern="[0-9]{10}"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="Street, City, State"
                    rows={2}
                  />
                </div>
              </div>
            </div>

            {/* Medical Tests */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                Medical Test Results
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pregnancies *
                    <span className="text-gray-500 text-xs ml-1">(0-20)</span>
                  </label>
                  <input
                    type="number"
                    name="pregnancies"
                    value={formData.pregnancies}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="0"
                    min="0"
                    max="20"
                    step="1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Glucose Level * <span className="text-gray-500 text-xs">(mg/dL, 1-300)</span>
                  </label>
                  <input
                    type="number"
                    name="glucose"
                    value={formData.glucose}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="125"
                    min="1"
                    max="300"
                    step="0.1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Blood Pressure * <span className="text-gray-500 text-xs">(mmHg, 1-200)</span>
                  </label>
                  <input
                    type="number"
                    name="bloodPressure"
                    value={formData.bloodPressure}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="80"
                    min="1"
                    max="200"
                    step="0.1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Skin Thickness * <span className="text-gray-500 text-xs">(mm, 0-100)</span>
                  </label>
                  <input
                    type="number"
                    name="skinThickness"
                    value={formData.skinThickness}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="20"
                    min="0"
                    max="100"
                    step="0.1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Insulin * <span className="text-gray-500 text-xs">(μU/mL, 0-900)</span>
                  </label>
                  <input
                    type="number"
                    name="insulin"
                    value={formData.insulin}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="80"
                    min="0"
                    max="900"
                    step="0.1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    BMI * <span className="text-gray-500 text-xs">(10-70)</span>
                  </label>
                  <input
                    type="number"
                    name="bmi"
                    value={formData.bmi}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="31.2"
                    min="10"
                    max="70"
                    step="0.1"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Diabetes Pedigree Function * <span className="text-gray-500 text-xs">(0-3)</span>
                  </label>
                  <input
                    type="number"
                    name="diabetesPedigreeFunction"
                    value={formData.diabetesPedigreeFunction}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="0.5"
                    min="0"
                    max="3"
                    step="0.001"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <Link to="/dashboard" className="btn-secondary">
                Cancel
              </Link>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Get Prediction
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    
      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  )
}
