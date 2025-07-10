"use client"

import React, { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
  is_active: boolean
  brand_id: number | null
  brand_name: string | null
  brand_package_type?: string | null
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isAdmin: boolean
  loading: boolean
  login: (credentials: { username: string; password: string }) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  checkAdminAccess: () => boolean
  canEditPDF: () => boolean
  canViewBrandManagement: () => boolean
  canEditBrandManagement: () => boolean
  getUserPermissions: () => {
    canChat: boolean
    canViewRobots: boolean
    canEditPDF: boolean
    canViewBrands: boolean
    canEditBrands: boolean
    canAccessAdmin: boolean
    userType: 'admin' | 'branded_pro' | 'branded_normal' | 'unbranded'
    warningMessage?: string
  }
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  const checkAdminAccess = () => {
    return user?.is_staff || user?.is_superuser || false
  }

  const canEditPDF = () => {
    // Admin her şeyi yapabilir
    if (user?.is_staff || user?.is_superuser) return true
    
    // Markası yoksa yapamaz
    if (!user?.brand_id) return false
    
    // Pro veya Premium paketi varsa yapabilir
    return user?.brand_package_type === 'pro' || user?.brand_package_type === 'premium'
  }

  const canViewBrandManagement = () => {
    // Admin her şeyi görebilir
    if (user?.is_staff || user?.is_superuser) return true
    
    // Markası olan kullanıcılar görebilir
    return !!user?.brand_id
  }

  const canEditBrandManagement = () => {
    // Sadece admin düzenleyebilir
    return user?.is_staff || user?.is_superuser || false
  }

  const getUserPermissions = () => {
    const isAdmin = user?.is_staff || user?.is_superuser
    const hasBrand = !!user?.brand_id
    const packageType = user?.brand_package_type
    const isProOrPremium = packageType === 'pro' || packageType === 'premium'

    if (isAdmin) {
      return {
        canChat: true,
        canViewRobots: true,
        canEditPDF: true,
        canViewBrands: true,
        canEditBrands: true,
        canAccessAdmin: true,
        userType: 'admin' as const
      }
    }

    if (hasBrand) {
      if (isProOrPremium) {
        return {
          canChat: true,
          canViewRobots: true,
          canEditPDF: true,
          canViewBrands: true,
          canEditBrands: false,
          canAccessAdmin: false,
          userType: 'branded_pro' as const
        }
      } else {
        return {
          canChat: true,
          canViewRobots: true,
          canEditPDF: false,
          canViewBrands: true,
          canEditBrands: false,
          canAccessAdmin: false,
          userType: 'branded_normal' as const,
          warningMessage: 'Markanızın paketi PDF düzenleme için yeterli değil'
        }
      }
    }

    // Markasız kullanıcı
    return {
      canChat: true,
      canViewRobots: true,
      canEditPDF: false,
      canViewBrands: false,
      canEditBrands: false,
      canAccessAdmin: false,
      userType: 'unbranded' as const,
      warningMessage: 'Marka ile bir bağınız bulunmamaktadır'
    }
  }

  const login = async (credentials: { username: string; password: string }) => {
    try {
      // Önce CSRF token'ı al
      await api.auth.getCSRFToken();
      // Sonra login isteğini gönder
      await api.auth.login(credentials)
      // After successful login, fetch user details
      const userResponse = await api.auth.getUser()
      setUser(userResponse.data as User)
      return { success: true }
    } catch (error: any) {
      let errorMessage = 'Giriş yapılırken bir hata oluştu.';
      
      // CSRF error handling
      if (error.message && error.message.includes('CSRF')) {
        errorMessage = 'Güvenlik token hatası. Lütfen sayfayı yenileyin.';
      } else if (error.response?.data?.non_field_errors?.[0]) {
        errorMessage = error.response.data.non_field_errors[0];
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const logout = async () => {
    try {
      await api.auth.logout()
    } catch (error) {
      console.error("Logout failed:", error)
    } finally {
      setUser(null)
      router.push('/yonetim')
    }
  }

  useEffect(() => {
    const checkAuth = async () => {
      // No token in localStorage to check.
      // We directly try to fetch the user. 
      // If the HttpOnly cookie is present and valid, this will succeed.
      try {
        const response = await api.auth.getUser()
        setUser(response.data as User)
      } catch (error) {
        // This will fail if the cookie is invalid or not present.
        // It's the expected behavior for a logged-out user.
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAdmin: checkAdminAccess(),
    loading,
    login,
    logout,
    checkAdminAccess,
    canEditPDF,
    canViewBrandManagement,
    canEditBrandManagement,
    getUserPermissions
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 