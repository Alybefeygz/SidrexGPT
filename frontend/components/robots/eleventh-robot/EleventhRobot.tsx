"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import EleventhRobotChatBox from "./EleventhRobotChatBox"
import { useRobotChat } from "../../../hooks/use-api"
import { useWidgetCommunication } from "../../../hooks/use-widget-communication"
import { toast } from "sonner"

interface EleventhRobotProps {
  onChatToggle: (robotId: string, isOpen: boolean) => void
  isOtherChatOpen: boolean
  isFloating?: boolean
}

interface ChatResponse {
  answer: string;
  citations?: any[];
  context_used?: boolean;
  response_time?: number;
  session_id?: string;
}

interface Citation {
  source: string
  content: string
  similarity: number
  chunk_index: number
  pdf_type: string
}

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
  status?: 'loading' | 'ok' | 'error'
  citations?: Citation[]
  context_used?: boolean
}

export default function EleventhRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: EleventhRobotProps) {
  
  // Chat state - SSR-safe localStorage persistence
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [isHydrated, setIsHydrated] = useState(false)

  // Hydration sonrası localStorage'dan state'i yükle
  useEffect(() => {
    setIsHydrated(true)
    if (typeof window !== 'undefined') {
      const savedState = localStorage.getItem('kalkan-chat-state') === 'open'
      setIsChatOpen(savedState)
    }
  }, [])
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **Kalkan SidrexGPT**. **Kalkan** ürününün özel asistanıyım! Koruma ve destek konusunda size yardımcı oluyorum!",
      isUser: false,
      timestamp: new Date(),
      status: 'ok'
    },
    {
      id: 2,
      text: "Size nasıl yardımcı olabilirim?",
      isUser: false,
      timestamp: new Date(),
      status: 'ok'
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [chatPosition, setChatPosition] = useState({ top: 0, left: 0 })

  // Robot Chat API integration
  const { sendMessage: sendChatMessage, loading: chatLoading } = useRobotChat('kalkan')

  // Widget Communication Hook
  const { notifyRobotClicked, notifyOpenChatbox, notifyCloseChatbox } = useWidgetCommunication()

  // PostMessage listener - Parent'dan gelen komutları dinle
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data === 'forceOpenChatbox') {
        console.log("📨 Received forceOpenChatbox from parent")
        setIsChatOpen(true)
        if (typeof window !== 'undefined') {
          localStorage.setItem('kalkan-chat-state', 'open')
        }
      } else if (event.data === 'forceCloseChatbox') {
        console.log("📨 Received forceCloseChatbox from parent")  
        setIsChatOpen(false)
        setIsHovered(false) // Robot uyku moduna geçsin
        if (typeof window !== 'undefined') {
          localStorage.setItem('kalkan-chat-state', 'closed')
        }
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  // Animation state
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  // Close chat when other chat opens
  useEffect(() => {
    if (isOtherChatOpen && isChatOpen) {
      setIsChatOpen(false)
      setIsHovered(false) // Robot uyku moduna geçsin
      if (typeof window !== 'undefined') {
        localStorage.setItem('kalkan-chat-state', 'closed')
      }
    }
  }, [isOtherChatOpen, isChatOpen])


  // Update chatbox position when chat is open
  useEffect(() => {
    if (isChatOpen && !isFloating && buttonRef.current) {
      // Desktop: chatbox robot'un solunda (aynı hizada)
      setChatPosition({
        top: -400, // Robot ile aynı hizada (chatbox height 500px - robot 96px farkı)
        left: -420, // Robot'un solunda (chatbox width 400px + gap 20px)
      })
    }
  }, [isChatOpen, isFloating])

  const sendMessage = async () => {
    if (inputValue.trim() === "" || chatLoading) return

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
      status: 'ok'
    }

    const loadingMessage: Message = {
        id: Date.now() + 1,
        text: "...",
        isUser: false,
        timestamp: new Date(),
        status: 'loading',
    }

    setMessages((prev) => [...prev, userMessage, loadingMessage])
    const messageText = inputValue
    setInputValue("")

    try {
      const response = await sendChatMessage(messageText) as ChatResponse
      
      if (response && (response as any).robot_response) {
        const botResponse: Message = {
          id: loadingMessage.id, // Use the same ID to update
          text: (response as any).robot_response,
          isUser: false,
          timestamp: new Date(),
          status: 'ok',
          citations: (response as any).citations || [],
          context_used: (response as any).context_used || false,
        }
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? botResponse : msg))
      } else {
        const errorResponse: Message = {
            id: loadingMessage.id,
            text: "Yanıt alınamadı, lütfen tekrar deneyin.",
            isUser: false,
            timestamp: new Date(),
            status: 'error',
        }
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error(error.message || 'Mesaj gönderilemedi')
      
      const errorResponse: Message = {
        id: loadingMessage.id,
        text: "Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
        isUser: false,
        timestamp: new Date(),
        status: 'error'
      }
      setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }

  const toggleChat = () => {
    if (!isChatOpen) {
      // AÇILIŞ: State'i localStorage'a kaydet
      if (typeof window !== 'undefined') {
        localStorage.setItem('kalkan-chat-state', 'open')
      }
      
      // Iframe büyütme sinyali gönder
      notifyOpenChatbox()
      
      // Chatbox pozisyonunu ayarla (iframe olmayan durumlar için)
      if (buttonRef.current && !isFloating) {
        // Desktop: Chatbox robot'un solunda (aynı hizada)
        setChatPosition({
          top: -400, // Robot ile aynı hizada (chatbox height 500px - robot 96px farkı)
          left: -420, // Robot'un solunda (chatbox width 400px + gap 20px)
        })
      }
      
      // Chatbox'ı aç
      setIsChatOpen(true)
      onChatToggle("eleventh", true)
      
    } else {
      // KAPANIŞ: State'i localStorage'a kaydet
      if (typeof window !== 'undefined') {
        localStorage.setItem('kalkan-chat-state', 'closed')
      }
      
      // Chatbox'ı kapat
      setIsChatOpen(false)
      setIsHovered(false) // Robot uyku moduna geçsin
      onChatToggle("eleventh", false)
      
      // İframe küçültme sinyali gönder
      notifyCloseChatbox()
    }
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={toggleChat}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          if (!isChatOpen) {
            setIsHovered(false)
          }
        }}
        className={`rounded-full shadow-2xl hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer flex items-center justify-center relative overflow-visible ${
          (isChatOpen || isHovered) ? "eleventh-robot-active" : ""
        }`}
        style={{
          width: '96px',  // Sabit boyut - w-24 = 96px
          height: '96px', // Sabit boyut - h-24 = 96px
          backgroundColor: "#F3E5F5",
          border: "2px solid #9C27B0",
        }}
      >
        {/* Z harfleri for third robot only - positioned in top-right corner */}
        <div className="absolute -top-2 -right-2 pointer-events-none third-robot-z">
          {/* Ana Z - en küçük */}
          <div
            className="absolute w-4 h-4 flex items-center justify-center text-yellow-400 font-bold text-sm"
            style={{ top: "0px", right: "0px" }}
          >
            Z
          </div>
          {/* Üst Z - normal boyut */}
          <div
            className="absolute w-6 h-6 flex items-center justify-center text-yellow-400 font-bold text-lg"
            style={{ top: "-20px", right: "-12px" }}
          >
            Z
          </div>
          {/* Orta Z - biraz küçük */}
          <div
            className="absolute w-5 h-5 flex items-center justify-center text-yellow-400 font-bold text-base"
            style={{ top: "-16px", right: "12px" }}
          >
            Z
          </div>
        </div>
        {/* Robot Mascot - TenthRobot yapısı gibi */}
        <div className={`robot-mascot-container ${isChatOpen || isHovered ? "eleventh-active" : ""}`}>
          <div className="robot-antenna-eleventh"></div>
          <div className="robot-head-eleventh">
            {/* Robot Ears */}
            <div className="robot-ear-eleventh robot-ear-left"></div>
            <div className="robot-ear-eleventh robot-ear-right"></div>
            <div className="robot-face-eleventh">
              {/* Eleventh robot eyes */}
              <div className="robot-eleventh-eyes"></div>
              {/* Eleventh robot hover eyes */}
              <div className="robot-eleventh-hover-eyes"></div>
              {/* Eleventh robot mouth */}
              <div className="robot-eleventh-mouth"></div>
            </div>
          </div>
        </div>
        {/* Kalkan mascots - independent from robot head movements */}
        <div className="robot-eleventh-kalkan"></div>
        <div className="robot-eleventh-hover-kalkan"></div>
      </button>

      {/* Chat Box */}
      {isChatOpen && (
        <EleventhRobotChatBox
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
          onClose={() => {
            setIsChatOpen(false)
            setIsHovered(false) // Robot uyku moduna geçsin
            // localStorage'a da kaydet
            if (typeof window !== 'undefined') {
              localStorage.setItem('kalkan-chat-state', 'closed')
            }
            // Chatbox kapandığında parent'a bildir (sadece X butonundan)
            notifyCloseChatbox()
            onChatToggle("eleventh", false)
          }}
          position={chatPosition}
          isFloating={isFloating}
          isLoading={chatLoading}
        />
      )}
    </div>
  )
}
