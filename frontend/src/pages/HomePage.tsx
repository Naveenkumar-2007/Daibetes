import { Link } from 'react-router-dom'
import { Activity, Brain, Shield, TrendingUp, User, Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

export default function HomePage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="text-xl sm:text-2xl font-extrabold text-blue-900">DIABETES AI</div>
              <div className="hidden md:flex gap-6 lg:gap-8 ml-8 lg:ml-12">
                <a href="#home" className="text-sm lg:text-base text-gray-700 hover:text-blue-600 transition-colors">Home</a>
                <a href="#about" className="text-sm lg:text-base text-gray-700 hover:text-blue-600 transition-colors">About</a>
                <a href="#services" className="text-sm lg:text-base text-gray-700 hover:text-blue-600 transition-colors">Services</a>
                <a href="#contact" className="text-sm lg:text-base text-gray-700 hover:text-blue-600 transition-colors">Contact</a>
              </div>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <Link to="/login" className="hidden sm:inline-block text-base lg:text-base text-gray-700 hover:text-blue-600 transition-colors font-medium">Sign in</Link>
              <Link to="/register" className="btn-primary">Get Started</Link>
              <button 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2.5 rounded-lg hover:bg-gray-100 transition-colors touch-target"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="md:hidden border-t border-gray-200 bg-white overflow-hidden"
            >
              <div className="px-4 py-4 space-y-2">
                <a href="#home" className="block py-3 text-base text-gray-700 hover:text-blue-600 transition-colors font-medium" onClick={() => setMobileMenuOpen(false)}>Home</a>
                <a href="#about" className="block py-3 text-base text-gray-700 hover:text-blue-600 transition-colors font-medium" onClick={() => setMobileMenuOpen(false)}>About</a>
                <a href="#services" className="block py-3 text-base text-gray-700 hover:text-blue-600 transition-colors font-medium" onClick={() => setMobileMenuOpen(false)}>Services</a>
                <a href="#contact" className="block py-3 text-base text-gray-700 hover:text-blue-600 transition-colors font-medium" onClick={() => setMobileMenuOpen(false)}>Contact</a>
                <Link to="/login" className="block py-3 text-base text-gray-700 hover:text-blue-600 transition-colors font-medium" onClick={() => setMobileMenuOpen(false)}>Sign in</Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Hero Section */}
      <section id="home" className="max-w-7xl mx-auto px-4 sm:px-6 py-10 sm:py-16 md:py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-4 sm:space-y-6 text-center lg:text-left"
          >
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-blue-900 leading-tight">
              Diabetes Prediction
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-gray-600 leading-relaxed">
              Predict your risk of diabetes with advanced machine learning
            </p>
            
            <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4 justify-center lg:justify-start">
              <Link to="/predict" className="btn-primary inline-flex items-center justify-center gap-2">
                <Activity className="w-4 h-4 sm:w-5 sm:h-5" />
                Check Now
              </Link>
              <a href="#about" className="btn-secondary">Learn More</a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-6 sm:pt-8">
              <div className="bg-white/60 backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 border border-gray-200">
                <div className="text-xs sm:text-sm text-gray-600">Accuracy</div>
                <div className="text-xl sm:text-2xl font-bold text-blue-700">89%</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 border border-gray-200">
                <div className="text-xs sm:text-sm text-gray-600">Patients</div>
                <div className="text-xl sm:text-2xl font-bold text-blue-700">1.2K+</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 border border-gray-200">
                <div className="text-xs sm:text-sm text-gray-600">Model</div>
                <div className="text-base sm:text-lg font-bold text-blue-700">AI</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 border border-gray-200">
                <div className="text-xs sm:text-sm text-gray-600">Secure</div>
                <div className="text-base sm:text-lg font-bold text-blue-700">100%</div>
              </div>
            </div>
          </motion.div>

          {/* Right Content - Medical Graphics */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative hidden lg:block"
          >
            <div className="relative h-[400px] lg:h-[500px] flex items-center justify-center">
              {/* AI Badge */}
              <div className="absolute top-8 right-8 z-10 bg-blue-500 text-white rounded-full w-20 lg:w-24 h-20 lg:h-24 flex items-center justify-center border-4 border-white shadow-xl">
                <div className="text-center">
                  <Brain className="w-6 lg:w-8 h-6 lg:h-8 mx-auto" />
                  <div className="text-lg lg:text-xl font-bold">AI</div>
                </div>
              </div>

              {/* DNA Helix Icon */}
              <div className="absolute left-0 bottom-32">
                <svg className="w-24 lg:w-32 h-24 lg:h-32 text-blue-400" viewBox="0 0 100 100" fill="currentColor">
                  <path d="M30,20 Q40,10 50,20 T70,20" stroke="currentColor" strokeWidth="3" fill="none"/>
                  <path d="M30,40 Q40,30 50,40 T70,40" stroke="currentColor" strokeWidth="3" fill="none"/>
                  <path d="M30,60 Q40,50 50,60 T70,60" stroke="currentColor" strokeWidth="3" fill="none"/>
                  <path d="M30,80 Q40,70 50,80 T70,80" stroke="currentColor" strokeWidth="3" fill="none"/>
                  <circle cx="30" cy="20" r="3"/>
                  <circle cx="50" cy="20" r="3"/>
                  <circle cx="70" cy="20" r="3"/>
                </svg>
              </div>

              {/* Computer Monitor */}
              <div className="relative z-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl p-8 w-full max-w-md shadow-2xl">
                <div className="bg-blue-400 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center gap-4">
                    <Activity className="w-12 h-12 text-blue-900" />
                    <TrendingUp className="w-12 h-12 text-blue-900" />
                  </div>
                  <div className="text-4xl font-bold text-blue-900">DIABETES</div>
                  <div className="flex gap-2">
                    <div className="w-8 h-2 bg-blue-600 rounded-full"></div>
                    <div className="w-12 h-2 bg-blue-600 rounded-full"></div>
                    <div className="w-6 h-2 bg-blue-600 rounded-full"></div>
                  </div>
                </div>
              </div>

              {/* Chart Icon */}
              <div className="absolute left-4 bottom-4">
                <div className="bg-blue-200 rounded-xl p-4 w-40 h-32 relative overflow-hidden shadow-lg">
                  <svg className="w-full h-full" viewBox="0 0 100 100">
                    <polyline 
                      points="0,80 20,70 40,50 60,60 80,30 100,40" 
                      fill="none" 
                      stroke="#3b82f6" 
                      strokeWidth="3"
                    />
                    <polyline 
                      points="0,80 20,70 40,50 60,60 80,30 100,40 100,100 0,100" 
                      fill="rgba(59, 130, 246, 0.2)"
                    />
                  </svg>
                </div>
              </div>

              {/* Doctor Image Placeholder */}
              <div className="absolute right-0 bottom-0 w-72 h-96 bg-gradient-to-br from-blue-100 to-white rounded-3xl overflow-hidden shadow-2xl">
                <div className="absolute inset-0 flex items-center justify-center">
                  <User className="w-32 h-32 text-blue-300" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-blue-500 to-transparent"></div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="about" className="max-w-7xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl font-bold text-center text-blue-900 mb-12">Why Choose Our AI Model?</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card hover:scale-105 transition-transform">
              <Brain className="w-12 h-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">AI-Powered Accuracy</h3>
              <p className="text-gray-600">Advanced machine learning algorithms trained on thousands of patient records for precise predictions.</p>
            </div>

            <div className="card hover:scale-105 transition-transform">
              <Shield className="w-12 h-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Secure & Private</h3>
              <p className="text-gray-600">Your health data is encrypted and never shared. Complete privacy guaranteed.</p>
            </div>

            <div className="card hover:scale-105 transition-transform">
              <Activity className="w-12 h-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Real-Time Analysis</h3>
              <p className="text-gray-600">Instant risk assessment with detailed explanations and health recommendations.</p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section id="services" className="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Check Your Risk?</h2>
          <p className="text-xl text-blue-100 mb-8">Get your diabetes risk assessment in less than 2 minutes</p>
          <Link to="/predict" className="inline-block bg-white text-blue-600 font-bold px-8 py-4 rounded-lg hover:bg-blue-50 transition-all shadow-xl">
            Start Assessment Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold text-blue-900 mb-4">DIABETES AI</h3>
              <p className="text-gray-600">Advanced diabetes risk prediction with AI-powered analysis</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-600">
                <li><a href="#home" className="hover:text-blue-600">Home</a></li>
                <li><a href="#about" className="hover:text-blue-600">About</a></li>
                <li><a href="#services" className="hover:text-blue-600">Services</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-600">
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
                <li>Support</li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-gray-600">
            © {new Date().getFullYear()} Diabetes AI - Built for Healthcare Innovation
          </div>
        </div>
      </footer>
    </div>
  )
}
