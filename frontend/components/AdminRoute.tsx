"use client"

import React from 'react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Shield, Lock } from 'lucide-react'

interface AdminRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
  requireAdmin?: boolean
}

export function AdminRoute({ children, requireAuth = false, requireAdmin = false }: AdminRouteProps) {
  const { user, isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    )
  }

  // Giriş yapılması gerekiyor
  if (requireAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        {/* Top Banner */}
        <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">
          TÜM ÜYELERİ KARGO BEDAVA
        </div>

        {/* Navigation */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex-shrink-0">
                <Link href="/" className="text-2xl font-bold text-slate-800">
                  Sidrex
                </Link>
              </div>

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

              <div className="flex items-center space-x-4">
                <Button asChild variant="outline" size="sm">
                  <Link href="/yonetim">Giriş Yap</Link>
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Access Denied Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <Lock className="mx-auto h-16 w-16 text-gray-400 mb-6" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Giriş Yapmanız Gerekiyor</h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Bu sayfaya erişim için lütfen giriş yapın. Hesabınız yoksa yöneticinizle iletişime geçin.
            </p>
            <div className="space-y-4">
              <Button asChild size="lg" className="bg-emerald-600 hover:bg-emerald-700">
                <Link href="/yonetim">
                  <Lock className="mr-2 h-5 w-5" />
                  Giriş Yap
                </Link>
              </Button>
              <div>
                <Button asChild variant="outline" size="lg">
                  <Link href="/">Ana Sayfaya Dön</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Admin yetkisi gerekiyor
  if (requireAdmin && isAuthenticated && !isAdmin) {
    return (
      <div className="min-h-screen bg-white">
        {/* Top Banner */}
        <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">
          TÜM ÜYELERİ KARGO BEDAVA
        </div>

        {/* Navigation */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex-shrink-0">
                <Link href="/" className="text-2xl font-bold text-slate-800">
                  Sidrex
                </Link>
              </div>

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

              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Hoş geldin, {user?.first_name || user?.username}
                </span>
                <Button asChild variant="outline" size="sm">
                  <Link href="/yonetim">Yönetim Paneli</Link>
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Access Denied Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <Shield className="mx-auto h-16 w-16 text-red-400 mb-6" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Admin Değilsiniz</h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Bu sayfaya erişim için admin yetkilerine sahip olmanız gerekiyor. 
              Lütfen admin hesabınızla giriş yapın veya yöneticinizle iletişime geçin.
            </p>
            <div className="space-y-4">
              <Button asChild size="lg" className="bg-emerald-600 hover:bg-emerald-700">
                <Link href="/yonetim">
                  <Lock className="mr-2 h-5 w-5" />
                  Admin Girişi Yap
                </Link>
              </Button>
              <div>
                <Button asChild variant="outline" size="lg">
                  <Link href="/">Ana Sayfaya Dön</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Tüm kontroller geçildi, içeriği göster
  return <>{children}</>
} 