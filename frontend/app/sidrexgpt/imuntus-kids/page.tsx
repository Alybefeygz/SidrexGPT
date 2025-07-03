"use client"

import Link from "next/link"
import { useState } from "react"
import { Navbar } from "@/components/Navbar"
import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"
import PDFUploader from "@/components/PDFUploader"
import { useAuth } from "@/contexts/AuthContext"
import { useRobotBySlug, useRobotPDFList } from "@/hooks/use-api"

export default function ThirdRobotPage() {
  const { canEditPDF, getUserPermissions } = useAuth()
  
  // Robot'u slug ile al
  const { data: robotData, loading: robotLoading, error: robotError } = useRobotBySlug('sidrexgpt-kids')
  const robotId = robotData?.robot?.id
  
  // Robot ID varsa PDF'leri al
  const { data: pdfs, loading: pdfsLoading, error: pdfsError, refetch } = useRobotPDFList(robotId)

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

  // Error state
  if (robotError || !robotId) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600">Robot bulunamadı!</div>
          <div className="text-sm text-gray-500 mt-2">{robotError}</div>
        </div>
      </div>
    )
  }

  return (
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
              İletişim
            </Link>
            <span className="mx-2 text-gray-400">{">"}</span>
            <span className="text-gray-900">SidrexGPT Kids</span>
          </nav>
        </div>
      </div>

      {/* Robot Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex flex-col items-center justify-center">
          <h1 className="text-3xl font-bold mb-8" style={{ color: "#FFC429" }}>SidrexGPT Kids Asistanı</h1>
          
          {/* Robot ve PDF Yükleyici bölümü */}
          <div className="w-full grid grid-cols-2 gap-4">
            {/* Sol taraf - Robot */}
            <div className="pl-32" style={{ marginTop: 'calc(10vh + 250px)' }}>
              <div className="flex flex-col items-center">
                <ThirdRobot
                  onChatToggle={() => {}}
                  isOtherChatOpen={false}
                />
              </div>
            </div>
            
            {/* Sağ taraf - PDF Yükleyici */}
            <div className="pr-4 pl-12" style={{ marginTop: 'calc(5vh - 50px)' }}>
              {canEditPDF() ? (
                <PDFUploader 
                  activeColor="#FFC429" 
                  robotId={robotId}
                  initialPdfs={pdfs || []}
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
  )
} 