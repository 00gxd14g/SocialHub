import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { 
  Wand2, 
  Copy, 
  RefreshCw, 
  Hash, 
  TrendingUp,
  FileText,
  Lightbulb,
  BarChart3
} from 'lucide-react'

const AIContentGenerator = () => {
  const [activeTab, setActiveTab] = useState('generate')
  const [loading, setLoading] = useState(false)
  const [generatedContent, setGeneratedContent] = useState('')
  const [hashtags, setHashtags] = useState([])
  const [contentAnalysis, setContentAnalysis] = useState(null)

  const [formData, setFormData] = useState({
    topic: '',
    platform: 'facebook',
    tone: 'professional',
    length: 'medium',
    content: '',
    keywords: '',
    targetAudience: 'general audience',
    wordCount: 800
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const generateContent = async () => {
    if (!formData.topic.trim()) {
      alert('Please enter a topic')
      return
    }

    setLoading(true)
    try {
      // Mock API call - replace with actual API endpoint
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockContent = `🚀 Exciting news about ${formData.topic}! 

In today's digital landscape, ${formData.topic} is becoming increasingly important for businesses and individuals alike. Here are some key insights:

✨ Key benefits include improved efficiency and better user experience
📈 Market trends show significant growth in this area
🎯 Perfect for ${formData.platform} audience

What are your thoughts on ${formData.topic}? Share your experiences in the comments!

#${formData.topic.replace(/\s+/g, '')} #Innovation #Technology #Growth`

      setGeneratedContent(mockContent)
      
      // Generate hashtags
      const mockHashtags = [
        `#${formData.topic.replace(/\s+/g, '')}`,
        '#Innovation',
        '#Technology',
        '#Growth',
        '#Business',
        '#Digital',
        '#Success',
        '#Trending'
      ]
      setHashtags(mockHashtags)

    } catch (error) {
      console.error('Error generating content:', error)
      alert('Failed to generate content. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const generateHashtags = async () => {
    if (!formData.content.trim()) {
      alert('Please enter content to generate hashtags')
      return
    }

    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockHashtags = [
        '#SocialMedia',
        '#ContentCreation',
        '#Marketing',
        '#Engagement',
        '#Digital',
        '#Strategy',
        '#Growth',
        '#Innovation',
        '#Business',
        '#Success'
      ]
      setHashtags(mockHashtags)
    } catch (error) {
      console.error('Error generating hashtags:', error)
      alert('Failed to generate hashtags. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const analyzeContent = async () => {
    if (!formData.content.trim()) {
      alert('Please enter content to analyze')
      return
    }

    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const mockAnalysis = {
        sentiment: 'positive',
        tone: 'professional',
        emotional_impact: 'high',
        engagement_potential: 'high',
        target_audience: 'business professionals',
        recommendations: [
          'Add more visual elements',
          'Include a call-to-action',
          'Use trending hashtags'
        ]
      }
      setContentAnalysis(mockAnalysis)
    } catch (error) {
      console.error('Error analyzing content:', error)
      alert('Failed to analyze content. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const tabs = [
    { id: 'generate', label: 'Generate Content', icon: Wand2 },
    { id: 'hashtags', label: 'Generate Hashtags', icon: Hash },
    { id: 'analyze', label: 'Analyze Content', icon: BarChart3 },
    { id: 'blog', label: 'Blog Generator', icon: FileText },
    { id: 'ideas', label: 'Content Ideas', icon: Lightbulb }
  ]

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AI Content Generator</h1>
        <p className="text-gray-400">Create engaging content with the power of AI</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "outline"}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 ${
                activeTab === tab.id 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </Button>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Wand2 size={20} />
              {tabs.find(t => t.id === activeTab)?.label}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeTab === 'generate' && (
              <>
                <div>
                  <Label htmlFor="topic" className="text-gray-300">Topic</Label>
                  <Input
                    id="topic"
                    placeholder="Enter your topic (e.g., AI in marketing)"
                    value={formData.topic}
                    onChange={(e) => handleInputChange('topic', e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-300">Platform</Label>
                    <Select value={formData.platform} onValueChange={(value) => handleInputChange('platform', value)}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="facebook">Facebook</SelectItem>
                        <SelectItem value="twitter">Twitter</SelectItem>
                        <SelectItem value="instagram">Instagram</SelectItem>
                        <SelectItem value="linkedin">LinkedIn</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label className="text-gray-300">Tone</Label>
                    <Select value={formData.tone} onValueChange={(value) => handleInputChange('tone', value)}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="professional">Professional</SelectItem>
                        <SelectItem value="casual">Casual</SelectItem>
                        <SelectItem value="friendly">Friendly</SelectItem>
                        <SelectItem value="humorous">Humorous</SelectItem>
                        <SelectItem value="inspiring">Inspiring</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label className="text-gray-300">Length</Label>
                  <Select value={formData.length} onValueChange={(value) => handleInputChange('length', value)}>
                    <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-gray-600">
                      <SelectItem value="short">Short</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="long">Long</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={generateContent} 
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Wand2 className="mr-2 h-4 w-4" />
                      Generate Content
                    </>
                  )}
                </Button>
              </>
            )}

            {activeTab === 'hashtags' && (
              <>
                <div>
                  <Label htmlFor="content" className="text-gray-300">Content</Label>
                  <Textarea
                    id="content"
                    placeholder="Enter your content to generate relevant hashtags..."
                    value={formData.content}
                    onChange={(e) => handleInputChange('content', e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white min-h-[120px]"
                  />
                </div>

                <div>
                  <Label className="text-gray-300">Platform</Label>
                  <Select value={formData.platform} onValueChange={(value) => handleInputChange('platform', value)}>
                    <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-gray-600">
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="twitter">Twitter</SelectItem>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={generateHashtags} 
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Hash className="mr-2 h-4 w-4" />
                      Generate Hashtags
                    </>
                  )}
                </Button>
              </>
            )}

            {activeTab === 'analyze' && (
              <>
                <div>
                  <Label htmlFor="analyze-content" className="text-gray-300">Content to Analyze</Label>
                  <Textarea
                    id="analyze-content"
                    placeholder="Enter your content for sentiment and engagement analysis..."
                    value={formData.content}
                    onChange={(e) => handleInputChange('content', e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white min-h-[120px]"
                  />
                </div>

                <Button 
                  onClick={analyzeContent} 
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Analyze Content
                    </>
                  )}
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* Output Panel */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp size={20} />
              Generated Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            {activeTab === 'generate' && generatedContent && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-gray-300">Generated Content</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(generatedContent)}
                      className="border-gray-600 text-gray-300 hover:bg-gray-700"
                    >
                      <Copy size={14} className="mr-1" />
                      Copy
                    </Button>
                  </div>
                  <Textarea
                    value={generatedContent}
                    readOnly
                    className="bg-gray-700 border-gray-600 text-white min-h-[200px]"
                  />
                </div>
                
                <div className="text-sm text-gray-400">
                  Characters: {generatedContent.length} | Words: {generatedContent.split(' ').length}
                </div>
              </div>
            )}

            {(activeTab === 'hashtags' || activeTab === 'generate') && hashtags.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-gray-300">Generated Hashtags</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(hashtags.join(' '))}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <Copy size={14} className="mr-1" />
                    Copy All
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {hashtags.map((hashtag, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="bg-blue-900 text-blue-300 cursor-pointer hover:bg-blue-800"
                      onClick={() => copyToClipboard(hashtag)}
                    >
                      {hashtag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'analyze' && contentAnalysis && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-300">Sentiment</Label>
                    <Badge 
                      variant={contentAnalysis.sentiment === 'positive' ? 'default' : 'secondary'}
                      className={`mt-1 ${
                        contentAnalysis.sentiment === 'positive' 
                          ? 'bg-green-900 text-green-300' 
                          : 'bg-gray-700 text-gray-300'
                      }`}
                    >
                      {contentAnalysis.sentiment}
                    </Badge>
                  </div>
                  
                  <div>
                    <Label className="text-gray-300">Engagement Potential</Label>
                    <Badge 
                      variant="secondary"
                      className={`mt-1 ${
                        contentAnalysis.engagement_potential === 'high'
                          ? 'bg-green-900 text-green-300'
                          : 'bg-yellow-900 text-yellow-300'
                      }`}
                    >
                      {contentAnalysis.engagement_potential}
                    </Badge>
                  </div>
                </div>

                <div>
                  <Label className="text-gray-300">Recommendations</Label>
                  <ul className="mt-2 space-y-1">
                    {contentAnalysis.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-400 flex items-center gap-2">
                        <span className="w-1 h-1 bg-blue-400 rounded-full"></span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {!generatedContent && !hashtags.length && !contentAnalysis && (
              <div className="text-center py-12 text-gray-500">
                <Wand2 size={48} className="mx-auto mb-4 opacity-50" />
                <p>Generate content to see results here</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AIContentGenerator

