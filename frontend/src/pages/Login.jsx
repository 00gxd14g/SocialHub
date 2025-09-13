import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Eye, EyeOff } from 'lucide-react'

const Login = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // For demo purposes, accept any email/password
      if (formData.email && formData.password) {
        localStorage.setItem('isAuthenticated', 'true')
        navigate('/')
      } else {
        setError('Email ve şifre gereklidir')
      }
    } catch (err) {
      setError('Giriş başarısız oldu')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-800 flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 sm:px-6 lg:px-10 py-4 border-b border-gray-600">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center">
            <span className="text-white font-bold">S</span>
          </div>
          <h1 className="text-white text-xl font-bold">SocialHub</h1>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          <a className="text-gray-300 hover:text-white text-sm font-medium transition-colors" href="#">Features</a>
          <a className="text-gray-300 hover:text-white text-sm font-medium transition-colors" href="#">Pricing</a>
          <a className="text-gray-300 hover:text-white text-sm font-medium transition-colors" href="#">Support</a>
        </nav>
        <div className="flex items-center gap-4">
          <Link 
            to="/register"
            className="hidden sm:inline-flex items-center justify-center rounded-md text-sm font-semibold text-white ring-1 ring-inset ring-gray-500 hover:bg-gray-700 h-9 px-4 transition-colors"
          >
            Sign Up
          </Link>
          <Button className="bg-blue-600 hover:bg-blue-700">
            Get Started
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-white">Welcome back</h2>
            <p className="mt-2 text-sm text-gray-400">Manage all your social accounts in one place.</p>
          </div>

          <Card className="bg-gray-700 border-gray-600 shadow-2xl">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="email" className="block text-sm font-medium text-gray-200">
                      Email address
                    </Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="you@example.com"
                      className="mt-1 bg-gray-900 border-gray-500 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="password" className="block text-sm font-medium text-gray-200">
                      Password
                    </Label>
                    <div className="relative mt-1">
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        autoComplete="current-password"
                        required
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder="••••••••"
                        className="bg-gray-900 border-gray-500 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500 pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-200"
                      >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="rememberMe"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onCheckedChange={(checked) => 
                        setFormData(prev => ({ ...prev, rememberMe: checked }))
                      }
                      className="border-gray-500 data-[state=checked]:bg-blue-600"
                    />
                    <Label htmlFor="rememberMe" className="text-sm text-gray-200">
                      Remember me
                    </Label>
                  </div>
                  <div className="text-sm">
                    <a className="font-medium text-blue-400 hover:text-blue-300" href="#">
                      Forgot your password?
                    </a>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-700 transition-all duration-300"
                >
                  {isLoading ? 'Signing in...' : 'Log in'}
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="text-center text-sm text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-blue-400 hover:text-blue-300">
              Sign up
            </Link>
          </p>
        </div>
      </main>
    </div>
  )
}

export default Login

