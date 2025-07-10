"use client"

import Link from "next/link"
import { useState } from "react"
import { Navbar } from "@/components/Navbar"
import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"
import PDFUploader from "@/components/PDFUploader"
import { useAuth } from "@/contexts/AuthContext"
import { useRobotBySlug, useRobotPDFList } from "@/hooks/use-api"
import { AdminRoute } from "@/components/AdminRoute"

export default function ThirdRobotPage() {
  const { canEditPDF, getUserPermissions } = useAuth()
  
  // Robot'u slug ile al
  const { data: robotData, loading: robotLoading, error: robotError } = useRobotBySlug('sidrexgpt-kids')
  
  // 🔧 Backend'den nested olarak gelen robot verisini düzelt
  const actualRobotData = (robotData as any)?.robot || robotData
  const robotId = actualRobotData?.id
  const accessLevel = actualRobotData?.access_level || 'admin' // Backend'den henüz access_level gelmiyor, default admin
  const robotMessage = actualRobotData?.message
  
  // Robot ID varsa PDF'leri al
  const { data: pdfs, loading: pdfsLoading, error: pdfsError, refetch } = useRobotPDFList(robotId)

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
          <div className="text-sm text-gray-500 mt-2">Geçersiz robot slug'ı: sidrexgpt-kids</div>
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
              <span className="text-gray-900">SidrexGPT Kids</span>
            </nav>
          </div>
        </div>

        {/* Robot Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-8" style={{ color: "#F2B831" }}>SidrexGPT Kids Asistanı</h1>
            
            {/* Robot ve PDF Yükleyici bölümü */}
            <div className="w-full grid grid-cols-2 gap-4">
              {/* Sol taraf - Robot */}
              <div className="pl-40" style={{ marginTop: 'calc(10vh + 250px)' }}>
                <div className="flex flex-col items-center">
                  <ThirdRobot
                    onChatToggle={handleChatToggle}
                    isOtherChatOpen={false}
                  />
                </div>
              </div>

              {/* Sağ taraf - PDF Yükleyici */}
              <div className="pr-4 pl-20" style={{ marginTop: 'calc(5vh - 50px)' }}>
                {canEditPDF() && robotId ? (
                  <PDFUploader 
                    activeColor="#F2B831"
                    robotId={robotId}
                    initialPdfs={pdfs as any || []}  // ✅ Type assertion ile düzeltildi
                    refetchPdfs={refetch}
                  />
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-8">
                    <div className="text-center">
                      <div className="text-4xl mb-4">🔒</div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">PDF Düzenleme Erişimi Yok</h3>
                      <p className="text-gray-600 mb-4">
                        {getUserPermissions().warningMessage}
                      </p>
                      <div className="text-sm text-gray-500">
                        PDF düzenleme özelliğini kullanmak için gerekli izinlere sahip değilsiniz.
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