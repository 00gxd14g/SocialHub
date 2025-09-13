import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Heart, 
  Eye, 
  Share2,
  Calendar,
  Download
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('30days')

  // Sample data for charts
  const engagementData = [
    { name: 'Jan', engagement: 400 },
    { name: 'Feb', engagement: 300 },
    { name: 'Mar', engagement: 600 },
    { name: 'Apr', engagement: 800 },
    { name: 'May', engagement: 500 },
    { name: 'Jun', engagement: 900 },
    { name: 'Jul', engagement: 700 }
  ]

  const platformData = [
    { name: 'Facebook', engagement: 30 },
    { name: 'Instagram', engagement: 70 },
    { name: 'Twitter', engagement: 50 },
    { name: 'LinkedIn', engagement: 90 }
  ]

  const metrics = [
    {
      title: 'Total Reach',
      value: '12,456',
      change: '+12%',
      trend: 'up',
      icon: Eye,
      color: 'text-blue-500'
    },
    {
      title: 'Total Engagement',
      value: '3,210',
      change: '+8%',
      trend: 'up',
      icon: Heart,
      color: 'text-red-500'
    },
    {
      title: 'Follower Growth',
      value: '+567',
      change: '+15%',
      trend: 'up',
      icon: Users,
      color: 'text-green-500'
    },
    {
      title: 'Avg. Engagement Rate',
      value: '8.5%',
      change: '-2%',
      trend: 'down',
      icon: Share2,
      color: 'text-purple-500'
    }
  ]

  const insights = [
    {
      title: 'Top Performing Post',
      description: '"Our new product launch is here! 🚀"',
      link: 'View Post'
    },
    {
      title: 'Most Active Follower',
      description: '@JaneDoe',
      link: 'View Profile'
    },
    {
      title: 'Top Content Type',
      description: 'Video',
      link: 'See more'
    }
  ]

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Analytics Overview</h1>
            <p className="mt-2 text-sm text-gray-400">Track your social media performance across all platforms.</p>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              className="border-gray-600 text-gray-300 hover:bg-gray-700"
            >
              <Calendar size={16} className="mr-2" />
              Last 30 Days
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Download size={16} className="mr-2" />
              Export Report
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-600">
          <nav className="-mb-px flex space-x-8">
            <a className="border-blue-500 text-blue-400 whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium">
              Overview
            </a>
            <a className="border-transparent text-gray-400 hover:border-gray-500 hover:text-white whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium">
              Posts
            </a>
            <a className="border-transparent text-gray-400 hover:border-gray-500 hover:text-white whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium">
              Stories
            </a>
            <a className="border-transparent text-gray-400 hover:border-gray-500 hover:text-white whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium">
              Audience
            </a>
          </nav>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {metrics.map((metric, index) => {
          const Icon = metric.icon
          const TrendIcon = metric.trend === 'up' ? TrendingUp : TrendingDown
          const trendColor = metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
          
          return (
            <Card key={index} className="bg-gray-800 border-gray-700">
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={metric.color} size={20} />
                  <p className="text-sm font-medium text-gray-400">{metric.title}</p>
                </div>
                <p className="text-3xl font-semibold text-white">{metric.value}</p>
                <div className={`flex items-center gap-1 mt-1 ${trendColor}`}>
                  <TrendIcon size={16} />
                  <span className="text-sm font-semibold">{metric.change}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-8">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-lg font-medium text-white">Engagement Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={engagementData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#F9FAFB'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-lg font-medium text-white">Engagement by Platform</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={platformData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#F9FAFB'
                    }} 
                  />
                  <Bar dataKey="engagement" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Audience Insights */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Audience Insights</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {insights.map((insight, index) => (
            <Card key={index} className="bg-gray-800 border-gray-700">
              <CardContent className="p-5">
                <p className="text-sm font-medium text-gray-400">{insight.title}</p>
                <p className="mt-2 text-base font-medium text-white truncate">{insight.description}</p>
                <a className="mt-2 text-sm font-medium text-blue-400 hover:underline" href="#">
                  {insight.link}
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Analytics

