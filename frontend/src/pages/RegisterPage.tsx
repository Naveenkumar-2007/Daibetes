import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, Eye, EyeOff } from 'lucide-react'
import { motion } from 'framer-motion'
import { authAPI } from '../lib/api'
import { useAuth } from '../lib/auth'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const navigate = useNavigate()
  const { login } = useAuth()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Client-side validation
    if (!formData.name.trim()) {
      setError('Please enter your full name')
      return
    }
    
    if (!formData.email.trim()) {
      setError('Please enter your email address')
      return
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address')
      return
    }
    
    if (!formData.password) {
      setError('Please enter a password')
      return
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const username = formData.email.split('@')[0].toLowerCase()
      const response = await authAPI.register({
        full_name: formData.name.trim(),
        username: username,
        email: formData.email.toLowerCase().trim(),
        password: formData.password
      })
      
      if (response.data.success) {
        // Auto-login after registration using the email (since login now accepts email)
        await login(formData.email.toLowerCase().trim(), formData.password)
        navigate('/dashboard')
      } else {
        setError(response.data.message || 'Registration failed')
      }
    } catch (err: any) {
      console.error('Registration error:', err)
      const errorMessage = err.response?.data?.message || err.message || 'Registration failed. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // Clear error when user starts typing
    if (error) {
      setError('')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <div className="inline-block bg-blue-100 rounded-full p-4 mb-4">
              <UserPlus className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
            <p className="text-gray-600 mt-2">Join us for better health monitoring</p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input-field pl-10 pr-10"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {formData.password && formData.password.length < 6 && (
                <p className="text-xs text-red-600 mt-1">Password must be at least 6 characters</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input-field pl-10 pr-10"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                <p className="text-xs text-red-600 mt-1">Passwords do not match</p>
              )}
            </div>

            <div className="flex items-start">
              <input type="checkbox" className="w-4 h-4 text-blue-600 border-gray-300 rounded mt-1" required />
              <span className="ml-2 text-sm text-gray-600">
                I agree to the{' '}
                <a href="#" className="text-blue-600 hover:text-blue-700">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-blue-600 hover:text-blue-700">Privacy Policy</a>
              </span>
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-semibold">
                Sign in
              </Link>
            </p>
          </div>

          <div className="mt-8 text-center">
            <Link to="/" className="text-gray-600 hover:text-gray-900 text-sm">
              ← Back to home
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
