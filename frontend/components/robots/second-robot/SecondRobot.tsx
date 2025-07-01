"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import SecondRobotChatBox from "./SecondRobotChatBox"
import { useRobotChat } from "../../../hooks/use-api"
import { toast } from "sonner"

interface SecondRobotProps {
  onChatToggle: (robotId: string, isOpen: boolean) => void
  isOtherChatOpen: boolean
  isFloating?: boolean
}

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
}

export default function SecondRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: SecondRobotProps) {
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **yorgun** **SidrexGPT**. Kaslarımı destekleyip **enerjimi** geri kazanmamı sağlayan **magnezyum** desteğiyle **yorgunluğu** geride bırakıyorum!",
      isUser: false,
      timestamp: new Date(),
    },
    {
      id: 2,
      text: "Size nasıl yardımcı olabilirim?",
      isUser: false,
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [chatPosition, setChatPosition] = useState({ top: 0, left: 0 })

  // Animation state
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  // Robot Chat API integration
  const { sendMessage: sendChatMessage, isLoading: chatLoading, error: chatError, clearError } = useRobotChat('sidrexgpt-mag')

  // Close chat when other chat opens
  useEffect(() => {
    if (isOtherChatOpen && isChatOpen) {
      setIsChatOpen(false)
      setIsHovered(false)
    }
  }, [isOtherChatOpen, isChatOpen])

  const sendMessage = async () => {
    if (inputValue.trim() === "" || chatLoading) return

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
    }

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage])
    const messageText = inputValue
    setInputValue("")

    try {
      // Send message to backend
      const response = await sendChatMessage(messageText)
      
      if (response && response.robot_response) {
        const botResponse: Message = {
          id: Date.now() + 1,
          text: response.robot_response,
          isUser: false,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, botResponse])
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error(error.message || 'Mesaj gönderilemedi')
      
      // Add error message
      const errorResponse: Message = {
        id: Date.now() + 1,
        text: "Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
        isUser: false,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorResponse])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }

  const toggleChat = () => {
    if (!isChatOpen && buttonRef.current && !isFloating) {
      const rect = buttonRef.current.getBoundingClientRect()
      setChatPosition({
        top: rect.bottom - 480 + window.scrollY,
        left: rect.left - 450 + window.scrollX,
      })
    }
    const newChatState = !isChatOpen
    setIsChatOpen(newChatState)
    onChatToggle("second", newChatState)
  }

  return (
    <>
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
    </>
  )
}
