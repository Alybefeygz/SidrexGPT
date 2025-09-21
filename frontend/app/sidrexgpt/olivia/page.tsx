"use client"

import Link from "next/link"
import { useState } from "react"
import { Navbar } from "@/components/Navbar"
import EighthRobot from "@/components/robots/eighth-robot/EighthRobot"
import PDFUploader from "@/components/PDFUploader"
import { useAuth } from "@/contexts/AuthContext"
import { useRobotPDFList } from "@/hooks/use-api"
import { AdminRoute } from "@/components/AdminRoute"

export default function OliviaPage() {
  const [activeChatRobot, setActiveChatRobot] = useState<boolean>(false)
  const { canEditPDF, getUserPermissions } = useAuth()
  
  // Robot ID'si 8 (Olivia için)
  const robotId = 8
  const { data: pdfs, loading: pdfsLoading, error: pdfsError, refetch } = useRobotPDFList(robotId)

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    setActiveChatRobot(isOpen)
  }

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
              <span className="text-gray-900">Olivia SidrexGPT</span>
            </nav>
          </div>
        </div>

        {/* Robot Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-8" style={{ color: "#D9E60D" }}>Olivia SidrexGPT Asistanı</h1>
            
            {/* Robot ve PDF Yükleyici bölümü */}
            <div className="w-full grid grid-cols-2 gap-4">
              {/* Sol taraf - Robot */}
              <div className="pl-40" style={{ marginTop: 'calc(10vh + 250px)' }}>
                <div className="flex flex-col items-center">
                  <EighthRobot
                    onChatToggle={handleChatToggle}
                    isOtherChatOpen={false}
                  />
                </div>
              </div>
              
              {/* Sağ taraf - PDF Yükleyici */}
              <div className="pr-4 pl-20" style={{ marginTop: 'calc(5vh - 50px)' }}>
                {canEditPDF() ? (
                  <PDFUploader 
                    activeColor="#D9E60D" 
                    robotId={8} 
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
    </AdminRoute>
  )
}