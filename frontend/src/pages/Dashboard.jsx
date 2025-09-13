import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TrendingUp, Users, Eye, Heart } from 'lucide-react'

const Dashboard = () => {
  const [scheduledPosts, setScheduledPosts] = useState([
    {
      id: 1,
      content: "Yeni ürün lansmanı duyurusu",
      description: "Heyecan verici yeni ürünümüzü yarın duyuruyoruz! Takipte kalın.",
      scheduledAt: "Yarın, 10:00",
      image: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=200&fit=crop"
    },
    {
      id: 2,
      content: "Haftalık ipuçları",
      description: "Haftalık ipuçları serimizin yeni bölümü yakında yayında!",
      scheduledAt: "2 gün sonra, 14:00",
      image: "https://images.unsplash.com/photo-1553484771-371a605b060b?w=400&h=200&fit=crop"
    }
  ])

  const [analytics, setAnalytics] = useState({
    totalFollowers: 12345,
    engagement: 5678,
    profileVisits: 2345,
    followersGrowth: 5,
    engagementGrowth: 10,
    visitsGrowth: 2
  })

  const [notifications, setNotifications] = useState([
    {
      id: 1,
      user: "Ahmet",
      action: "gönderinizi beğendi",
      time: "1 saat önce",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face"
    },
    {
      id: 2,
      user: "Ayşe",
      action: "gönderinize yorum yaptı",
      time: "2 saat önce",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face"
    },
    {
      id: 3,
      user: "Mehmet",
      action: "sizi takip etmeye başladı",
      time: "3 saat önce",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
    }
  ])

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 text-white">Ana Sayfa</h1>
        <p className="text-gray-400">Sosyal medya hesaplarınızdan gelen son güncellemeler ve önemli bildirimler.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {/* Scheduled Posts Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold mb-4 text-white">Planlanmış Gönderiler</h2>
            <div className="space-y-4">
              {scheduledPosts.map((post) => (
                <Card key={post.id} className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="flex-1">
                        <p className="text-sm text-gray-400">{post.scheduledAt}</p>
                        <p className="font-semibold mt-1 text-white">{post.content}</p>
                        <p className="text-sm text-gray-300 mt-1">{post.description}</p>
                      </div>
                      <div 
                        className="w-32 h-20 bg-cover bg-center rounded-md"
                        style={{ backgroundImage: `url(${post.image})` }}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Analytics Section */}
          <section>
            <h2 className="text-2xl font-bold mb-4 text-white">Analizler</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="text-blue-500" size={20} />
                    <p className="text-gray-400 text-sm font-medium">Toplam Takipçi</p>
                  </div>
                  <p className="text-3xl font-bold text-white">{analytics.totalFollowers.toLocaleString()}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingUp className="text-green-500" size={16} />
                    <p className="text-green-500 text-sm font-semibold">+{analytics.followersGrowth}%</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Heart className="text-red-500" size={20} />
                    <p className="text-gray-400 text-sm font-medium">Gönderi Etkileşimi</p>
                  </div>
                  <p className="text-3xl font-bold text-white">{analytics.engagement.toLocaleString()}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingUp className="text-green-500" size={16} />
                    <p className="text-green-500 text-sm font-semibold">+{analytics.engagementGrowth}%</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="text-purple-500" size={20} />
                    <p className="text-gray-400 text-sm font-medium">Profil Ziyareti</p>
                  </div>
                  <p className="text-3xl font-bold text-white">{analytics.profileVisits.toLocaleString()}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingUp className="text-green-500" size={16} />
                    <p className="text-green-500 text-sm font-semibold">+{analytics.visitsGrowth}%</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </section>
        </div>

        {/* Notifications Sidebar */}
        <div className="lg:col-span-1">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-white">Bildirimler</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                {notifications.map((notification) => (
                  <div key={notification.id} className="flex items-center gap-4">
                    <div 
                      className="w-12 h-12 bg-cover bg-center rounded-full"
                      style={{ backgroundImage: `url(${notification.avatar})` }}
                    />
                    <div>
                      <p className="font-semibold text-white">
                        {notification.user}, {notification.action}
                      </p>
                      <p className="text-sm text-gray-400">{notification.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

