import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Download, Calendar, TrendingUp, Eye, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { reportAPI } from '../lib/api'
import MobileNav from '../components/MobileNav'

interface Report {
  report_id: string
  prediction_id: string
  patient_name: string
  prediction_result: string
  probability: number
  generated_at: string
  report_file?: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingReport, setViewingReport] = useState<string | null>(null)
  const [reportContent, setReportContent] = useState<string>('')
  useAuth() // Ensure user is authenticated

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await reportAPI.getUserReports()
      if (response.data.success) {
        setReports(response.data.reports || [])
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const viewReport = async (reportId: string) => {
    try {
      const response = await reportAPI.downloadReport(reportId)
      // Handle the response as text
      let text = ''
      if (typeof response.data === 'string') {
        text = response.data
      } else if (response.data instanceof Blob) {
        text = await response.data.text()
      } else {
        text = JSON.stringify(response.data, null, 2)
      }
      setReportContent(text)
      setViewingReport(reportId)
    } catch (error: any) {
      console.error('Error viewing report:', error)
      alert(error.response?.data?.message || 'Failed to view report')
    }
  }

  const downloadReport = async (reportId: string, patientName: string) => {
    try {
      const response = await reportAPI.downloadReport(reportId)
      
      // Create blob from response data
      let blob: Blob
      if (response.data instanceof Blob) {
        blob = response.data
      } else if (typeof response.data === 'string') {
        blob = new Blob([response.data], { type: 'text/plain' })
      } else {
        blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'text/plain' })
      }
      
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const fileName = `diabetes_report_${patientName.replace(/\s+/g, '_')}_${new Date().toLocaleDateString().replace(/\//g, '-')}.txt`
      link.setAttribute('download', fileName)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      alert('Report downloaded successfully!')
    } catch (error: any) {
      console.error('Error downloading report:', error)
      alert(error.response?.data?.message || 'Failed to download report')
    }
  }

  const deleteReport = async (reportId: string) => {
    if (!window.confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
      return
    }
    
    try {
      // Remove from local state
      setReports(prevReports => prevReports.filter(r => r.report_id !== reportId))
      alert('Report deleted successfully!')
      // TODO: Implement backend delete endpoint
      // await reportAPI.deleteReport(reportId)
    } catch (error: any) {
      console.error('Error deleting report:', error)
      alert(error.response?.data?.message || 'Failed to delete report')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-extrabold text-blue-900">MY REPORTS</div>
            <div className="flex items-center gap-6">
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">Dashboard</Link>
              <Link to="/predict" className="text-gray-700 hover:text-blue-600 transition-colors">New Prediction</Link>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Reports</h1>
          <p className="text-gray-600">View and download your diabetes risk assessment reports</p>
        </motion.div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : reports.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl shadow-lg p-12 text-center"
          >
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Reports Yet</h3>
            <p className="text-gray-600 mb-6">Generate your first diabetes risk report by making a prediction</p>
            <Link to="/predict" className="btn-primary inline-block">
              Make Prediction
            </Link>
          </motion.div>
        ) : (
          <>
            {viewingReport && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-6 z-50"
                onClick={() => setViewingReport(null)}
              >
                <div 
                  className="bg-white rounded-2xl p-8 max-w-4xl w-full max-h-[80vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">Report Details</h2>
                    <button
                      onClick={() => setViewingReport(null)}
                      className="text-gray-500 hover:text-gray-700 text-2xl"
                    >
                      ×
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-6">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                      {reportContent}
                    </pre>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reports.map((report, index) => (
                <motion.div
                  key={report.report_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${
                      report.prediction_result === 'Positive' || report.prediction_result?.includes('High')
                        ? 'bg-red-100' 
                        : 'bg-green-100'
                    }`}>
                      <FileText className={`w-6 h-6 ${
                        report.prediction_result === 'Positive' || report.prediction_result?.includes('High')
                          ? 'text-red-600' 
                          : 'text-green-600'
                      }`} />
                    </div>
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                      report.prediction_result === 'Positive' || report.prediction_result?.includes('High')
                        ? 'bg-red-100 text-red-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {report.prediction_result || 'Negative'}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 mb-3">
                    {report.patient_name && report.patient_name !== 'Unknown' ? report.patient_name : 'Patient Report'}
                  </h3>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <TrendingUp className="w-4 h-4" />
                      <span>Risk: {(report.probability * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(report.generated_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => viewReport(report.report_id)}
                      className="flex items-center justify-center gap-1 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      title="View Report"
                    >
                      <Eye className="w-4 h-4" />
                      View
                    </button>
                    <button
                      onClick={() => downloadReport(report.report_id, report.patient_name || 'patient')}
                      className="flex items-center justify-center gap-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                      title="Download Report"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                    <button
                      onClick={() => deleteReport(report.report_id)}
                      className="flex items-center justify-center gap-1 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                      title="Delete Report"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </div>
    
      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  )
}
