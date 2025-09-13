import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Facebook, 
  Instagram, 
  Twitter, 
  Linkedin,
  Settings,
  Bot,
  FolderOpen,
  Plus,
  Check,
  X
} from 'lucide-react'

const Accounts = () => {
  const [connectedAccounts, setConnectedAccounts] = useState([
    {
      id: 1,
      platform: 'Twitter',
      username: '@socialhub_demo',
      followers: '12.5K',
      status: 'connected',
      icon: Twitter,
      color: 'bg-blue-500'
    },
    {
      id: 2,
      platform: 'Instagram',
      username: '@socialhub.demo',
      followers: '8.2K',
      status: 'connected',
      icon: Instagram,
      color: 'bg-pink-500'
    }
  ])

  const availableIntegrations = [
    {
      id: 'facebook',
      name: 'Facebook',
      description: 'Manage your posts and interactions.',
      icon: Facebook,
      color: 'bg-blue-600'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      description: 'Professional networking and content.',
      icon: Linkedin,
      color: 'bg-blue-700'
    },
    {
      id: 'mcp',
      name: 'MCP',
      description: 'Manage your projects and tasks.',
      icon: FolderOpen,
      color: 'bg-gray-600'
    },
    {
      id: 'ai',
      name: 'AI Service',
      description: 'Integrate AI into your workflow.',
      icon: Bot,
      color: 'bg-purple-600'
    }
  ]

  const handleConnect = (integrationId) => {
    console.log('Connecting to:', integrationId)
    // Here you would implement the OAuth flow for each platform
  }

  const handleDisconnect = (accountId) => {
    setConnectedAccounts(prev => prev.filter(account => account.id !== accountId))
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Connect your accounts
        </h1>
        <p className="mt-4 text-lg text-gray-400">
          Connect your social media accounts and other services like MCP and AI to manage everything from one place.
        </p>
      </div>

      {/* Connected Accounts */}
      {connectedAccounts.length > 0 && (
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Connected Accounts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {connectedAccounts.map((account) => {
              const Icon = account.icon
              return (
                <Card key={account.id} className="bg-gray-800 border-gray-700">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-md ${account.color} text-white`}>
                          <Icon size={24} />
                        </div>
                        <div>
                          <h3 className="text-base font-medium text-white">{account.platform}</h3>
                          <p className="text-sm text-gray-400">{account.username}</p>
                          <p className="text-sm text-gray-500">{account.followers} followers</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="bg-green-900 text-green-300">
                          <Check size={12} className="mr-1" />
                          Connected
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisconnect(account.id)}
                          className="text-gray-400 hover:text-red-400"
                        >
                          <X size={16} />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}

      {/* Available Integrations */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Available Integrations</h2>
        <div className="space-y-4">
          {availableIntegrations.map((integration) => {
            const Icon = integration.icon
            return (
              <Card key={integration.id} className="bg-gray-800 border-gray-700 hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-md ${integration.color} text-white`}>
                      <Icon size={24} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-base font-medium text-white">{integration.name}</h3>
                      <p className="text-sm text-gray-400">{integration.description}</p>
                    </div>
                    <Button 
                      onClick={() => handleConnect(integration.id)}
                      className="bg-gray-700 hover:bg-gray-600 text-white"
                    >
                      <Plus size={16} className="mr-2" />
                      Connect
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Action Button */}
      <div className="mt-12 flex justify-center">
        <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg">
          Done
        </Button>
      </div>

      {/* Help Section */}
      <div className="mt-12 text-center">
        <Card className="bg-gray-800 border-gray-700 max-w-2xl mx-auto">
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-white mb-2">Need Help?</h3>
            <p className="text-gray-400 mb-4">
              Having trouble connecting your accounts? Check our integration guide or contact support.
            </p>
            <div className="flex justify-center gap-4">
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-700">
                View Guide
              </Button>
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-700">
                Contact Support
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Accounts

