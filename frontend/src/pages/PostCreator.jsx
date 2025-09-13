import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import AIContentGenerator from '../components/AIContentGenerator'
import { 
  Image, 
  Smile, 
  Hash, 
  Calendar, 
  Send,
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  Wand2
} from 'lucide-react'

const PostCreator = () => {
  const [postContent, setPostContent] = useState('')
  const [showAIGenerator, setShowAIGenerator] = useState(false)
  const [selectedPlatforms, setSelectedPlatforms] = useState({
    twitter: true,
    facebook: false,
    instagram: false,
    linkedin: false
  })

  const platforms = [
    {
      id: 'twitter',
      name: 'Twitter',
      icon: Twitter,
      color: 'border-blue-500',
      bgColor: 'bg-blue-500/10'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'border-blue-600',
      bgColor: 'bg-blue-600/10'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'border-pink-500',
      bgColor: 'bg-pink-500/10'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      color: 'border-blue-700',
      bgColor: 'bg-blue-700/10'
    }
  ]

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => ({
      ...prev,
      [platformId]: !prev[platformId]
    }))
  }

  const handlePost = () => {
    console.log('Posting:', { content: postContent, platforms: selectedPlatforms })
    // Here you would integrate with your backend API
  }

  const handleSchedule = () => {
    console.log('Scheduling:', { content: postContent, platforms: selectedPlatforms })
    // Here you would open a date/time picker and schedule the post
  }

  if (showAIGenerator) {
    return (
      <div className="p-8">
        <div className="mb-4">
          <Button 
            variant="outline" 
            onClick={() => setShowAIGenerator(false)}
            className="border-gray-600 text-gray-300 hover:bg-gray-700"
          >
            ← Back to Post Creator
          </Button>
        </div>
        <AIContentGenerator />
      </div>
    )
  }

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-4xl font-bold tracking-tight text-white">Create a post</h2>
        <p className="text-gray-400 mt-2">Craft your message and share it with the world across your connected accounts.</p>
      </header>

      <div className="max-w-4xl mx-auto space-y-8">
        {/* Post Creation Card */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">U</span>
              </div>
              <div className="flex-1">
                <Textarea
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                  placeholder="What's on your mind?"
                  className="bg-transparent border-0 focus:ring-0 text-lg placeholder-gray-500 resize-none min-h-[120px] text-white"
                />
              </div>
            </div>

            <div className="mt-4 flex justify-between items-center border-t border-gray-700 pt-4">
              <div className="flex gap-2 text-gray-400">
                <Button variant="ghost" size="sm" className="p-2 rounded-full hover:bg-gray-700 hover:text-white">
                  <Image size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="p-2 rounded-full hover:bg-gray-700 hover:text-white">
                  <Smile size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="p-2 rounded-full hover:bg-gray-700 hover:text-white">
                  <Hash size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="p-2 rounded-full hover:bg-gray-700 hover:text-white">
                  <Calendar size={20} />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowAIGenerator(true)}
                  className="p-2 rounded-full hover:bg-purple-700 hover:text-purple-300 text-purple-400"
                >
                  <Wand2 size={20} />
                </Button>
              </div>

              <div className="flex items-center gap-4">
                <Button 
                  variant="outline" 
                  onClick={handleSchedule}
                  className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
                >
                  Schedule
                </Button>
                <Button 
                  onClick={handlePost}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Send size={16} className="mr-2" />
                  Post
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Platform Selection */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-xl font-semibold text-white">Post to</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {platforms.map((platform) => {
                const Icon = platform.icon
                const isSelected = selectedPlatforms[platform.id]
                
                return (
                  <div
                    key={platform.id}
                    onClick={() => handlePlatformToggle(platform.id)}
                    className={`flex items-center gap-3 p-4 rounded-md border-2 cursor-pointer transition-all ${
                      isSelected 
                        ? `${platform.color} ${platform.bgColor}` 
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    <Icon size={24} className={isSelected ? 'text-white' : 'text-gray-400'} />
                    <span className={`font-medium ${isSelected ? 'text-white' : 'text-gray-400'}`}>
                      {platform.name}
                    </span>
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => handlePlatformToggle(platform.id)}
                      className="ml-auto"
                    />
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Character Count and Tips */}
        <div className="flex justify-between items-center text-sm text-gray-400">
          <div>
            <span className={postContent.length > 280 ? 'text-red-400' : 'text-gray-400'}>
              {postContent.length}/280 characters
            </span>
          </div>
          <div className="flex gap-4">
            <span>💡 Tip: Use hashtags to increase reach</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PostCreator

