import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.PROD ? '' : 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth APIs
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/api/login', { username, password }),
  
  register: (data: { full_name: string; email: string; username: string; password: string }) =>
    api.post('/api/register', data),
  
  logout: () => api.get('/logout'),
  
  getSession: () => api.get('/api/session')
}

// Prediction APIs
export const predictionAPI = {
  predict: (data: {
    name: string
    age: number
    sex: string
    contact: string
    address: string
    pregnancies: number
    glucose: number
    bloodPressure: number
    skinThickness: number
    insulin: number
    bmi: number
    diabetesPedigreeFunction: number
  }) => api.post('/predict', data),
  
  getUserPredictions: () => api.get('/user/predictions'),
  
  getPredictionById: (id: string) => api.get(`/user/prediction/${id}`)
}

// Dashboard APIs
export const dashboardAPI = {
  getUserStats: () => api.get('/api/user/statistics'),
  
  getUserHistory: () => api.get('/api/user/history')
}

// Report APIs
export const reportAPI = {
  generateReport: (predictionId: string) =>
    api.post('/api/generate_report', { prediction_id: predictionId }),
  
  downloadReport: (reportId: string) =>
    api.get(`/download_report/${reportId}`, { responseType: 'blob' })
}

export default api
