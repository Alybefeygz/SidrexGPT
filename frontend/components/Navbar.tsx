"use client"

import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/AuthContext'
import { Search, ShoppingCart, User } from 'lucide-react'

interface NavbarProps {
  currentPage?: 'products' | 'sidrexgpts' | 'yonetim'
}

export function Navbar({ currentPage }: NavbarProps) {
  const { user, isAuthenticated, isAdmin, logout } = useAuth()

  return (
    <>
      {/* Top Banner */}
      <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">
        TÜM ÜYELERİ KARGO BEDAVA
      </div>

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
              <Link 
                href="/" 
                className={currentPage === 'products' 
                  ? "text-emerald-500 hover:text-emerald-600 font-medium" 
                  : "text-slate-700 hover:text-slate-900"
                }
              >
                Ürünlerimiz
              </Link>
              <Link 
                href="/sidrexgpt"
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  currentPage === 'products' ? 'text-black' : 'text-muted-foreground'
                }`}
              >
                SidrexGPT's
              </Link>
              <Link 
                href="/yonetim" 
                className={currentPage === 'yonetim' 
                  ? "text-emerald-500 hover:text-emerald-600 font-medium" 
                  : "text-slate-700 hover:text-slate-900"
                }
              >
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
              
              {/* Giriş/Çıkış butonları ve kullanıcı bilgisi */}
              {isAuthenticated ? (
                <>
                  <div className="text-sm text-gray-600 mr-2">
                    Hoş geldin, <span className="font-medium">{user?.first_name || user?.username}</span>
                  </div>
                  <Button onClick={logout} variant="outline" size="sm">
                    Çıkış Yap
                  </Button>
                </>
              ) : (
                <Button asChild variant="outline" size="sm">
                  <Link href="/yonetim">Giriş Yap</Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>
    </>
  )
} 