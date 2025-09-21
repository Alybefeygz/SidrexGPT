"use client"

import { Search, ShoppingCart, User } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"

export default function YonetimPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { user, isAuthenticated, isAdmin, login, logout, getUserPermissions } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await login({
        username: username,
        password: password
      })

      if (result.success) {
        // Login başarılı, sayfa otomatik olarak güncellenir
        setUsername('')
        setPassword('')
      } else {
        setError(result.error || 'Giriş yapılırken bir hata oluştu.')
      }
    } catch (err: any) {
      console.error('Login error:', err)
      setError('Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.')
    } finally {
      setLoading(false)
    }
  }

  // If user is authenticated, show dashboard based on user role
  if (isAuthenticated) {
    if (!isAdmin) {
      // Normal user dashboard - only Robot Management access
      return (
        <div className="min-h-screen bg-white">
          {/* Top Banner */}
          <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">TÜM ÜYELERİ KARGO BEDAVA</div>

          {/* Navigation */}
          <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                {/* Logo */}
                <div className="flex-shrink-0">
                  <Link href="/" className="text-2xl font-bold text-slate-800">
                    Sidrex
                  </Link>
                </div>

                {/* Navigation Links */}
                <nav className="hidden md:flex space-x-8">
                  <Link href="/" className="text-slate-700 hover:text-slate-900">
                    Ürünlerimiz
                  </Link>
                  <Link href="/sidrexgpt" className="text-slate-700 hover:text-slate-900">
                    SidrexGPT's
                  </Link>
                  <Link href="/yonetim" className="text-emerald-500 hover:text-emerald-600 font-medium">
                    Yönetim
                  </Link>
                </nav>

                {/* Right Icons */}
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    Hoş geldin, {user?.first_name || user?.username}
                  </span>
                  <Button variant="ghost" size="icon">
                    <Search className="h-5 w-5" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <User className="h-5 w-5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="relative">
                    <ShoppingCart className="h-5 w-5" />
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      0
                    </span>
                  </Button>
                  <Button onClick={logout} variant="outline" size="sm">
                    Çıkış Yap
                  </Button>
                </div>
              </div>
            </div>
          </header>

          {/* Breadcrumb */}
          <div className="bg-gray-50 py-3">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <nav className="text-sm">
                <Link href="/" className="text-gray-500 hover:text-gray-700">
                  Ana Sayfa
                </Link>
                <span className="mx-2 text-gray-400">{">"}</span>
                <span className="text-gray-900">Kullanıcı Paneli</span>
              </nav>
            </div>
          </div>

          {/* User Dashboard Content */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-8">Kullanıcı Yönetim Paneli</h1>
              
              {/* Permission Warning */}
              {getUserPermissions().warningMessage && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 max-w-2xl mx-auto">
                  <div className="flex items-center">
                    <div className="text-yellow-600 mr-3">⚠️</div>
                    <span className="text-yellow-800">{getUserPermissions().warningMessage}</span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                
                {/* Robots Management - All authenticated users can access */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="text-center">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Robot Yönetimi</h3>
                    <p className="text-gray-600 mb-4">Robot detaylarını görüntüleyin ve PDF dosyalarını yönetin</p>
                    <div className="space-y-2">
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#c0c0c0", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/ana-robot">SidrexGPT Asistanı</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#6d71b6", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/mag4ever">Mag4Ever</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#ffc429", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/imuntus-kids">Imuntus Kids</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#5ca9ed", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/zzen">Zzen</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#B66ECC", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/milk-thistle">Milk Thistle Complex</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#E78EEB", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/repro-womens">Repro Women's Once Daily</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#8FE11A", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/slmx">Slm-X</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#D9E60D", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/olivia">Olivia</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#E07E73", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/lipo-iron">Lipo Iron Complex</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#08966F", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/pro-men">Pro Men's Once Daily</Link>
                      </Button>
                      <Button 
                        asChild 
                        className="w-full hover:opacity-90 transition-opacity" 
                        size="sm" 
                        style={{ backgroundColor: "#FF8616", color: "white", border: "none" }}
                      >
                        <Link href="/sidrexgpt/imuntus">Imuntus</Link>
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Brand Management - For all users */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="text-center">
                    <div className="text-4xl mb-4">🏢</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Marka Yönetimi</h3>
                    <p className="text-gray-600 mb-4">
                      {isAdmin ? 'Marka ayarlarını düzenleyin' : 'Marka bilgilerini görüntüleyin'}
                    </p>
                    <Button asChild className="w-full">
                      <Link href="/brands">
                        {isAdmin ? 'Markaları Yönet' : 'Marka Bilgileri'}
                      </Link>
                    </Button>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      )
    }

    // Admin dashboard
    return (
      <div className="min-h-screen bg-white">
        {/* Top Banner */}
        <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">TÜM ÜYELERİ KARGO BEDAVA</div>

        {/* Navigation */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <div className="flex-shrink-0">
                <Link href="/" className="text-2xl font-bold text-slate-800">
                  Sidrex
                </Link>
              </div>

              {/* Navigation Links */}
              <nav className="hidden md:flex space-x-8">
                <Link href="/" className="text-slate-700 hover:text-slate-900">
                  Ürünlerimiz
                </Link>
                <Link href="/sidrexgpt" className="text-slate-700 hover:text-slate-900">
                  SidrexGPT's
                </Link>
                <Link href="/yonetim" className="text-emerald-500 hover:text-emerald-600 font-medium">
                  Yönetim
                </Link>
              </nav>

              {/* Right Icons */}
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Admin: {user?.first_name || user?.username}
                </span>
                <Button variant="ghost" size="icon">
                  <Search className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" className="relative">
                  <ShoppingCart className="h-5 w-5" />
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    0
                  </span>
                </Button>
                <Button onClick={logout} variant="outline" size="sm">
                  Çıkış Yap
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Breadcrumb */}
        <div className="bg-gray-50 py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="text-sm">
              <Link href="/" className="text-gray-500 hover:text-gray-700">
                Ana Sayfa
              </Link>
              <span className="mx-2 text-gray-400">{">"}</span>
              <span className="text-gray-900">Yönetim Paneli</span>
            </nav>
          </div>
        </div>

        {/* Admin Dashboard Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Yönetim Paneli</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
              
              {/* Robots Management - Left side */}
              <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-center">
                  <div className="text-4xl mb-4">🤖</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Robot Yönetimi</h3>
                  <p className="text-gray-600 mb-4">Robot detaylarını görüntüleyin ve yönetin</p>
                  <div className="space-y-2">
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#c0c0c0", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/ana-robot">SidrexGPT Asistanı</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#6d71b6", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/mag4ever">Mag4Ever</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#ffc429", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/imuntus-kids">Imuntus Kids</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#5ca9ed", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/zzen">Zzen</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#B66ECC", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/milk-thistle">Milk Thistle Complex</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#E78EEB", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/repro-womens">Repro Women's Once Daily</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#8FE11A", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/slmx">Slm-X</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#D9E60D", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/olivia">Olivia</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#E07E73", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/lipo-iron">Lipo Iron Complex</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#08966F", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/pro-men">Pro Men's Once Daily</Link>
                    </Button>
                    <Button 
                      asChild 
                      className="w-full hover:opacity-90 transition-opacity" 
                      size="sm" 
                      style={{ backgroundColor: "#FF8616", color: "white", border: "none" }}
                    >
                      <Link href="/sidrexgpt/imuntus">Imuntus</Link>
                    </Button>
                  </div>
                </div>
              </div>

              {/* Right side - Management Cards Stacked */}
              <div className="space-y-6">
                {/* User Management - Only for Admin users */}
                {isAdmin && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-center">
                      <div className="text-4xl mb-4">👥</div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">Kullanıcı Yönetimi</h3>
                      <p className="text-gray-600 mb-4">Kullanıcı bilgilerini görüntüleyin ve yönetin</p>
                      <Button asChild className="w-full">
                        <Link href="/users">Kullanıcıları Yönet</Link>
                      </Button>
                    </div>
                  </div>
                )}

                {/* Brand Management - Only for Admin users */}
                {isAdmin && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-center">
                      <div className="text-4xl mb-4">🏢</div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">Marka Yönetimi</h3>
                      <p className="text-gray-600 mb-4">Marka ayarlarını düzenleyin</p>
                      <Button asChild className="w-full">
                        <Link href="/brands">Markaları Yönet</Link>
                      </Button>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>
      </div>
    )
  }

  // Login form
  return (
    <div className="min-h-screen bg-white">
      {/* Top Banner */}
      <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">TÜM ÜYELERİ KARGO BEDAVA</div>

      {/* Navigation */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link href="/" className="text-2xl font-bold text-slate-800">
                Sidrex
              </Link>
            </div>

            {/* Navigation Links */}
            <nav className="hidden md:flex space-x-8">
              <Link href="/" className="text-slate-700 hover:text-slate-900">
                Ürünlerimiz
              </Link>
              <Link href="/sidrexgpt" className="text-slate-700 hover:text-slate-900">
                SidrexGPT's
              </Link>
              <Link href="/yonetim" className="text-emerald-500 hover:text-emerald-600 font-medium">
                Yönetim
              </Link>
            </nav>

            {/* Right Icons */}
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="icon">
                <Search className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="relative">
                <ShoppingCart className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  0
                </span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="bg-gray-50 py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="text-sm">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              Ana Sayfa
            </Link>
            <span className="mx-2 text-gray-400">{">"}</span>
            <span className="text-gray-900">Yönetim</span>
          </nav>
        </div>
      </div>

      {/* Login Form */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="min-h-[500px] flex items-center justify-center">
          <div className="w-full max-w-md">
            <div className="bg-white shadow-xl rounded-lg px-8 py-10 border border-gray-200">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900">Admin Girişi</h2>
                <p className="text-gray-600 mt-2">Yönetim paneline erişim için giriş yapın</p>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}
                
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                    Kullanıcı Adı veya E-posta
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="admin kullanıcı adı"
                    disabled={loading}
                  />
                </div>
                
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Şifre
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="••••••••"
                    disabled={loading}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded"
                      disabled={loading}
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                      Beni hatırla
                    </label>
                  </div>
                  
                  <div className="text-sm">
                    <a href="#" className="font-medium text-emerald-600 hover:text-emerald-500">
                      Şifremi unuttum?
                    </a>
                  </div>
                </div>
                
                <div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Giriş yapılıyor...
                      </div>
                    ) : (
                      'Admin Girişi Yap'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 