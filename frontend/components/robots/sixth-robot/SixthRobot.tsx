"use client"

import React, { useState, useRef, useEffect, useCallback, memo } from "react"
import { toast } from "sonner"
import { useRobotChat } from "@/hooks/use-api"
import { useIsMobile } from "@/hooks/use-mobile"
import { useWidgetCommunication } from "@/hooks/use-widget-communication"
import SixthRobotChatBox from "./SixthRobotChatBox"

interface SixthRobotProps {
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

// ⚡ PERFORMANS: Memoized component
const SixthRobot = memo(function SixthRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: SixthRobotProps) {
  // Mobile detection
  const isMobile = useIsMobile()
  
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **Repro Women's Once Daily SidrexGPT**. Kadın sağlığınızı desteklemek için **folat**, **demir**, **kalsiyum** ve **D vitamini** ile güçlendirilmiş formülümle **reproduktif sağlığınızı** destekliyorum!",
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

  // Animation state
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  // Robot Chat API integration
  const { sendMessage: sendChatMessage, loading: chatLoading } = useRobotChat('repro-womens')

  // Widget Communication Hook
  const { notifyRobotClicked, notifyOpenChatbox, notifyCloseChatbox } = useWidgetCommunication()

  // ⚡ PERFORMANS: Memoized callbacks
  const handleChatToggle = useCallback((robotId: string, isOpen: boolean) => {
    onChatToggle(robotId, isOpen)
  }, [onChatToggle])

  // Close chat when other chat opens
  useEffect(() => {
    if (isOtherChatOpen && isChatOpen) {
      setIsChatOpen(false)
      setIsHovered(false)
    }
  }, [isOtherChatOpen, isChatOpen])

  // Calculate responsive dimensions for chatbox
  const calculateChatboxDimensions = () => {
    const screenWidth = window.innerWidth
    let chatboxWidth = 384
    let chatboxHeight = 480
    
    if (screenWidth < 500) {
      const scale = screenWidth / 500
      chatboxWidth = Math.max(280, 384 * scale)
      chatboxHeight = Math.max(360, 480 * scale)
    }
    
    return { chatboxWidth, chatboxHeight }
  }

  // Update chatbox position when mobile state changes while chat is open
  useEffect(() => {
    if (isChatOpen && !isFloating && buttonRef.current) {
      if (isMobile) {
        // Mobile: center chatbox on screen with 1px right offset
        const rect = buttonRef.current.getBoundingClientRect()
        const screenHeight = window.innerHeight
        const screenWidth = window.innerWidth
        
        // Calculate responsive dimensions using centralized function
        const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
        
        const verticalCenter = screenHeight / 2
        const horizontalCenter = screenWidth / 2
        const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140 // 140px higher (60px down from previous)
        const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1 // Center + 1px right offset
        
        setChatPosition({
          top: chatboxTop - rect.top - window.scrollY,
          left: chatboxLeft - rect.left - window.scrollX,
        })
      } else {
        // Desktop: original position
        setChatPosition({
          top: -390,
          left: -420,
        })
      }
    }
  }, [isMobile, isChatOpen, isFloating])

  // ⚡ PERFORMANS: Memoized sendMessage function
  const sendMessage = useCallback(async () => {
    if (inputValue.trim() === "" || chatLoading) {
      return;
    }

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
      status: 'ok',
    };

    const loadingMessage: Message = {
        id: Date.now() + 1,
        text: "...",
        isUser: false,
        timestamp: new Date(),
        status: 'loading',
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    const messageText = inputValue;
    setInputValue("");

    try {
      const response = await sendChatMessage(messageText) as ChatResponse;
      
      // DEBUG: Gelen yanıtın gerçek yapısını görmek için konsola yazdır
      console.log("Final response received in component:", response);

      if (response && (response as any).robot_response) {
        const botResponse: Message = {
          id: loadingMessage.id,
          text: (response as any).robot_response,
          isUser: false,
          timestamp: new Date(),
          status: 'ok',
          citations: (response as any).citations || [],
          context_used: (response as any).context_used || false,
        };
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? botResponse : msg));
      } else {
        const errorResponse: Message = {
            id: loadingMessage.id,
            text: "Yanıt alınamadı, lütfen tekrar deneyin.",
            isUser: false,
            timestamp: new Date(),
            status: 'error',
        };
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      toast.error(error.message || 'Mesaj gönderilemedi');
      
      const errorResponse: Message = {
        id: loadingMessage.id,
        text: "Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
        isUser: false,
        timestamp: new Date(),
        status: 'error',
      };
      setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
    }
  }, [inputValue, chatLoading, sendChatMessage, setMessages, setInputValue]);

