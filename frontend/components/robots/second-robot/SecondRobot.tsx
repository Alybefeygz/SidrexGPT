"use client"

import React, { useState, useRef, useEffect, useCallback, memo } from "react"
import { toast } from "sonner"
import { useRobotChat } from "@/hooks/use-api"
import SecondRobotChatBox from "./SecondRobotChatBox"

interface SecondRobotProps {
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
const SecondRobot = memo(function SecondRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: SecondRobotProps) {
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **yorgun** **SidrexGPT**. Kaslarımı destekleyip **enerjimi** geri kazanmamı sağlayan **magnezyum** desteğiyle **yorgunluğu** geride bırakıyorum!",
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
  const { sendMessage: sendChatMessage, loading: chatLoading } = useRobotChat('sidrexgpt-mag')

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
    if (!isChatOpen && buttonRef.current && !isFloating) {
      // For iframe context, position chatbox relative to robot
      setChatPosition({
        top: -390, // Position another 50px lower
        left: -420, // Position to the left of robot
      })
    }
    const newChatState = !isChatOpen
    setIsChatOpen(newChatState)
    handleChatToggle("second", newChatState)
  }, [isChatOpen, isFloating, handleChatToggle])

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
          isChatOpen || isHovered ? "second-robot-active" : ""
        }`}
        style={{
          backgroundColor: "#F2EDFF",
          border: "2px solid #6D71B6",
        }}
      >
        {/* Battery Icon */}
        <div className="robot-battery">
          <div className="battery-body">
            <div className="battery-fill"></div>
            <div className="battery-terminal"></div>
          </div>
        </div>

        {/* Second Robot Mascot */}
        <div className={`robot-mascot-container ${isChatOpen || isHovered ? "second-active" : ""}`}>
          <div className="robot-head-second">
            <div className="robot-antenna-purple"></div>
            <div className="robot-ear-second robot-ear-left"></div>
            <div className="robot-ear-second robot-ear-right"></div>
            <div className="robot-face-second">
              <div className="robot-eye-semicircle-second left"></div>
              <div className="robot-eye-semicircle-second right"></div>
              <div className="robot-eye-oval left"></div>
              <div className="robot-eye-oval right"></div>
              <div className="robot-mouth-oval"></div>
              <div className="robot-mouth-overlay"></div>
              <div className="robot-eye-white left"></div>
              <div className="robot-eye-white right"></div>
              <div className="robot-smile-white"></div>
            </div>
          </div>
        </div>
      </button>

      {/* Chat Box */}
      {isChatOpen && (
        <SecondRobotChatBox
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
          onClose={() => {
            setIsChatOpen(false)
            setIsHovered(false)
          }}
          position={chatPosition}
          isFloating={isFloating}
          isLoading={chatLoading}
        />
      )}
    </div>
  )
})

export default SecondRobot
