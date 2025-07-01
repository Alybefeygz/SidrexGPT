'use client'

import { useState } from 'react'
import { useAuth, useProfiles, useRobots } from '@/hooks/use-api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'

export default function ApiTestPage() {
  const { user, login, register, logout, isAuthenticated, loading: authLoading } = useAuth()
  const { data: profiles, loading: profilesLoading, error: profilesError } = useProfiles()
  const { data: robots, loading: robotsLoading, error: robotsError } = useRobots()
  const { toast } = useToast()

  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [registerForm, setRegisterForm] = useState({ 
    username: '', 
    email: '', 
    password1: '', 
    password2: '' 
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await login(loginForm)
    if (result.success) {
      toast({
        title: "Giriş Başarılı!",
        description: "Hoş geldiniz!",
      })
    } else {
      toast({
        title: "Giriş Başarısız",
        description: result.error,
        variant: "destructive",
      })
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await register(registerForm)
    if (result.success) {
      toast({
        title: "Kayıt Başarılı!",
        description: "Hesabınız oluşturuldu ve giriş yapıldı.",
      })
      // Formu temizle
      setRegisterForm({ username: '', email: '', password1: '', password2: '' })
    } else {
      toast({
        title: "Kayıt Başarısız",
        description: result.error,
        variant: "destructive",
      })
    }
  }

  if (authLoading) {
    return <div className="p-8">Yükleniyor...</div>
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">API Test Sayfası</h1>
      
      <Tabs defaultValue="auth" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="auth">Authentication</TabsTrigger>
          <TabsTrigger value="profiles">Profiller</TabsTrigger>
          <TabsTrigger value="robots">Robotlar</TabsTrigger>
        </TabsList>

        <TabsContent value="auth" className="space-y-4">
          {isAuthenticated ? (
            <Card>
              <CardHeader>
                <CardTitle>Kullanıcı Bilgileri</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-100 p-4 rounded">
                  {JSON.stringify(user, null, 2)}
                </pre>
                <Button onClick={logout} className="mt-4" variant="destructive">
                  Çıkış Yap
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Login Form */}
              <Card>
                <CardHeader>
                  <CardTitle>Giriş Yap</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <Input
                      placeholder="Kullanıcı adı"
                      value={loginForm.username}
                      onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                    />
                    <Input
                      type="password"
                      placeholder="Şifre"
                      value={loginForm.password}
                      onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                    />
                    <Button type="submit" className="w-full">
                      Giriş Yap
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Register Form */}
              <Card>
                <CardHeader>
                  <CardTitle>Kayıt Ol</CardTitle>
                  <div className="text-sm text-gray-600 mt-2">
                    <p className="font-medium mb-1">Şifre Kuralları:</p>
                    <ul className="text-xs space-y-1">
                      <li>• En az 8 karakter olmalı</li>
                      <li>• Kullanıcı adından farklı olmalı</li>
                      <li>• Yaygın şifreler kullanmayın</li>
                      <li>• Sadece sayılardan oluşmamalı</li>
                    </ul>
                  </div>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleRegister} className="space-y-4">
                    <Input
                      placeholder="Kullanıcı adı"
                      value={registerForm.username}
                      onChange={(e) => setRegisterForm({...registerForm, username: e.target.value})}
                    />
                    <Input
                      type="email"
                      placeholder="Email"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                    />
                    <Input
                      type="password"
                      placeholder="Şifre"
                      value={registerForm.password1}
                      onChange={(e) => setRegisterForm({...registerForm, password1: e.target.value})}
                    />
                    <Input
                      type="password"
                      placeholder="Şifre (Tekrar)"
                      value={registerForm.password2}
                      onChange={(e) => setRegisterForm({...registerForm, password2: e.target.value})}
                    />
                    <Button type="submit" className="w-full">
                      Kayıt Ol
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="profiles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profiller</CardTitle>
            </CardHeader>
            <CardContent>
              {profilesLoading ? (
                <div>Profiller yükleniyor...</div>
              ) : profilesError ? (
                <div className="text-red-500">Hata: {profilesError}</div>
              ) : (
                <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                  {JSON.stringify(profiles, null, 2)}
                </pre>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="robots" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Robotlar</CardTitle>
            </CardHeader>
            <CardContent>
              {robotsLoading ? (
                <div>Robotlar yükleniyor...</div>
              ) : robotsError ? (
                <div className="text-red-500">Hata: {robotsError}</div>
              ) : (
                <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                  {JSON.stringify(robots, null, 2)}
                </pre>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
} 