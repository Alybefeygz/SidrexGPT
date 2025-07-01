"use client"

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Navbar } from '@/components/Navbar'
import { AdminRoute } from '@/components/AdminRoute'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Users, Calendar, Shield, User, Edit3, Save, RefreshCw, Building2, Plus, X, Edit, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'

interface Brand {
  id: number
  name: string
}

interface User {
  id: number
  user: string  // Profile API'de username yerine user field var
  foto: string | null
  brand: string | null  // Full brand info with package details
  brand_id: number | null
  bio: string | null
  is_staff: boolean
  is_superuser: boolean
  is_active: boolean
  user_id: number
}

interface AuthUser {
  pk: number
  username: string
  is_staff: boolean
  is_superuser: boolean
  is_active: boolean
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [authUsers, setAuthUsers] = useState<AuthUser[]>([])
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [userFilter, setUserFilter] = useState<'all' | 'active' | 'inactive'>('all')

  
  // Yeni kullanıcı oluşturma modal state'leri
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletingUser, setDeletingUser] = useState<User | null>(null)
  const [userToDelete, setUserToDelete] = useState<User | null>(null)
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    email: '',
    brand_id: 'none',
    user_type: 'normal'
  })
  const [editUser, setEditUser] = useState({
    username: '',
    user_type: 'normal',
    brand_id: 'none'
  })
  
  const { toast } = useToast()
  const { user: currentUser } = useAuth()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch users and brands in parallel
        const [usersResponse, brandsResponse] = await Promise.all([
          api.profiles.list(),
          api.brands.list()
        ])

        setUsers(usersResponse.data)
        setBrands(brandsResponse.data)
        
        // Auth user bilgilerini profile'den çıkarma
        const authUsersData = usersResponse.data.map((user: User) => ({
          pk: user.user_id,
          username: user.user,
          is_staff: user.is_staff,
          is_superuser: user.is_superuser,
          is_active: user.is_active
        }))
        setAuthUsers(authUsersData)
      } catch (err: any) {
        console.error('Data fetch error:', err)
        setError(err.message || 'Veriler yüklenirken bir hata oluştu')
        toast({
          title: "Hata",
          description: err.message || 'Veriler yüklenirken bir hata oluştu',
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [toast])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Hiç giriş yapmamış'
    const date = new Date(dateString)
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getProfileImageUrl = (foto: string | null) => {
    if (!foto) return null
    return foto.startsWith('http') ? foto : `http://127.0.0.1:8000${foto}`
  }

  const getUserRole = (user: User) => {
    if (user.is_superuser) return 'Super Admin'
    if (user.is_staff) return 'Admin'
    return 'Kullanıcı'
  }

  const getUserRoleColor = (user: User) => {
    if (user.is_superuser) return 'bg-red-100 text-red-800 border-red-200'
    if (user.is_staff) return 'bg-blue-100 text-blue-800 border-blue-200'
    return 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const isUserAdmin = (user: User) => {
    return user.is_staff || user.is_superuser
  }

  const getUserStatus = (user: User) => {
    return user.is_active ? 'Aktif' : 'Pasif'
  }

  const getUserStatusColor = (user: User) => {
    return user.is_active 
      ? 'bg-green-100 text-green-800 border-green-200' 
      : 'bg-red-100 text-red-800 border-red-200'
  }

  const getUserStatusIcon = (user: User) => {
    return user.is_active ? '✅' : '❌'
  }

  const getFilteredUsers = () => {
    switch (userFilter) {
      case 'active':
        return users.filter(user => user.is_active)
      case 'inactive':
        return users.filter(user => !user.is_active)
      default:
        return users
    }
  }

  const getFilterStats = () => {
    const total = users.length
    const active = users.filter(user => user.is_active).length
    const inactive = users.filter(user => !user.is_active).length
    return { total, active, inactive }
  }

  const toggleUserActive = async (user: User) => {
    try {
      const response = await api.profiles.toggleActive(user.id)
      
      // State'i güncelle
      setUsers(prevUsers => 
        prevUsers.map(u => 
          u.id === user.id ? { ...u, is_active: !u.is_active } : u
        )
      )
      
      toast({
        title: "Başarılı!",
        description: `Kullanıcı durumu ${!user.is_active ? 'aktif' : 'pasif'} olarak güncellendi`,
        variant: "default",
      })
    } catch (err: any) {
      console.error('User toggle error:', err)
      toast({
        title: "Hata",
        description: err.message || 'Kullanıcı durumu güncellenirken bir hata oluştu',
        variant: "destructive",
      })
    }
  }

  const startEditingUser = (user: User) => {
    setEditingUser(user)
    setEditUser({
      username: user.user,
      user_type: user.is_superuser ? 'superadmin' : user.is_staff ? 'admin' : 'normal',
      brand_id: user.brand_id?.toString() || 'none'
    })
    setShowEditModal(true)
  }

  const cancelEditing = () => {
    setEditingUser(null)
    setShowEditModal(false)
    setEditUser({ username: '', user_type: 'normal', brand_id: 'none' })
  }

  const updateUser = async () => {
    if (!editingUser) return
    
    try {
      setUpdating(true)
      
      // Debug: Mevcut değerleri logla
      console.log('🔍 Frontend UPDATE - editUser:', editUser)
      console.log('🔍 Frontend UPDATE - editingUser:', editingUser)
      
      // API için veri objesi oluştur (api.profiles.update otomatik olarak FormData'ya çevirecek)
      const updateData = {
        username: editUser.username,
        user_type_input: editUser.user_type,
        brand_id_input: editUser.brand_id !== 'none' ? editUser.brand_id : ''
      }
      
      console.log('🔍 Frontend UPDATE - updateData:', updateData)
      
      const response = await api.profiles.update(editingUser.id, updateData)
      const updatedUser = response.data
      
      // State'i güncelle
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === editingUser.id ? updatedUser : user
        )
      )
      
      setShowEditModal(false)
      setEditingUser(null)
      setEditUser({
        username: '',
        user_type: 'normal',
        brand_id: 'none'
      })
      
      toast({
        title: "Başarılı!",
        description: "Kullanıcı bilgileri güncellendi",
        variant: "default",
      })
    } catch (err: any) {
      console.error('🔍 Frontend UPDATE - Error:', err)
      console.error('🔍 Frontend UPDATE - Error response:', err.response?.data)
      console.error('🔍 Frontend UPDATE - Error status:', err.response?.status)
      
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          err.message || 
                          'Kullanıcı güncellenirken bir hata oluştu'
      
      toast({
        title: "Hata",
        description: typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage,
        variant: "destructive",
      })
    } finally {
      setUpdating(false)
    }
  }

  const deleteUser = async () => {
    if (!userToDelete) return
    
    try {
      setDeleting(true)
      
      await api.profiles.delete(userToDelete.id)
      
      // State'i güncelle
      setUsers(prevUsers => prevUsers.filter(user => user.id !== userToDelete.id))
      
      setShowDeleteModal(false)
      setUserToDelete(null)
      
      toast({
        title: "Başarılı!",
        description: "Kullanıcı silindi",
        variant: "default",
      })
    } catch (err: any) {
      console.error('User delete error:', err)
      toast({
        title: "Hata",
        description: err.message || 'Kullanıcı silinirken bir hata oluştu',
        variant: "destructive",
      })
    } finally {
      setDeleting(false)
    }
  }

  const createNewUser = async () => {
    try {
      setCreating(true)
      
      // Boş veya geçersiz değerleri kontrol et
      if (!newUser.username || !newUser.password) {
        throw new Error('Kullanıcı adı ve şifre zorunludur')
      }

      // API için veri objesi oluştur (api.profiles.create otomatik olarak FormData'ya çevirecek)
      const userData = {
        username: newUser.username,
        password: newUser.password,
        email: newUser.email || '',
        brand_id_input: newUser.brand_id !== 'none' ? newUser.brand_id : '',
        user_type_input: newUser.user_type || 'normal'
      }
      
      console.log('🔍 Frontend: Gönderilecek veri:', userData)
      
      const response = await api.profiles.create(userData)
      const createdUser = response.data
      
      // State'i güncelle
      setUsers(prevUsers => [...prevUsers, createdUser])
      
      setShowCreateModal(false)
      setNewUser({
        username: '',
        password: '',
        email: '',
        brand_id: 'none',
        user_type: 'normal'
      })
      
      toast({
        title: "Başarılı!",
        description: "Yeni kullanıcı oluşturuldu",
        variant: "default",
      })
    } catch (err: any) {
      console.error('🔍 Frontend: User create error:', err)
      console.error('🔍 Frontend: Error response:', err.response?.data)
      console.error('🔍 Frontend: Error status:', err.response?.status)
      
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.details || 
                          err.response?.data?.message || 
                          err.message || 
                          'Kullanıcı oluşturulurken bir hata oluştu'
      
      toast({
        title: "Hata",
        description: typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage,
        variant: "destructive",
      })
    } finally {
      setCreating(false)
    }
  }



  return (
    <AdminRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8 flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Kullanıcı Yönetimi</h1>
              <p className="text-gray-600">Sistem kullanıcılarını görüntüleyin ve yönetin</p>
            </div>
            <Button 
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Plus className="h-4 w-4 mr-2" />
              Yeni Kişi Oluştur
            </Button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Kullanıcılar yükleniyor...</span>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="text-center py-12">
              <div className="text-red-600 mb-4">❌ {error}</div>
              <Button onClick={() => window.location.reload()} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Tekrar Dene
              </Button>
            </div>
          )}

          {/* Filter Section */}
          {!loading && !error && users.length > 0 && (
            <div className="mb-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  {/* Filter Statistics */}
                  <div className="flex items-center space-x-4">
                    <h3 className="text-sm font-medium text-gray-700">Kullanıcı Durumu:</h3>
                    <div className="flex items-center space-x-1 text-xs text-gray-600">
                      <span className="bg-gray-100 px-2 py-1 rounded">
                        Toplam: {getFilterStats().total}
                      </span>
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                        Aktif: {getFilterStats().active}
                      </span>
                      <span className="bg-red-100 text-red-800 px-2 py-1 rounded">
                        Pasif: {getFilterStats().inactive}
                      </span>
                    </div>
                  </div>

                  {/* Filter Buttons */}
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => setUserFilter('all')}
                      size="sm"
                      variant={userFilter === 'all' ? 'default' : 'outline'}
                      className={userFilter === 'all' ? 'bg-blue-600 text-white' : ''}
                    >
                      <Users className="h-4 w-4 mr-1" />
                      Tümü ({getFilterStats().total})
                    </Button>
                    <Button
                      onClick={() => setUserFilter('active')}
                      size="sm"
                      variant={userFilter === 'active' ? 'default' : 'outline'}
                      className={userFilter === 'active' ? 'bg-green-600 text-white' : 'text-green-600 border-green-300 hover:bg-green-50'}
                    >
                      ✅ Aktif ({getFilterStats().active})
                    </Button>
                    <Button
                      onClick={() => setUserFilter('inactive')}
                      size="sm"
                      variant={userFilter === 'inactive' ? 'default' : 'outline'}
                      className={userFilter === 'inactive' ? 'bg-red-600 text-white' : 'text-red-600 border-red-300 hover:bg-red-50'}
                    >
                      ❌ Pasif ({getFilterStats().inactive})
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Users Grid */}
          {!loading && !error && users.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {getFilteredUsers().map((user) => (
                <Card key={user.id} className="shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {/* Profile Photo or Icon with Status Indicator */}
                        <div className="relative mr-3">
                          {user.foto ? (
                            <img 
                              src={getProfileImageUrl(user.foto) || ''} 
                              alt={`${user.user} profil fotoğrafı`}
                              className={`h-12 w-12 rounded-full object-cover border-2 ${
                                user.is_active ? 'border-green-300' : 'border-red-300'
                              }`}
                            />
                          ) : (
                            <div className={`h-12 w-12 rounded-full flex items-center justify-center border-2 ${
                              user.is_active 
                                ? 'bg-green-100 border-green-300' 
                                : 'bg-red-100 border-red-300'
                            }`}>
                              <User className={`h-6 w-6 ${
                                user.is_active ? 'text-green-600' : 'text-red-600'
                              }`} />
                            </div>
                          )}
                          {/* Status Indicator Circle */}
                          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
                            user.is_active ? 'bg-green-500' : 'bg-red-500'
                          }`}>
                            <div className="w-full h-full flex items-center justify-center">
                              <span className="text-white text-xs">
                                {user.is_active ? '●' : '●'}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <CardTitle className="text-lg text-gray-900">{user.user}</CardTitle>
                            <span className="text-lg">
                              {getUserStatusIcon(user)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">Profil ID: {user.id}</p>
                        </div>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <Badge className={`${getUserRoleColor(user)} border text-xs`}>
                          {getUserRole(user)}
                        </Badge>
                        <Badge className={`${getUserStatusColor(user)} border text-xs`}>
                          {getUserStatus(user)}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="p-6">
                    {/* User Info */}
                    <div className="space-y-3 mb-4">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Kullanıcı Adı:</span>
                        <p className="text-gray-900 font-medium">{user.user}</p>
                      </div>

                      <div>
                        <span className="text-sm font-medium text-gray-700">Hesap Durumu:</span>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge className={`${getUserStatusColor(user)} border text-xs`}>
                            {getUserStatusIcon(user)} {getUserStatus(user)}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {user.is_active 
                              ? 'Kullanıcı sistemde aktif olarak kullanılabilir' 
                              : 'Kullanıcı hesabı pasif durumda, sisteme giriş yapamaz'
                            }
                          </span>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-sm font-medium text-gray-700">Bio:</span>
                        <p className="text-gray-900 text-sm">{user.bio || 'Henüz bio eklenmemiş'}</p>
                      </div>
                    </div>

                    {/* Marka Bilgisi - Herkes için göster */}
                    <div className={`bg-gradient-to-r p-4 rounded-lg border ${
                      user.is_active 
                        ? 'from-gray-50 to-blue-50 border-gray-200' 
                        : 'from-red-50 to-orange-50 border-red-200'
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Building2 className="h-5 w-5 text-gray-600 mr-2" />
                          <span className="text-gray-700">Mevcut Marka:</span>
                          <Badge className={`ml-2 ${user.brand ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                            {user.brand || 'Atanmamış'}
                          </Badge>
                        </div>
                        <Badge className={`${getUserStatusColor(user)} border text-xs`}>
                          {getUserStatusIcon(user)} {getUserStatus(user)}
                        </Badge>
                      </div>
                      
                      {/* Pasif kullanıcı uyarısı */}
                      {!user.is_active && (
                        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            <span className="text-xs text-red-800">
                              <strong>⚠️ Hesap Pasif:</strong> Bu kullanıcı sisteme giriş yapamaz ve API'leri kullanamaz.
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-2 mt-4">
                      <Button
                        onClick={() => startEditingUser(user)}
                        size="sm"
                        variant="outline"
                        className="flex-1"
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Düzenle
                      </Button>
                      
                      {/* Durum değiştirme butonu - admin yetkisi gerekli ve kendisi değilse */}
                      {currentUser?.username !== user.user && (
                        <Button
                          onClick={() => toggleUserActive(user)}
                          size="sm"
                          variant="outline"
                          className={`flex-1 ${
                            user.is_active 
                              ? 'text-orange-600 hover:text-orange-700 hover:bg-orange-50' 
                              : 'text-green-600 hover:text-green-700 hover:bg-green-50'
                          }`}
                        >
                          {user.is_active ? (
                            <>
                              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
                              </svg>
                              Pasif Yap
                            </>
                          ) : (
                            <>
                              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              Aktif Yap
                            </>
                          )}
                        </Button>
                      )}
                      
                      {/* Silme butonu sadece mevcut kullanıcının kendisi değilse göster */}
                      {currentUser?.username !== user.user && (
                        <Button
                          onClick={() => {
                            setUserToDelete(user)
                            setShowDeleteModal(true)
                          }}
                          size="sm"
                          variant="outline"
                          className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Sil
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* No Data State */}
          {!loading && !error && users.length === 0 && (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Kullanıcı Bulunamadı</h3>
              <p className="text-gray-600">Henüz hiç kullanıcı kaydı bulunmuyor.</p>
            </div>
          )}

          {/* No Filtered Data State */}
          {!loading && !error && users.length > 0 && getFilteredUsers().length === 0 && (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {userFilter === 'active' && 'Aktif Kullanıcı Bulunamadı'}
                {userFilter === 'inactive' && 'Pasif Kullanıcı Bulunamadı'}
              </h3>
              <p className="text-gray-600 mb-4">
                {userFilter === 'active' && 'Hiç aktif kullanıcı bulunmuyor.'}
                {userFilter === 'inactive' && 'Hiç pasif kullanıcı bulunmuyor.'}
              </p>
              <Button
                onClick={() => setUserFilter('all')}
                variant="outline"
                size="sm"
              >
                <Users className="h-4 w-4 mr-2" />
                Tüm Kullanıcıları Göster
              </Button>
            </div>
          )}

          {/* Create User Modal */}
          {showCreateModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Yeni Kullanıcı Oluştur</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setShowCreateModal(false)
                      setNewUser({ username: '', password: '', email: '', brand_id: 'none', user_type: 'normal' })
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="username">Kullanıcı Adı</Label>
                    <Input
                      id="username"
                      type="text"
                      value={newUser.username}
                      onChange={(e) => setNewUser(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="Kullanıcı adını girin"
                      disabled={creating}
                    />
                  </div>

                  <div>
                    <Label htmlFor="password">Şifre</Label>
                    <Input
                      id="password"
                      type="password"
                      value={newUser.password}
                      onChange={(e) => setNewUser(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="Şifreyi girin"
                      disabled={creating}
                    />
                  </div>

                  <div>
                    <Label htmlFor="email">E-posta</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="E-posta adresini girin"
                      disabled={creating}
                    />
                  </div>

                  <div>
                    <Label htmlFor="user-type">Kullanıcı Türü</Label>
                    <Select
                      value={newUser.user_type}
                      onValueChange={(value) => setNewUser(prev => ({ ...prev, user_type: value }))}
                      disabled={creating}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Kullanıcı türünü seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="normal">Normal Kullanıcı</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="superadmin">Süper Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="brand">Marka</Label>
                    <Select
                      value={newUser.brand_id}
                      onValueChange={(value) => setNewUser(prev => ({ ...prev, brand_id: value }))}
                      disabled={creating}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Marka seçin (opsiyonel)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Markası Yok</SelectItem>
                        {brands.map((brand) => (
                          <SelectItem key={brand.id} value={brand.id.toString()}>
                            {brand.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex space-x-3 mt-6">
                  <Button
                    onClick={createNewUser}
                    disabled={creating || !newUser.username.trim() || !newUser.password.trim()}
                    className="bg-blue-600 hover:bg-blue-700 text-white flex-1"
                  >
                    {creating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Oluşturuluyor...
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-2" />
                        Kullanıcı Oluştur
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowCreateModal(false)
                      setNewUser({ username: '', password: '', email: '', brand_id: 'none', user_type: 'normal' })
                    }}
                    disabled={creating}
                    className="flex-1"
                  >
                    İptal
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Edit User Modal */}
          {showEditModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Kullanıcı Düzenle</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelEditing}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="username">Kullanıcı Adı</Label>
                    <Input
                      id="username"
                      type="text"
                      value={editUser.username}
                      onChange={(e) => setEditUser(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="Kullanıcı adını girin"
                      disabled={updating}
                    />
                  </div>

                  <div>
                    <Label htmlFor="user-type">Kullanıcı Türü</Label>
                    <Select
                      value={editUser.user_type}
                      onValueChange={(value) => setEditUser(prev => ({ ...prev, user_type: value }))}
                      disabled={updating}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Kullanıcı türünü seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="normal">Normal Kullanıcı</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="superadmin">Süper Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="brand">Marka</Label>
                    <Select
                      value={editUser.brand_id}
                      onValueChange={(value) => setEditUser(prev => ({ ...prev, brand_id: value }))}
                      disabled={updating}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Marka seçin (opsiyonel)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Markası Yok</SelectItem>
                        {brands.map((brand) => (
                          <SelectItem key={brand.id} value={brand.id.toString()}>
                            {brand.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex space-x-3 mt-6">
                  <Button
                    onClick={updateUser}
                    disabled={updating || !editUser.username.trim() || !editUser.user_type.trim() || !editUser.brand_id.trim()}
                    className="bg-blue-600 hover:bg-blue-700 text-white flex-1"
                  >
                    {updating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Güncelleniyor...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Kullanıcı Güncelle
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={cancelEditing}
                    disabled={updating}
                    className="flex-1"
                  >
                    İptal
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Delete User Modal */}
          {showDeleteModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Kullanıcı Sil</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setShowDeleteModal(false)
                      setUserToDelete(null)
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <p className="text-gray-700">
                  Kullanıcı "{userToDelete?.user}" silinecektir. Bu işlem geri döndürülemez.
                </p>

                <div className="flex space-x-3 mt-6">
                  <Button
                    onClick={deleteUser}
                    disabled={deleting}
                    className="bg-red-600 hover:bg-red-700 text-white flex-1"
                  >
                    {deleting ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Siliniyor...
                      </>
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4 mr-2" />
                        Kullanıcı Sil
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowDeleteModal(false)
                      setUserToDelete(null)
                    }}
                    disabled={deleting}
                    className="flex-1"
                  >
                    İptal
                  </Button>
                </div>
              </div>
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