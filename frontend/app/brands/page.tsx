"use client"

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Navbar } from '@/components/Navbar'
import { AdminRoute } from '@/components/AdminRoute'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Building2, Calendar, BarChart3, Clock, CheckCircle2, AlertCircle, Edit3, Save, RefreshCw } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '../../lib/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
  is_staff: boolean
  is_superuser: boolean
}

interface Brand {
  id: number
  name: string
  total_api_requests: number
  request_limit: number
  paket_turu: string
  paket_turu_display: string
  paket_baslangic_tarihi: string
  paket_bitis_tarihi: string
  remaining_requests: number
  remaining_days: number
  package_status: string
  is_package_expired: boolean
  // Kullanıcı limit bilgileri
  user_limit: number
  active_users_count: number
  user_status: string
  can_add_user: boolean
  active_users: User[]
  created_at: string
  updated_at: string
}

export default function BrandsPage() {
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingBrand, setEditingBrand] = useState<number | null>(null)
  const [updatingBrand, setUpdatingBrand] = useState<number | null>(null)
  const [refreshingBrand, setRefreshingBrand] = useState<number | null>(null)
  const [selectedPackageType, setSelectedPackageType] = useState<string>('')
  const { toast } = useToast()
  const { canEditBrandManagement, isAdmin, getUserPermissions } = useAuth()

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await api.brands.list()
        setBrands(response.data)
      } catch (err: any) {
        console.error('Brands fetch error:', err)
        setError(err.message || 'Marka verileri yüklenirken bir hata oluştu')
        toast({
          title: "Hata",
          description: err.message || 'Marka verileri yüklenirken bir hata oluştu',
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchBrands()
  }, [toast])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getPackageTypeColor = (paketTuru: string) => {
    switch (paketTuru.toLowerCase()) {
      case 'premium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'pro':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'normal':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusColor = (isExpired: boolean) => {
    return isExpired 
      ? 'text-red-600 bg-red-50 border-red-200' 
      : 'text-green-600 bg-green-50 border-green-200'
  }

  const getUserLimitColor = (userStatus: string) => {
    if (userStatus.includes('Kullanıcı Eklenmez')) {
      return 'bg-red-100 text-red-800 border-red-200'
    } else if (userStatus.includes('Limit Dolu')) {
      return 'bg-orange-100 text-orange-800 border-orange-200'
    } else if (userStatus.includes('Kullanılabilir')) {
      return 'bg-green-100 text-green-800 border-green-200'
    } else {
      return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const calculateUsagePercentage = (used: number, limit: number) => {
    return Math.round((used / limit) * 100)
  }

  const startEditingBrand = (brand: Brand) => {
    setEditingBrand(brand.id)
    setSelectedPackageType(brand.paket_turu)
  }

  const cancelEditing = () => {
    setEditingBrand(null)
    setSelectedPackageType('')
  }

  const saveBrandPackageType = async (brandId: number) => {
    try {
      setUpdatingBrand(brandId)
      
      const formData = new FormData()
      formData.append('paket_turu', selectedPackageType)
      
      const response = await api.brands.update(brandId, formData)
      const updatedBrand = response.data
      
      // State'i güncelle
      setBrands(prevBrands => 
        prevBrands.map(brand => 
          brand.id === brandId ? updatedBrand : brand
        )
      )
      
      setEditingBrand(null)
      setSelectedPackageType('')
      
      toast({
        title: "Başarılı!",
        description: `Paket türü ${getPackageTypeDisplayName(selectedPackageType)} olarak güncellendi`,
        variant: "default",
      })
      
    } catch (err: any) {
      console.error('Brand update error:', err)
      toast({
        title: "Hata",
        description: err.message || 'Paket türü güncellenirken bir hata oluştu',
        variant: "destructive",
      })
    } finally {
      setUpdatingBrand(null)
    }
  }

  const getPackageTypeDisplayName = (paketTuru: string) => {
    switch (paketTuru.toLowerCase()) {
      case 'normal':
        return 'Normal Paket'
      case 'pro':
        return 'Pro Paket'
      case 'premium':
        return 'Premium Paket'
      default:
        return paketTuru
    }
  }

  const refreshPackage = async (brandId: number) => {
    try {
      setRefreshingBrand(brandId)
      
      const token = localStorage.getItem('authToken')
      
      // Paket yenileme için change_package endpoint'ini kullan - aynı paket türüyle
      const currentBrand = brands.find(b => b.id === brandId)
      if (!currentBrand) {
        throw new Error('Marka bulunamadı')
      }

      const response = await fetch(`http://127.0.0.1:8000/api/brands/${brandId}/change_package/`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Token ${token}` : '',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paket_turu: currentBrand.paket_turu
        })
      })

            if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Paket yenilenemedi`)
      }

      await response.json()

      // State'i güncelle
      setBrands(prevBrands => 
        prevBrands.map(brand => 
          brand.id === brandId ? {
            ...brand,
            total_api_requests: 0, // API sayacı tamamen sıfırlandı
            remaining_requests: brand.request_limit, // Kalan istek = tam limit (hiç kullanılmamış)
            remaining_days: 30, // Yeni 30 günlük süre
            paket_baslangic_tarihi: new Date().toISOString(),
            paket_bitis_tarihi: new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            package_status: '✅ Aktif',
            is_package_expired: false,
            updated_at: new Date().toISOString()
          } : brand
        )
      )
      
      toast({
        title: "Başarılı!",
        description: `${currentBrand.paket_turu_display} paketi yenilendi! API sayacı sıfırlandı ve 30 günlük yeni süre başladı.`,
        variant: "default",
      })
      
    } catch (err: any) {
      console.error('Package refresh error:', err)
      toast({
        title: "Hata",
        description: err.message || 'Paket yenilenirken bir hata oluştu',
        variant: "destructive",
      })
    } finally {
      setRefreshingBrand(null)
    }
  }

  // Kullanıcı dostu erişim kontrolü
  const permissions = getUserPermissions()
  
  // Markası olmayan kullanıcıların da görebilmesi için özel kontrol
  if (!loading && permissions.userType === 'unbranded' && brands.length === 0) {
    // Markası olmayan kullanıcılar için özel durumu handle et
  }

  return (
    <AdminRoute requireAuth={true} requireAdmin={false}>
      <div className="min-h-screen bg-white">
        <Navbar currentPage="yonetim" />

        {/* Breadcrumb */}
        <div className="bg-gray-50 py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="text-sm">
              <Link href="/" className="text-gray-500 hover:text-gray-700">
                Ana Sayfa
              </Link>
              <span className="mx-2 text-gray-400">{">"}</span>
              <Link href="/yonetim" className="text-gray-500 hover:text-gray-700">
                Yönetim Paneli
              </Link>
              <span className="mx-2 text-gray-400">{">"}</span>
              <span className="text-gray-900">Marka Yönetimi</span>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-8">
            <Building2 className="mx-auto h-12 w-12 text-emerald-600 mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Marka Yönetimi</h1>
            <p className="text-gray-600">
              {isAdmin ? 'Marka bilgilerini ve paket detaylarını görüntüleyip düzenleyin' : 'Marka bilgilerini ve paket detaylarını görüntüleyin'}
            </p>
            
            {/* Permission Info for non-admin users */}
            {!isAdmin && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4 max-w-2xl mx-auto">
                <div className="flex items-center">
                  <div className="text-blue-600 mr-3">ℹ️</div>
                  <span className="text-blue-800">
                    {getUserPermissions().userType === 'unbranded' 
                      ? 'Marka bağlantınız bulunmadığı için sadece genel bilgileri görüntüleyebilirsiniz.'
                      : 'Bu sayfada marka bilgilerini görüntüleyebilirsiniz. Düzenleme yapabilmek için admin yetkisi gereklidir.'
                    }
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-emerald-600 mr-3" />
              <span className="text-gray-600">Marka verileri yükleniyor...</span>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="text-center py-12">
              <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Veri Yükleme Hatası</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={() => window.location.reload()} variant="outline">
                Tekrar Dene
              </Button>
            </div>
          )}

          {/* Brands Grid */}
          {!loading && !error && brands.length > 0 && (
            <div className="grid grid-cols-1 gap-6">
              {brands.map((brand) => (
                <Card key={brand.id} className="shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Building2 className="h-8 w-8 text-emerald-600 mr-3" />
                        <div>
                          <CardTitle className="text-2xl text-gray-900">{brand.name}</CardTitle>
                          <p className="text-sm text-gray-600 mt-1">ID: {brand.id}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getPackageTypeColor(brand.paket_turu)} border`}>
                          {brand.paket_turu_display}
                        </Badge>
                        <Badge className={`${getStatusColor(brand.is_package_expired)} border`}>
                          {brand.is_package_expired ? (
                            <>
                              <AlertCircle className="w-3 h-3 mr-1" />
                              Süresi Dolmuş
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              Aktif
                            </>
                          )}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="p-6">
                    {/* API Usage Statistics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="flex items-center">
                          <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
                          <span className="text-sm font-medium text-blue-900">Toplam İstek</span>
                        </div>
                        <p className="text-2xl font-bold text-blue-600 mt-1">
                          {brand.total_api_requests.toLocaleString()}
                        </p>
                      </div>

                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="flex items-center">
                          <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
                          <span className="text-sm font-medium text-green-900">Kalan İstek</span>
                        </div>
                        <p className="text-2xl font-bold text-green-600 mt-1">
                          {brand.remaining_requests.toLocaleString()}
                        </p>
                      </div>

                      <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="flex items-center">
                          <BarChart3 className="h-5 w-5 text-purple-600 mr-2" />
                          <span className="text-sm font-medium text-purple-900">İstek Limiti</span>
                        </div>
                        <p className="text-2xl font-bold text-purple-600 mt-1">
                          {brand.request_limit.toLocaleString()}
                        </p>
                      </div>

                      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 text-orange-600 mr-2" />
                          <span className="text-sm font-medium text-orange-900">Kalan Gün</span>
                        </div>
                        <p className="text-2xl font-bold text-orange-600 mt-1">
                          {brand.remaining_days}
                        </p>
                      </div>
                    </div>

                    {/* Usage Progress Bar */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">API Kullanım Oranı</span>
                        <span className="text-sm text-gray-600">
                          {calculateUsagePercentage(brand.total_api_requests, brand.request_limit)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-emerald-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ 
                            width: `${calculateUsagePercentage(brand.total_api_requests, brand.request_limit)}%` 
                          }}
                        ></div>
                      </div>
                    </div>

                    {/* User Management Section */}
                    <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200 mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          <svg className="h-5 w-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                          </svg>
                          <span className="text-sm font-medium text-purple-900">Kullanıcı Yönetimi</span>
                        </div>
                        <Badge className={`${getUserLimitColor(brand.user_status)} border text-xs`}>
                          {brand.user_status}
                        </Badge>
                      </div>

                      {/* User Limit Statistics */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                        <div className="bg-white p-3 rounded-lg border border-purple-100">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-xs font-medium text-purple-900">Kullanıcı Limiti</span>
                          </div>
                          <p className="text-lg font-bold text-purple-600 mt-1">
                            {brand.user_limit === 0 ? '🚫 Yok' : `👤 ${brand.user_limit}`}
                          </p>
                        </div>

                        <div className="bg-white p-3 rounded-lg border border-purple-100">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <span className="text-xs font-medium text-green-900">Aktif Kullanıcı</span>
                          </div>
                          <p className="text-lg font-bold text-green-600 mt-1">
                            👥 {brand.active_users_count}
                          </p>
                        </div>

                        <div className="bg-white p-3 rounded-lg border border-purple-100">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            <span className="text-xs font-medium text-blue-900">Eklenebilir</span>
                          </div>
                          <p className="text-lg font-bold text-blue-600 mt-1">
                            {brand.can_add_user ? '✅ Evet' : '❌ Hayır'}
                          </p>
                        </div>
                      </div>

                      {/* Active Users List */}
                      {brand.active_users && brand.active_users.length > 0 && (
                        <div className="bg-white p-3 rounded-lg border border-purple-100">
                          <h4 className="text-sm font-medium text-purple-900 mb-2">Aktif Kullanıcılar:</h4>
                          <div className="space-y-2">
                            {brand.active_users.map((user) => (
                              <div key={user.id} className="flex items-center justify-between text-sm">
                                <div className="flex items-center">
                                  <span className="mr-2">
                                    {user.is_superuser ? '👑' : user.is_staff ? '🔹' : '👤'}
                                  </span>
                                  <span className="font-medium text-gray-900">{user.username}</span>
                                  <span className="text-gray-500 ml-2">({user.email})</span>
                                </div>
                                <span className="text-xs text-gray-500">
                                  {new Date(user.date_joined).toLocaleDateString('tr-TR')}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* No Users Message */}
                      {(!brand.active_users || brand.active_users.length === 0) && (
                        <div className="bg-white p-3 rounded-lg border border-purple-100 text-center">
                          <span className="text-sm text-gray-500">
                            {brand.user_limit === 0 
                              ? '🚫 Bu paket türünde kullanıcı tanımlanamaz'
                              : '👤 Henüz kullanıcı tanımlanmamış'
                            }
                          </span>
                        </div>
                      )}

                      {/* Package Upgrade Suggestion */}
                      {brand.user_limit === 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            <span className="text-xs text-yellow-800">
                              Kullanıcı ekleyebilmek için paketi <strong>Pro</strong> veya <strong>Premium</strong>'a yükseltin
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                                         {/* Package Type Management */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200 mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          <Edit3 className="h-5 w-5 text-blue-600 mr-2" />
                          <span className="text-sm font-medium text-blue-900">Paket Türü Yönetimi</span>
                        </div>
                        {editingBrand !== brand.id && canEditBrandManagement() && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => startEditingBrand(brand)}
                            className="text-blue-600 border-blue-300 hover:bg-blue-50"
                          >
                            <Edit3 className="h-4 w-4 mr-1" />
                            Değiştir
                          </Button>
                        )}
                      </div>
                      
                                             {editingBrand === brand.id && canEditBrandManagement() ? (
                         <div className="flex items-center space-x-3">
                           <Select
                             value={selectedPackageType}
                             onValueChange={setSelectedPackageType}
                             disabled={updatingBrand === brand.id}
                           >
                             <SelectTrigger className="w-48">
                               <SelectValue placeholder="Paket türü seçin" />
                             </SelectTrigger>
                             <SelectContent>
                               <SelectItem value="normal">Normal Paket</SelectItem>
                               <SelectItem value="pro">Pro Paket</SelectItem>
                               <SelectItem value="premium">Premium Paket</SelectItem>
                             </SelectContent>
                           </Select>
                           
                           <Button
                             onClick={() => saveBrandPackageType(brand.id)}
                             disabled={updatingBrand === brand.id || !selectedPackageType || selectedPackageType === brand.paket_turu}
                             size="sm"
                             className="bg-green-600 hover:bg-green-700 text-white"
                           >
                             {updatingBrand === brand.id ? (
                               <>
                                 <Loader2 className="h-4 w-4 animate-spin mr-1" />
                                 Kaydediliyor...
                               </>
                             ) : (
                               <>
                                 <Save className="h-4 w-4 mr-1" />
                                 Kaydet
                               </>
                             )}
                           </Button>
                           
                           <Button
                             variant="outline"
                             size="sm"
                             onClick={cancelEditing}
                             disabled={updatingBrand === brand.id}
                             className="text-gray-600"
                           >
                             İptal
                           </Button>
                         </div>
                      ) : (
                        <div className="flex items-center">
                          <span className="text-gray-700">Mevcut Paket:</span>
                          <Badge className={`ml-2 ${getPackageTypeColor(brand.paket_turu)}`}>
                            {brand.paket_turu_display}
                          </Badge>
                        </div>
                      )}
                    </div>

                    {/* Package Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center mb-2">
                          <Calendar className="h-4 w-4 text-gray-600 mr-2" />
                          <span className="text-sm font-medium text-gray-700">Paket Başlangıç</span>
                        </div>
                        <p className="text-gray-900">{formatDate(brand.paket_baslangic_tarihi)}</p>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center mb-2">
                          <Calendar className="h-4 w-4 text-gray-600 mr-2" />
                          <span className="text-sm font-medium text-gray-700">Paket Bitiş</span>
                        </div>
                        <p className="text-gray-900">{formatDate(brand.paket_bitis_tarihi)}</p>
                      </div>
                    </div>

                    {/* Package Renewal - Only for admins */}
                    {canEditBrandManagement() && (
                      <div className="bg-gradient-to-r from-emerald-50 to-green-50 p-4 rounded-lg border border-emerald-200 mb-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <RefreshCw className="h-5 w-5 text-emerald-600 mr-2" />
                            <div>
                              <span className="text-sm font-medium text-emerald-900 block">Paket Yenileme</span>
                              <span className="text-xs text-emerald-700">API sayacını sıfırla ve paketi 30 gün uzat</span>
                            </div>
                          </div>
                          <Button
                            onClick={() => refreshPackage(brand.id)}
                            disabled={refreshingBrand === brand.id}
                            size="sm"
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                          >
                            {refreshingBrand === brand.id ? (
                              <>
                                <Loader2 className="h-4 w-4 animate-spin mr-1" />
                                Yenileniyor...
                              </>
                            ) : (
                              <>
                                <RefreshCw className="h-4 w-4 mr-1" />
                                Paketi Yenile
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Timestamps */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-500">
                        <div>
                          <span className="font-medium">Oluşturulma: </span>
                          {formatDate(brand.created_at)}
                        </div>
                        <div>
                          <span className="font-medium">Son Güncelleme: </span>
                          {formatDate(brand.updated_at)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* No Data State */}
          {!loading && !error && brands.length === 0 && (
            <div className="text-center py-12">
              <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {permissions.userType === 'unbranded' ? 'Marka Bağlantısı Bulunamadı' : 'Marka Bulunamadı'}
              </h3>
              <p className="text-gray-600">
                {permissions.userType === 'unbranded' 
                  ? 'Marka yönetim sayfasını görüntüleyebilmek için bir marka ile bağlantınızın bulunması gerekir. Lütfen sistem yöneticinizle iletişime geçin.'
                  : 'Henüz hiç marka kaydı bulunmuyor.'
                }
              </p>
            </div>
          )}

          {/* Back Button */}
          <div className="mt-8 text-center">
            <Button asChild variant="outline" size="lg">
              <Link href="/yonetim">
                Yönetim Paneline Dön
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </AdminRoute>
  )
}