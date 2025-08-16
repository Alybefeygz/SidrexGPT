"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { Navbar } from "@/components/Navbar"
import FourthRobot from "@/components/robots/fourth-robot/FourthRobot"
import PDFUploader from "@/components/PDFUploader"
import RobotMessagesManager from "@/components/RobotMessagesManager"
import { useAuth } from "@/contexts/AuthContext"
import { useRobotBySlug, useRobotPDFList } from "@/hooks/use-api"
import { AdminRoute } from "@/components/AdminRoute"
import api from "@/lib/api"

export default function FourthRobotPage() {
  const { canEditPDF, canEditMessages, getUserPermissions } = useAuth()
  const [robotMessages, setRobotMessages] = useState<string[]>([])
  const [messagesLoading, setMessagesLoading] = useState(false)
  
  // Robot'u slug ile al
  const { data: robotData, loading: robotLoading, error: robotError } = useRobotBySlug('zzen')
  
  // 🔧 Backend'den nested olarak gelen robot verisini düzelt
  const actualRobotData = (robotData as any)?.robot || robotData
  const robotId = actualRobotData?.id
  const accessLevel = actualRobotData?.access_level || 'admin' // Backend'den henüz access_level gelmiyor, default admin
  const robotMessage = actualRobotData?.message
  
  // Robot ID varsa PDF'leri al
  const { data: pdfs, loading: pdfsLoading, error: pdfsError, refetch } = useRobotPDFList(robotId)
  
  // Robot mesajlarını yükle
  const fetchRobotMessages = async () => {
    if (!robotId) return
    
    try {
      setMessagesLoading(true)
      const response = await api.get(`/robots/${robotId}/messages/`)
      const newMessages = response.data.messages || []
      setRobotMessages(newMessages)
      
      // Debug log
      console.log('Robot mesajları güncellendi:', newMessages)
    } catch (error) {
      console.error('Robot mesajları yüklenirken hata:', error)
    } finally {
      setMessagesLoading(false)
    }
  }
  
  // Robot ID değiştiğinde mesajları yükle
  useEffect(() => {
    fetchRobotMessages()
  }, [robotId])
  
  // Mesajlar güncellendiğinde robot state'ini direkt güncelle
  const handleMessagesUpdate = (newMessages: string[]) => {
    setRobotMessages(newMessages)
    console.log('Robot mesajları direkt güncellendi:', newMessages)
  }

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // ... existing code ...
  }

  // Loading state
  if (robotLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl">Robot bilgileri yükleniyor...</div>
        </div>
      </div>
    )
  }

  // API error varsa
  if (robotError) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600">Robot yüklenirken hata oluştu!</div>
          <div className="text-sm text-gray-500 mt-2">{robotError}</div>
          <div className="text-xs text-gray-400 mt-4">Debug Data: {JSON.stringify(robotData)}</div>
        </div>
      </div>
    )
  }

  // robotId yok ise genel hata
  if (!robotId) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600">Robot bulunamadı!</div>
          <div className="text-sm text-gray-500 mt-2">Geçersiz robot slug'ı: zzen</div>
          <div className="text-xs text-gray-400 mt-4">Debug Data: {JSON.stringify(robotData)}</div>
        </div>
      </div>
    )
  }

  // Access level kontrolü
  const isLimitedAccess = accessLevel === 'limited' || accessLevel === 'public'

  return (
    <AdminRoute requireAuth={true}>
      <div className="min-h-screen bg-white">
        <Navbar currentPage="sidrexgpts" />

        {/* Breadcrumb */}
        <div className="bg-gray-50 py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="text-sm">
              <Link href="/" className="text-gray-500 hover:text-gray-700">
                Ana Sayfa
              </Link>
              <span className="mx-2 text-gray-400">{">"}</span>
              <Link href="/sidrexgpt" className="text-gray-500 hover:text-gray-700">
                SidrexGPT's
              </Link>
              <span className="mx-2 text-gray-400">{">"}</span>
              <span className="text-gray-900">Zzen Asistanı</span>
            </nav>
          </div>
        </div>

        {/* Robot Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-8" style={{ color: "#5CA9ED" }}>Zzen Asistanı</h1>
            
            {/* Robot ve PDF Yükleyici bölümü */}
            <div className="w-full grid grid-cols-2 gap-4">
              {/* Sol taraf - Robot */}
              <div className="pl-40" style={{ marginTop: 'calc(10vh + 250px)' }}>
                <div className="flex flex-col items-center">
                  <FourthRobot
                    onChatToggle={handleChatToggle}
                    isOtherChatOpen={false}
                    messages={robotMessages}
                  />
                </div>
              </div>

              {/* Sağ taraf - Robot Messages Manager */}
              <div className="pr-4 pl-20" style={{ marginTop: 'calc(5vh - 50px)' }}>
                {canEditMessages() && robotId ? (
                  <RobotMessagesManager 
                    activeColor="#5CA9ED"
                    robotId={robotId}
                    refetchMessages={fetchRobotMessages}
                    onMessagesUpdate={handleMessagesUpdate}
                  />
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-8">
                    <div className="text-center">
                      <div className="text-4xl mb-4">🔒</div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Robot Mesajları Düzenleme Erişimi Yok</h3>
                      <p className="text-gray-600 mb-4">
                        {getUserPermissions().warningMessage}
                      </p>
                      <div className="text-sm text-gray-500">
                        Robot mesajlarını düzenleme özelliğini kullanmak için gerekli izinlere sahip değilsiniz.
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AdminRoute>
  )
}