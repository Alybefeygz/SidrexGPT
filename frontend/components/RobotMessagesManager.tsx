"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trash2, Plus, Edit2, Check, X, GripVertical } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import api from "@/lib/api"

interface RobotMessage {
  id: number
  message: string
  isEditing?: boolean
}

interface RobotMessagesManagerProps {
  activeColor: string
  robotId: string | number
  refetchMessages?: () => void
  onMessagesUpdate?: (messages: string[]) => void
}

export default function RobotMessagesManager({
  activeColor,
  robotId,
  refetchMessages,
  onMessagesUpdate
}: RobotMessagesManagerProps) {
  const [messages, setMessages] = useState<RobotMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [editingMessage, setEditingMessage] = useState("")
  const { toast } = useToast()

  // API'den mesajları yükle
  const fetchMessages = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/robots/${robotId}/messages/`)
      const messagesWithIds = response.data.messages.map((msg: string, index: number) => ({
        id: index + 1,
        message: msg,
        isEditing: false
      }))
      setMessages(messagesWithIds)
    } catch (error: any) {
      console.error('Mesajlar yüklenirken hata:', error)
      toast({
        title: "Hata",
        description: error.response?.data?.detail || "Mesajlar yüklenirken bir hata oluştu",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // Backend'e mesajları güncelle (helper function)
  const updateBackendMessages = async (messageTexts: string[]) => {
    try {
      await api.put(`/robots/${robotId}/messages/`, {
        messages: messageTexts
      })
      
      // Parent component'i güncelle
      if (onMessagesUpdate) {
        onMessagesUpdate(messageTexts)
      }
      
      if (refetchMessages) {
        refetchMessages()
      }
      
      return true
    } catch (error: any) {
      console.error('Mesajlar güncellenirken hata:', error)
      toast({
        title: "Hata",
        description: error.response?.data?.detail || "Mesajlar güncellenirken bir hata oluştu",
        variant: "destructive",
      })
      return false
    }
  }


  // Yeni mesaj ekle
  const addMessage = () => {
    if (messages.length >= 5) {
      toast({
        title: "Limit Aşıldı",
        description: "Maksimum 5 mesaj ekleyebilirsiniz.",
        variant: "destructive",
      })
      return
    }

    const newMessage: RobotMessage = {
      id: Date.now(), // Geçici ID
      message: "",
      isEditing: true
    }
    setMessages([...messages, newMessage])
    setEditingMessage("")
  }

  // Mesaj sil ve backend'i güncelle
  const deleteMessage = async (id: number) => {
    const updatedMessages = messages.filter(m => m.id !== id)
    setMessages(updatedMessages)
    
    // Backend'e değişikliği gönder
    await updateBackendMessages(updatedMessages.map(m => m.message).filter(msg => msg.trim() !== ''))
  }

  // Mesaj düzenlemeyi başlat
  const startEditing = (id: number) => {
    const message = messages.find(m => m.id === id)
    if (message) {
      setEditingMessage(message.message)
      setMessages(messages.map(m => 
        m.id === id ? { ...m, isEditing: true } : { ...m, isEditing: false }
      ))
    }
  }

  // Mesaj düzenlemeyi kaydet ve backend'i güncelle
  const saveEdit = async (id: number) => {
    if (editingMessage.trim() === "") {
      toast({
        title: "Hata",
        description: "Mesaj boş olamaz.",
        variant: "destructive",
      })
      return
    }

    if (editingMessage.length > 200) {
      toast({
        title: "Hata",
        description: "Mesaj 200 karakterden uzun olamaz.",
        variant: "destructive",
      })
      return
    }

    const updatedMessages = messages.map(m => 
      m.id === id 
        ? { ...m, message: editingMessage.trim(), isEditing: false }
        : m
    )
    
    setMessages(updatedMessages)
    setEditingMessage("")
    
    // Backend'e değişikliği gönder
    await updateBackendMessages(updatedMessages.map(m => m.message).filter(msg => msg.trim() !== ''))
  }

  // Mesaj düzenlemeyi iptal et
  const cancelEdit = async (id: number) => {
    // Eğer yeni eklenen mesaj ise sil
    const message = messages.find(m => m.id === id)
    if (message && message.message === "") {
      await deleteMessage(id)
    } else {
      setMessages(messages.map(m => 
        m.id === id ? { ...m, isEditing: false } : m
      ))
    }
    setEditingMessage("")
  }

  // Mesajları sürükle-bırak ile sırala ve backend'i güncelle
  const moveMessage = async (fromIndex: number, toIndex: number) => {
    const newMessages = [...messages]
    const [movedMessage] = newMessages.splice(fromIndex, 1)
    newMessages.splice(toIndex, 0, movedMessage)
    setMessages(newMessages)
    
    // Backend'e sıralama değişikliğini gönder
    await updateBackendMessages(newMessages.map(m => m.message).filter(msg => msg.trim() !== ''))
  }

  useEffect(() => {
    fetchMessages()
  }, [robotId])

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle style={{ color: activeColor }}>Robot Mesajları</CardTitle>
          <CardDescription>
            ZZEN robot için özel mesajları yönetebilirsiniz
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="text-lg">Mesajlar yükleniyor...</div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle style={{ color: activeColor }}>Robot Mesajları</CardTitle>
            <CardDescription>
              ZZEN robot için özel mesajları yönetebilirsiniz (maksimum 5 adet)
            </CardDescription>
          </div>
          <Badge variant="secondary">
            {messages.length}/5
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Mesaj Listesi */}
          {messages.map((message, index) => (
            <div
              key={message.id}
              className="flex items-center gap-3 p-4 border rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              {/* Sürükleme Handle */}
              <div className="cursor-grab active:cursor-grabbing">
                <GripVertical className="w-4 h-4 text-gray-400" />
              </div>

              {/* Mesaj İçeriği */}
              <div className="flex-1">
                {message.isEditing ? (
                  <div className="flex items-center gap-2">
                    <Input
                      value={editingMessage}
                      onChange={(e) => setEditingMessage(e.target.value)}
                      placeholder="Robot mesajını yazın..."
                      className="flex-1"
                      maxLength={200}
                      onKeyPress={async (e) => {
                        if (e.key === 'Enter') {
                          await saveEdit(message.id)
                        }
                      }}
                    />
                    <div className="flex items-center gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={async () => await saveEdit(message.id)}
                        className="p-1"
                      >
                        <Check className="w-4 h-4 text-green-600" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={async () => await cancelEdit(message.id)}
                        className="p-1"
                      >
                        <X className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 flex-1">
                      <img src="/images/moon.png" alt="moon" className="w-5 h-5" />
                      <span className="text-sm font-medium">
                        {message.message || "Boş mesaj"}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => startEditing(message.id)}
                        className="p-1"
                      >
                        <Edit2 className="w-4 h-4 text-blue-600" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={async () => await deleteMessage(message.id)}
                        className="p-1"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Yeni Mesaj Ekle */}
          {messages.length < 5 && (
            <Button
              onClick={addMessage}
              variant="outline"
              className="w-full border-dashed"
              style={{ borderColor: activeColor, color: activeColor }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Yeni Mesaj Ekle
            </Button>
          )}

          {/* Bilgi Metni */}
          <div className="text-xs text-gray-500 pt-4 border-t">
            <p>💡 Bu mesajlar robot'a tıklandığında rastgele olarak gösterilir.</p>
            <p>📝 Her mesaj maksimum 200 karakter olabilir.</p>
            <p>🎯 Bu özellik sadece ZZEN robot için kullanılabilir.</p>
            <p>⚡ Değişiklikler otomatik olarak kaydedilir.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}