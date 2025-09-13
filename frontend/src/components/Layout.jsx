import { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  Home, 
  Bell, 
  BarChart3, 
  Calendar, 
  Users, 
  Plus,
  Settings,
  User
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  
  const navigation = [
    { name: 'Ana Sayfa', href: '/', icon: Home },
    { name: 'Bildirimler', href: '/notifications', icon: Bell },
    { name: 'Analizler', href: '/analytics', icon: BarChart3 },
    { name: 'Planlayıcı', href: '/scheduler', icon: Calendar },
    { name: 'Hesaplar', href: '/accounts', icon: Users },
  ]

  return (
    <aside className="flex flex-col w-64 bg-gray-900 p-6 shrink-0">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-blue-600 rounded-full w-10 h-10 flex items-center justify-center">
          <span className="text-white font-bold text-lg">S</span>
        </div>
        <h1 className="text-xl font-bold text-white">SocialHub</h1>
      </div>
      
      <nav className="flex flex-col gap-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-md transition-colors duration-200 ${
                isActive
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
      
      <Button 
        onClick={() => window.location.href = '/create-post'}
        className="flex items-center justify-center gap-2 mt-auto bg-blue-600 hover:bg-blue-700 text-white"
      >
        <Plus size={20} />
        <span>Yeni Gönderi</span>
      </Button>
    </aside>
  )
}

const Layout = () => {
  return (
    <div className="relative flex h-screen w-full bg-gray-800 text-white">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