  // ⚡ PERFORMANS: Memoized handleKeyPress
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }, [sendMessage])

  // ⚡ PERFORMANS: Memoized toggleChat
  const toggleChat = useCallback(() => {
    const newChatState = !isChatOpen
    
    // İlk robot tıklanması - widget communication başlat
    if (!isChatOpen) {
      // Robot tıklandı bildirimi gönder
      notifyRobotClicked()
      
      if (buttonRef.current && !isFloating) {
        // For iframe context, position chatbox relative to robot
        if (isMobile) {
          // Mobile: center chatbox on screen with 1px right offset
          const rect = buttonRef.current.getBoundingClientRect()
          const screenHeight = window.innerHeight
          const screenWidth = window.innerWidth
          
          // Calculate responsive dimensions using centralized function
          const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
          
          const verticalCenter = screenHeight / 2
          const horizontalCenter = screenWidth / 2
          const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140 // 140px higher (60px down from previous)
          const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1 // Center + 1px right offset
          
          setChatPosition({
            top: chatboxTop - rect.top - window.scrollY,
            left: chatboxLeft - rect.left - window.scrollX,
          })
        } else {
          // Desktop: original position
          setChatPosition({
            top: -390,
            left: -420,
          })
        }
      }
      
      // Chatbox açılma bildirimi gönder
      notifyOpenChatbox()
    } else {
      // Chatbox kapatılıyor - kapatma bildirimi gönder
      notifyCloseChatbox()
    }
    
    setIsChatOpen(newChatState)
    handleChatToggle("sixth", newChatState)
  }, [isChatOpen, isFloating, handleChatToggle, isMobile, notifyRobotClicked, notifyOpenChatbox, notifyCloseChatbox])

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
        className={`w-24 h-24 rounded-full shadow-2xl hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer flex items-center justify-center relative overflow-visible ${
          isChatOpen || isHovered ? "sixth-robot-active" : ""
        }`}
        style={{
          backgroundColor: "#FFDAEF",
          border: "2px solid #E78EEB",
        }}
      >
        {/* Heart Icon for Women's Health */}
        <div className="robot-heart-icon">
          <div className="heart-body">
            <div className="heart-pulse"></div>
          </div>
        </div>

        {/* Sixth Robot Mascot */}
        <div className={`robot-mascot-container ${isChatOpen || isHovered ? "sixth-active" : ""}`}>
          <div className="robot-sixth-background-glow"></div>
          <div className="robot-antenna-sixth"></div>
          <div className="robot-sixth-hover-antenna"></div>
          <div className="robot-head-sixth">
            <div className="robot-ear-sixth robot-ear-left"></div>
            <div className="robot-ear-sixth robot-ear-right"></div>
            <div className="robot-face-sixth">
              <div className="robot-sixth-sleepy-eyes"></div>
              <div className="robot-sixth-hover-eyes"></div>
              <div className="robot-sixth-hover-main-eyes"></div>
              <div className="robot-sixth-sleepy-mouth"></div>
              <div className="robot-sixth-hover-mouth"></div>
            </div>
          </div>
        </div>

        {/* Hover durumunda çıkan çimen görselleri - robot kafasından bağımsız */}
        <div className="robot-sixth-hover-grass"></div>
        <div className="robot-sixth-hover-grass-2"></div>
        <div className="robot-sixth-hover-grass-3"></div>
        
        {/* Hover durumunda çıkan çiçek görselleri - çimen görsellerinin üstünde */}
        <div className="robot-sixth-hover-flower"></div>
        <div className="robot-sixth-hover-flower-left"></div>
        <div className="robot-sixth-hover-flower-right"></div>

        {/* Flower decorations for women's theme */}
        <div className="robot-flower-decorations">
          <div className="flower-petals top-left"></div>
          <div className="flower-petals top-right"></div>
          <div className="flower-petals bottom-left"></div>
          <div className="flower-petals bottom-right"></div>
        </div>
      </button>

      {/* Chat Box */}
      {isChatOpen && (
        <SixthRobotChatBox
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
          onClose={() => {
            setIsChatOpen(false)
            setIsHovered(false)
            // Chatbox kapandığında parent'a bildir
            notifyCloseChatbox()
            handleChatToggle("sixth", false)
          }}
          position={chatPosition}
          isFloating={isFloating}
          isLoading={chatLoading}
        />
      )}
    </div>
  )
})

export default SixthRobot