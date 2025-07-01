"use client"

import { useState, useRef, useEffect } from "react"
import { File, CheckCircle, X, PlusCircle, Upload, Loader2, LogIn } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { useRobotPDFList, useRobotPDFActions } from "@/hooks/use-api"
import { useAuth } from "@/contexts/AuthContext"
import Link from "next/link"

interface PDFFile {
  id: number
  dosya_adi: string
  dosya_boyutu: number
  is_active: boolean
  pdf_type: 'kural' | 'rol' | 'bilgi' | 'beyan'
  aciklama?: string
  yukleme_zamani: string
  robot: number
  isPending?: boolean // Henüz kaydedilmemiş PDF'ler için
}

interface PDFUploaderProps {
  activeColor?: string // Robotun rengi için parametre
  robotId?: number // Backend'den hangi robotu kullanacağımız
  initialPdfs?: PDFFile[];
  refetchPdfs: () => void;
}

export default function PDFUploader({ 
  activeColor = "#16B6C2", 
  robotId, 
  initialPdfs = [],
  refetchPdfs
}: PDFUploaderProps) {
  const { toast } = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { isAuthenticated, isAdmin, canEditPDF, getUserPermissions, loading: authLoading } = useAuth()
  
  // Backend'den PDF'leri çek
  const { data: pdfs, loading: pdfsLoading, error: pdfsError, refetch } = useRobotPDFList(robotId)
  const { uploadPDF, deletePDF, togglePDFActive, updatePDF, loading: actionLoading, error: actionError } = useRobotPDFActions()

  const [localPdfs, setLocalPdfs] = useState<PDFFile[]>(initialPdfs)
  const [hasChanges, setHasChanges] = useState(false)
  const [pendingChanges, setPendingChanges] = useState<{
    uploads: File[]
    updates: { id: number, changes: any }[]
    deletes: number[]
    toggles: number[]
  }>({
    uploads: [],
    updates: [],
    deletes: [],
    toggles: []
  })

  // Backend'den gelen PDF'leri local state'e aktar
  useEffect(() => {
    if (initialPdfs && JSON.stringify(initialPdfs) !== JSON.stringify(localPdfs)) {
      setLocalPdfs(initialPdfs)
      // Eğer pending değişiklikler varsa, hasChanges'i false yapma
      if (!pendingChanges.uploads.length && !pendingChanges.updates.length && 
          !pendingChanges.deletes.length && !pendingChanges.toggles.length) {
        setHasChanges(false)
        setPendingChanges({
          uploads: [],
          updates: [],
          deletes: [],
          toggles: []
        })
      }
    }
  }, [initialPdfs, localPdfs, pendingChanges])

  // pendingChanges değiştiğinde hasChanges'i güncelle
  useEffect(() => {
    const hasAnyChanges = 
      pendingChanges.uploads.length > 0 ||
      pendingChanges.updates.length > 0 ||
      pendingChanges.deletes.length > 0 ||
      pendingChanges.toggles.length > 0

    console.log('PendingChanges değişti:', pendingChanges)
    console.log('HasChanges:', hasAnyChanges)
    
    setHasChanges(hasAnyChanges)
  }, [pendingChanges])

  useEffect(() => {
    if (actionError) {
      toast({
        title: "Hata",
        description: actionError,
        variant: "destructive",
      })
    }
  }, [actionError, toast])

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return

    const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf')
    
    if (pdfFiles.length === 0) {
      toast({
        title: "Uyarı",
        description: "Lütfen sadece PDF dosyaları seçin.",
        variant: "destructive",
      })
      return
    }

    // Pending uploads'a ekle
    setPendingChanges(prev => {
      const newState = {
        ...prev,
        uploads: [...prev.uploads, ...pdfFiles]
      }
      console.log('Yeni pending changes:', newState)
      return newState
    })

    // Local state'i güncelle (preview için)
    const tempPdfs = pdfFiles.map((file, index) => ({
      id: -(Date.now() + index), // Geçici negatif ID
      dosya_adi: file.name,
      dosya_boyutu: file.size,
      is_active: false,
      pdf_type: 'bilgi' as const,
      aciklama: '',
      yukleme_zamani: new Date().toISOString(),
      robot: robotId!, // Burada robotId'nin tanımlı olduğunu varsayıyoruz
      isPending: true // Henüz kaydedilmedi işareti
    }))

    setLocalPdfs(prev => [...prev, ...tempPdfs] as PDFFile[])

    toast({
      title: "Eklendi",
      description: `${pdfFiles.length} PDF yükleme için hazırlandı. Sisteme yükle butonuna basın.`,
    })
    
    // File input'u temizle
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    handleFileUpload(files)
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleToggleActive = (id: number) => {
    // Local state'i güncelle
    setLocalPdfs(prev => prev.map(pdf => 
      pdf.id === id ? { ...pdf, is_active: !pdf.is_active } : pdf
    ))

    // Pending changes'e ekle
    if (id > 0) { // Sadece gerçek PDF'ler için
      setPendingChanges(prev => {
        const newToggles = prev.toggles.includes(id) 
          ? prev.toggles.filter(toggleId => toggleId !== id) // Toggle'ı geri al
          : [...prev.toggles, id] // Toggle'ı ekle

        console.log('Toggle sonrası pending changes:', {
          ...prev,
          toggles: newToggles
        })

        return {
          ...prev,
          toggles: newToggles
        }
      })
    }

    toast({
      title: "Değişiklik Kaydedildi",
      description: "PDF aktivasyon durumu değiştirildi. Sisteme yükle butonuna basarak uygulayın.",
    })
  }

  const handleRemovePdf = (id: number) => {
    // Local state'den kaldır
    setLocalPdfs(prev => prev.filter(pdf => pdf.id !== id))

    if (id > 0) { // Gerçek PDF ise pending deletes'e ekle
      setPendingChanges(prev => {
        const newDeletes = [...prev.deletes, id]
        const newUpdates = prev.updates.filter(update => update.id !== id)
        const newToggles = prev.toggles.filter(toggleId => toggleId !== id)

        const hasAnyChanges = 
          prev.uploads.length > 0 ||
          newUpdates.length > 0 ||
          newDeletes.length > 0 ||
          newToggles.length > 0

        setHasChanges(hasAnyChanges)

        return {
          ...prev,
          deletes: newDeletes,
          updates: newUpdates,
          toggles: newToggles
        }
      })
    } else { // Geçici PDF ise (henüz kaydedilmemiş) sadece uploads'dan kaldır
      setPendingChanges(prev => {
        const newUploads = prev.uploads.filter((_, index) => -(Date.now() + index) !== id)

        const hasAnyChanges = 
          newUploads.length > 0 ||
          prev.updates.length > 0 ||
          prev.deletes.length > 0 ||
          prev.toggles.length > 0

        setHasChanges(hasAnyChanges)

        return {
          ...prev,
          uploads: newUploads
        }
      })
    }

    toast({
      title: "Kaldırıldı",
      description: "PDF kaldırma için hazırlandı. Sisteme yükle butonuna basın.",
    })
  }

  const handleChangePdfType = (id: number, newType: 'kural' | 'rol' | 'bilgi' | 'beyan') => {
    // Local state'i güncelle
    setLocalPdfs(prev => prev.map(pdf => 
      pdf.id === id ? { ...pdf, pdf_type: newType } : pdf
    ))

    if (id > 0) { // Sadece gerçek PDF'ler için
      setPendingChanges(prev => {
        let newUpdates = [...prev.updates]
        const existingUpdateIndex = newUpdates.findIndex(update => update.id === id)
        
        if (existingUpdateIndex >= 0) {
          // Mevcut update'i güncelle
          newUpdates[existingUpdateIndex] = {
            ...newUpdates[existingUpdateIndex],
            changes: { ...newUpdates[existingUpdateIndex].changes, pdf_type: newType, robot_id: robotId }
          }
        } else {
          // Yeni update ekle
          newUpdates = [...prev.updates, { id, changes: { pdf_type: newType, robot_id: robotId } }]
        }

        return {
          ...prev,
          updates: newUpdates
        }
      })
    }

    toast({
      title: "Değişiklik Kaydedildi",
      description: "PDF türü değiştirildi. Sisteme yükle butonuna basarak uygulayın.",
    })
  }

  const handleSystemUpload = async () => {
    if (!robotId) {
      toast({
        title: "Hata",
        description: "Robot ID bulunamadı.",
        variant: "destructive",
      })
      return
    }

    try {
      // Yeni PDF'leri yükle
      for (const file of pendingChanges.uploads) {
        const result = await uploadPDF(robotId, file, 'bilgi')
        if (!result.success) {
          throw new Error(result.error || "PDF yükleme hatası")
        }
      }

      // PDF türü değişikliklerini uygula
      for (const update of pendingChanges.updates) {
        const result = await updatePDF(update.id, update.changes)
        if (!result.success) {
          throw new Error(result.error || "PDF güncelleme hatası")
        }
      }

      // PDF aktivasyon durumu değişikliklerini uygula
      for (const pdfId of pendingChanges.toggles) {
        const result = await togglePDFActive(pdfId)
        if (!result.success) {
          throw new Error(result.error || "PDF aktivasyon durumu değiştirme hatası")
        }
      }

      // PDF silme işlemlerini uygula
      for (const pdfId of pendingChanges.deletes) {
        const result = await deletePDF(pdfId)
        if (!result.success) {
          throw new Error(result.error || "PDF silme hatası")
        }
      }

      // Başarılı mesajı göster
      toast({
        title: "Başarılı",
        description: "Tüm değişiklikler başarıyla uygulandı.",
      })

      // State'leri sıfırla
      setPendingChanges({
        uploads: [],
        updates: [],
        deletes: [],
        toggles: []
      })
      setHasChanges(false)

      // PDF listesini yenile
      await refetch()
      refetchPdfs()

    } catch (error: any) {
      toast({
        title: "Hata",
        description: error.message || "İşlem sırasında bir hata oluştu.",
        variant: "destructive",
      })
    }
  }

  // Renk tonlarını hesaplama
  const getActiveStyles = () => {
    const lighterColor = activeColor + "15"
    const borderColor = activeColor + "50"
    
    return {
      bg: lighterColor,
      border: borderColor,
      text: activeColor
    }
  }
  
  const activeStyles = getActiveStyles()

  if (pdfsLoading || authLoading) {
    return (
      <div className="w-full h-full p-5 bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-center h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin" style={{ color: activeColor }} />
          <span className="ml-2 text-gray-600">
            {authLoading ? 'Yetki kontrol ediliyor...' : 'PDF\'ler yükleniyor...'}
          </span>
        </div>
      </div>
    )
  }

  if (pdfsError) {
    // Auth kontrolü - eğer 401 Unauthorized hatası varsa ve kullanıcı giriş yapmamışsa giriş mesajı göster
    const isUnauthorized = pdfsError.includes('401') || pdfsError.includes('Unauthorized') || pdfsError.includes('Authentication')
    
    if (isUnauthorized && !isAuthenticated) {
      return (
        <div className="w-full h-full p-5 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-center h-[400px]">
            <div className="text-center">
              <LogIn className="h-8 w-8 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Giriş Yapmalısınız</h3>
              <p className="text-gray-600 mb-4">PDF'leri görüntülemek için giriş yapmanız gerekiyor.</p>
              <Link href="/yonetim">
                <Button 
                  className="inline-flex items-center gap-2"
                  style={{ backgroundColor: activeColor }}
                >
                  <LogIn className="h-4 w-4" />
                  Giriş Yap
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )
    }
    
    return (
      <div className="w-full h-full p-5 bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-center h-[400px]">
          <div className="text-center">
            <X className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-red-500">PDF'ler yüklenirken hata oluştu</p>
            <Button variant="outline" onClick={() => refetch()} className="mt-2">
              Tekrar Dene
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full p-5 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="mb-3 flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">PDF Dosyaları</h3>
        
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={actionLoading}
            className="h-8 text-xs"
          >
            Yenile
          </Button>
          {isAuthenticated && canEditPDF() ? (
            <Button
              size="sm"
              onClick={handleButtonClick}
              disabled={actionLoading}
              className="h-8 text-xs flex items-center gap-1"
              style={{
                backgroundColor: activeColor
              }}
            >
              {actionLoading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <PlusCircle className="h-3.5 w-3.5" />
              )}
              PDF Ekle
            </Button>
          ) : isAuthenticated ? (
            <Button
              size="sm"
              variant="outline"
              disabled={true}
              className="h-8 text-xs flex items-center gap-1 cursor-not-allowed"
            >
              <X className="h-3.5 w-3.5" />
              Düzenleme Yetkisi Yok
            </Button>
          ) : (
            <Link href="/yonetim">
              <Button
                size="sm"
                variant="outline"
                className="h-8 text-xs flex items-center gap-1"
              >
                <LogIn className="h-3.5 w-3.5" />
                Giriş Yap
              </Button>
            </Link>
          )}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInput}
            accept=".pdf"
            multiple
            className="hidden"
            disabled={actionLoading}
          />
        </div>
      </div>

      {/* PDF List */}
      <div className="h-[320px] overflow-y-auto p-3">
        {(!localPdfs || localPdfs.length === 0) ? (
          <div className="h-full flex flex-col items-center justify-center">
            {!isAuthenticated ? (
              // Login olmayan kullanıcılar için giriş mesajı
              <>
                <LogIn className="h-10 w-10 text-blue-400 mb-3" />
                <h4 className="text-base font-medium text-gray-900 mb-2">Giriş Yapmalısınız</h4>
                <p className="text-sm text-gray-500 text-center mb-4">PDF'leri görüntülemek için giriş yapın</p>
                <Link href="/yonetim">
                  <Button 
                    size="sm"
                    className="inline-flex items-center gap-2"
                    style={{ backgroundColor: activeColor }}
                  >
                    <LogIn className="h-4 w-4" />
                    Giriş Yap
                  </Button>
                </Link>
              </>
            ) : (
              // Login olan kullanıcılar için PDF yükleme mesajı
              <>
                <File className="h-10 w-10 text-gray-300 mb-2" />
                <p className="text-sm text-gray-500 text-center">Henüz PDF yüklenmedi</p>
                {canEditPDF() ? (
                <button 
                  className="mt-3 text-xs font-medium"
                  style={{ color: activeColor }}
                  onClick={handleButtonClick}
                  disabled={actionLoading}
                >
                  PDF eklemek için tıklayın
                </button>
                ) : (
                  <div className="mt-3 text-center">
                    <p className="text-xs text-red-600 font-medium">
                      {getUserPermissions().warningMessage}
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          <ul className="space-y-2">
            {localPdfs.map((pdf) => (
                              <li 
                  key={pdf.id} 
                  className={`flex items-center justify-between p-2 rounded-lg border ${pdf.isPending ? 'opacity-75' : ''}`}
                  style={{
                    backgroundColor: pdf.is_active ? activeStyles.bg : (pdf.isPending ? "#fef3c7" : "#f9fafb"),
                    borderColor: pdf.is_active ? activeStyles.border : (pdf.isPending ? "#f59e0b" : "#e5e7eb")
                  }}
                >
                                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <File className="h-5 w-5 text-gray-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 truncate">{pdf.dosya_adi}</p>
                        {pdf.isPending && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Bekliyor
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">{formatFileSize(pdf.dosya_boyutu * 1024 * 1024)}</p>
                    </div>
                  </div>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  <select
                    value={pdf.pdf_type}
                    onChange={(e) => handleChangePdfType(pdf.id, e.target.value as 'kural' | 'rol' | 'bilgi' | 'beyan')}
                    className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:border-gray-400 min-w-[60px] h-6"
                    onClick={(e) => e.stopPropagation()}
                    style={{ fontSize: '10px' }}
                    disabled={actionLoading || !canEditPDF()}
                  >
                    <option value="beyan">🚨 Beyan</option>
                    <option value="rol">🔴 Rol</option>
                    <option value="kural">🔴 Kural</option>
                    <option value="bilgi">📘 Bilgi</option>
                  </select>
                  <button
                    className={`p-1 rounded-full ${canEditPDF() ? 'hover:bg-gray-100' : 'cursor-not-allowed opacity-50'}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (canEditPDF()) {
                      handleToggleActive(pdf.id)
                      }
                    }}
                    title={canEditPDF() ? (pdf.is_active ? "Pasif yap" : "Aktif yap") : "Düzenleme yetkisi yok"}
                    style={{
                      color: pdf.is_active ? activeColor : "#9ca3af"
                    }}
                    disabled={actionLoading || !canEditPDF()}
                  >
                    {actionLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    className={`p-1 rounded-full text-gray-400 ${canEditPDF() ? 'hover:text-red-500 hover:bg-gray-100' : 'cursor-not-allowed opacity-50'}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (canEditPDF()) {
                      handleRemovePdf(pdf.id)
                      }
                    }}
                    title={canEditPDF() ? "Kaldır" : "Düzenleme yetkisi yok"}
                    disabled={actionLoading || !canEditPDF()}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Sisteme Yükle Butonu */}
      <div className="p-3 border-t border-gray-200">
        {isAuthenticated && canEditPDF() ? (
          <Button
            className="w-full"
            disabled={!hasChanges || actionLoading}
            style={{
              backgroundColor: !hasChanges || actionLoading
                ? "#9ca3af" 
                : activeColor
            }}
            onClick={handleSystemUpload}
          >
            {actionLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                İşleniyor...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                {hasChanges 
                  ? `Değişiklikleri Kaydet (${pendingChanges.uploads.length + pendingChanges.updates.length + pendingChanges.deletes.length + pendingChanges.toggles.length} işlem)`
                  : "Sisteme Yükle"
                }
              </>
            )}
          </Button>
        ) : isAuthenticated ? (
          <div className="w-full bg-red-50 border border-red-200 rounded-lg p-3 text-center">
            <p className="text-sm text-red-700 font-medium">
              {getUserPermissions().warningMessage}
            </p>
            <p className="text-xs text-red-600 mt-1">
              PDF düzenleme yapabilmek için gerekli paket türünde olmalısınız.
            </p>
          </div>
        ) : (
          <Link href="/yonetim" className="block">
            <Button
              className="w-full inline-flex items-center justify-center gap-2"
              variant="outline"
            >
              <LogIn className="h-4 w-4" />
              Giriş Yapmalısınız
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
} 