"use client"

import React, { useState, useRef, useEffect, useCallback, memo } from "react"
import { toast } from "sonner"
import { useRobotChat } from "@/hooks/use-api"
import { useIsMobile } from "@/hooks/use-mobile"
import EighthRobotChatBox from "./EighthRobotChatBox"

interface EighthRobotProps {
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

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
  status?: 'loading' | 'ok' | 'error'
  citations?: any[]
  context_used?: boolean
}

const EighthRobot = memo(function EighthRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: EighthRobotProps) {
  const isMobile = useIsMobile()
  
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **Olivia SidrexGPT**. **Olivia** ürününün özel asistanıyım!",
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

  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  const { sendMessage: sendChatMessage, loading: chatLoading } = useRobotChat('olivia')

  const handleChatToggle = useCallback((robotId: string, isOpen: boolean) => {
    onChatToggle(robotId, isOpen)
  }, [onChatToggle])

  useEffect(() => {
    if (isOtherChatOpen && isChatOpen) {
      setIsChatOpen(false)
      setIsHovered(false)
    }
  }, [isOtherChatOpen, isChatOpen])

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

  useEffect(() => {
    if (isChatOpen && !isFloating && buttonRef.current) {
      if (isMobile) {
        const rect = buttonRef.current.getBoundingClientRect()
        const screenHeight = window.innerHeight
        const screenWidth = window.innerWidth
        
        const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
        
        const verticalCenter = screenHeight / 2
        const horizontalCenter = screenWidth / 2
        const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140
        const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1
        
        setChatPosition({
          top: chatboxTop - rect.top - window.scrollY,
          left: chatboxLeft - rect.left - window.scrollX,
        })
      } else {
        setChatPosition({
          top: -390,
          left: -420,
        })
      }
    }
  }, [isMobile, isChatOpen, isFloating])

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

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }, [sendMessage])

  const toggleChat = useCallback(() => {
    const newChatState = !isChatOpen
    
    if (!isChatOpen) {
      if (buttonRef.current && !isFloating) {
        if (isMobile) {
          const rect = buttonRef.current.getBoundingClientRect()
          const screenHeight = window.innerHeight
          const screenWidth = window.innerWidth
          
          const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
          
          const verticalCenter = screenHeight / 2
          const horizontalCenter = screenWidth / 2
          const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140
          const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1
          
          setChatPosition({
            top: chatboxTop - rect.top - window.scrollY,
            left: chatboxLeft - rect.left - window.scrollX,
          })
        } else {
          setChatPosition({
            top: -390,
            left: -420,
          })
        }
      }
    }
    
    setIsChatOpen(newChatState)
    handleChatToggle("eighth", newChatState)
  }, [isChatOpen, isFloating, handleChatToggle, isMobile])

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
          isChatOpen || isHovered ? "eighth-robot-active" : ""
        }`}
        style={{
          backgroundColor: "#FFFEB7",
          border: "3px solid #FEDD08",
        }}
      >
        {/* 8. Robot - Bağımsız CSS Sınıfları */}
        <div className={`robot-mascot-container ${isChatOpen || isHovered ? "eighth-active" : ""}`}>
          <div className="robot-antenna-eighth"></div>
          <div className="robot-head-eighth">
            <div className="robot-ear-eighth robot-ear-left"></div>
            <div className="robot-ear-eighth robot-ear-right"></div>
            <div className="robot-face-eighth">
              <div className="robot-eighth-eyes"></div>
              <div className="robot-eighth-hover-eyes"></div>
              <div className="robot-eighth-mouth"></div>
              <div className="robot-eighth-hover-mouth"></div>
            </div>
          </div>
        </div>
        
        {/* Bone mascots - independent from robot head movements */}
        <div className="robot-eighth-bone"></div>
        <div className="robot-eighth-hover-bone"></div>
      </button>

      {/* Chat Box */}
      {isChatOpen && (
        <EighthRobotChatBox
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
          onClose={() => {
            setIsChatOpen(false)
            setIsHovered(false)
            handleChatToggle("eighth", false)
          }}
          position={chatPosition}
          isFloating={isFloating}
          isLoading={chatLoading}
        />
      )}
    </div>
  )
})

export default EighthRobot