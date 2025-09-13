import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import PostCreator from './pages/PostCreator'
import Analytics from './pages/Analytics'
import Accounts from './pages/Accounts'
import './App.css'

// Simple auth check - in a real app this would be more sophisticated
const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated
    const authStatus = localStorage.getItem('isAuthenticated')
    setIsAuthenticated(authStatus === 'true')
    setIsLoading(false)
  }, [])

  return { isAuthenticated, isLoading }
}

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-800 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="create-post" element={<PostCreator />} />
          <Route path="accounts" element={<Accounts />} />
          <Route path="notifications" element={<div className="p-8 text-white">Notifications page coming soon...</div>} />
          <Route path="scheduler" element={<div className="p-8 text-white">Scheduler page coming soon...</div>} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
