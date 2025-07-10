"use client"

import { useState, useRef } from 'react'
import { api } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Upload, FileText, Trash2, Loader2, AlertTriangle, CheckCircle, Info, PlusCircle, X, LogIn } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface PDF {
  id: number;
  dosya_adi: string;
  pdf_type: string;
  is_active: boolean;
}

interface PDFUploaderProps {
  activeColor: string;
  robotId: number;
  initialPdfs: PDF[];
  refetchPdfs: () => void;
}

export default function PDFUploader({ activeColor, robotId, initialPdfs, refetchPdfs }: PDFUploaderProps) {
  const [loadingAction, setLoadingAction] = useState<{ type: string; id: number | null } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoadingAction({ type: 'upload', id: null });
    try {
      await api.robots.uploadPdf(robotId, file);
      toast({ title: "Başarılı!", description: `"${file.name}" başarıyla yüklendi.` });
      refetchPdfs();
    } catch (error: any) {
      toast({
        title: "Yükleme Başarısız",
        description: error.response?.data?.error || "Dosya yüklenirken bir hata oluştu.",
        variant: "destructive",
      });
    } finally {
      setLoadingAction(null);
      if(fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDelete = async (pdf: PDF) => {
    setLoadingAction({ type: 'delete', id: pdf.id });
    try {
      await api.robots.deletePdf(pdf.id);
      toast({ title: "Başarıyla Silindi", description: `"${pdf.dosya_adi}" adlı dosya silindi.` });
      refetchPdfs();
    } catch (error: any) {
      toast({
        title: "Silme Başarısız",
        description: error.response?.data?.detail || "Dosya silinirken bir hata oluştu.",
        variant: "destructive",
      });
    } finally {
      setLoadingAction(null);
    }
  };

  const handleToggleActive = async (pdf: PDF) => {
    setLoadingAction({ type: 'toggle', id: pdf.id });
    try {
      await api.robots.togglePdfActive(pdf.id);
      toast({ title: "Durum Güncellendi", description: `"${pdf.dosya_adi}" dosyasının durumu değiştirildi.` });
      refetchPdfs();
    } catch (error: any) {
      toast({ title: "Hata", description: "Durum güncellenirken bir hata oluştu.", variant: "destructive" });
    } finally {
      setLoadingAction(null);
    }
  };

  const handleChangeType = async (pdf: PDF, newType: string) => {
    setLoadingAction({ type: 'type', id: pdf.id });
    try {
      await api.robots.changePdfType(pdf.id, newType);
      toast({ title: "Tür Güncellendi", description: `"${pdf.dosya_adi}" dosyasının türü değiştirildi.` });
      refetchPdfs();
    } catch (error: any) {
      toast({ title: "Hata", description: "Tür güncellenirken bir hata oluştu.", variant: "destructive" });
    } finally {
      setLoadingAction(null);
    }
  };
  
  const isLoading = (type: string, id: number | null) => loadingAction?.type === type && (id === null || loadingAction?.id === id);


  return (
    <div className="w-full h-full p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="mb-4 flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-800">PDF Dosyaları</h3>
        <Button size="sm" onClick={() => fileInputRef.current?.click()} disabled={!!loadingAction} style={{ backgroundColor: activeColor }}>
          {isLoading('upload', null) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PlusCircle className="mr-2 h-4 w-4" />}
          {isLoading('upload', null) ? 'Yükleniyor...' : 'PDF Ekle'}
          </Button>
        <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".pdf" className="hidden" />
      </div>

      <div className="max-h-[300px] overflow-y-auto p-1 pr-3">
        {initialPdfs.length > 0 ? (
          <ul className="space-y-3">
            {initialPdfs.map((pdf) => (
              <li 
                key={pdf.id} 
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${!pdf.is_active && 'bg-gray-50 border-gray-200'}`}
                style={pdf.is_active ? { backgroundColor: `${activeColor}1A`, borderColor: activeColor } : {}}
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <FileText className="h-5 w-5 text-gray-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate" title={pdf.dosya_adi}>{pdf.dosya_adi}</p>
                    {pdf.is_active && (
                      <div className="flex items-center space-x-1 mt-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-xs text-green-600">RAG Active</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  <select
                    value={pdf.pdf_type}
                     onChange={(e) => handleChangeType(pdf, e.target.value)}
                     className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 h-8"
                     disabled={!!loadingAction}
                   >
                     <option value="bilgi">Bilgi</option>
                     <option value="kural">Kural</option>
                     <option value="rol">Rol</option>
                     <option value="beyan">Beyan</option>
                  </select>

                  <Button variant="ghost" size="icon" onClick={() => handleToggleActive(pdf)} disabled={!!loadingAction} title={pdf.is_active ? "Pasif Yap" : "Aktif Yap"}>
                    {isLoading('toggle', pdf.id) ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className={`h-5 w-5 transition-colors ${!pdf.is_active && 'text-gray-400'}`} style={pdf.is_active ? { color: activeColor } : {}}/>}
                  </Button>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="ghost" size="icon" disabled={!!loadingAction} title="Sil">
                        {isLoading('delete', pdf.id) ? <Loader2 className="h-4 w-4 animate-spin text-red-500" /> : <Trash2 className="h-5 w-5 text-gray-400 hover:text-red-500 transition-colors" />}
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Emin misiniz?</AlertDialogTitle>
                        <AlertDialogDescription>
                          "{pdf.dosya_adi}" dosyasını kalıcı olarak silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>İptal</AlertDialogCancel>
                        <AlertDialogAction onClick={() => handleDelete(pdf)} className="bg-red-600 hover:bg-red-700">Evet, Sil</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center text-gray-500 py-16">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-4">Henüz PDF yüklenmemiş.</p>
            <p className="text-sm text-gray-400">Başlamak için "PDF Ekle" düğmesini kullanın.</p>
          </div>
        )}
      </div>
    </div>
  )
} 