import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Session from './pages/Session'
import { checkHealth } from './services/api'

function App() {
  const [isHealthy, setIsHealthy] = useState(true)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAppHealth = async () => {
      try {
        await checkHealth()
        setIsHealthy(true)
      } catch (error) {
        console.error('Health check failed:', error)
        setIsHealthy(false)
      } finally {
        setLoading(false)
      }
    }

    checkAppHealth()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    )
  }

  if (!isHealthy) {
    return (
      <div className="flex items-center justify-center h-screen bg-red-50">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-red-600 mb-4">Service Unavailable</h1>
          <p className="text-gray-600">The backend server is not responding. Please check that it is running.</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/session/:sessionId" element={<Session />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
