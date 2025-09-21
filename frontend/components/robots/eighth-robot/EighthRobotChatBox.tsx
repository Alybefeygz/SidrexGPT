"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import { Send } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { useIsMobile } from "../../../hooks/use-mobile"

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
  status?: 'loading' | 'ok' | 'error'
  citations?: any[]
  context_used?: boolean
}

interface EighthRobotChatBoxProps {
  messages: Message[]
  inputValue: string
  setInputValue: (value: string) => void
  sendMessage: () => void
  handleKeyPress: (e: React.KeyboardEvent) => void
  onClose: () => void
  position: { top: number; left: number }
  isFloating?: boolean
  isLoading?: boolean
}

export default function EighthRobotChatBox({
  messages,
  inputValue,
  setInputValue,
  sendMessage,
  handleKeyPress,
  onClose,
  position,
  isFloating = false,
  isLoading = false,
}: EighthRobotChatBoxProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()
  
  const [dimensions, setDimensions] = useState({ width: 384, height: 480 })
  
  useEffect(() => {
    const updateDimensions = () => {
      const screenWidth = window.innerWidth
      
      if (screenWidth < 500) {
        const scale = screenWidth / 500
        setDimensions({
          width: Math.max(280, 384 * scale),
          height: Math.max(360, 480 * scale),
        })
      } else {
        setDimensions({ width: 384, height: 480 })
      }
    }
    
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  useEffect(() => {
    if (messagesEndRef.current) {
      const chatContainer = messagesEndRef.current.closest('.overflow-y-auto')
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight
      }
    }
  }, [messages])

  return (
    <div
      className={`markamind-chatbox z-50 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col animate-in slide-in-from-bottom-2 duration-300 ${
        isFloating ? "fixed bottom-4" : "absolute"
      }`}
      style={
        !isFloating
          ? {
              top: `${position.top}px`,
              left: `${position.left}px`,
              width: `${dimensions.width}px`,
              height: `${dimensions.height}px`,
            }
          : {
              width: `${dimensions.width}px`,
              height: `${dimensions.height}px`,
              right: '150px',
            }
      }
    >
      {/* Chat Header */}
      <div
        className="text-white p-5 rounded-t-lg flex justify-between items-center"
        style={{ backgroundColor: "#D9E60D" }}
      >
        <h3 className="font-semibold text-lg">Olivia SidrexGPT</h3>
        <button onClick={onClose} className="text-white hover:text-gray-200 text-xl">
          ×
        </button>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 p-5 overflow-y-auto bg-gray-50">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] p-4 rounded-lg shadow-sm ${
                  message.isUser
                    ? "text-white rounded-br-none"
                    : "bg-white text-gray-700 rounded-bl-none"
                } ${message.status === 'error' ? 'bg-red-100 text-red-700' : ''}`}
                style={message.isUser ? { backgroundColor: "#D9E60D" } : {}}
              >
                {message.status === 'loading' ? (
                  <p className="text-sm flex items-center space-x-1">
                    <span className="animate-bounce">.</span>
                    <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>.</span>
                    <span className="animate-bounce" style={{ animationDelay: "0.4s" }}>.</span>
                  </p>
                ) : (
                  <div className="text-sm">
                    {message.isUser ? (
                      message.text
                    ) : (
                      <ReactMarkdown
                        components={{
                          strong: ({ node, ...props }) => <span className="font-bold" {...props} />,
                        }}
                      >
                        {message.text}
                      </ReactMarkdown>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      <div className="p-5 border-t border-gray-200 bg-white rounded-b-lg">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:border-transparent"
            style={{ 
              '--tw-ring-color': '#D9E60D'
            } as React.CSSProperties & { '--tw-ring-color': string }}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="w-12 h-12 rounded-full hover:opacity-90 transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: "#D9E60D", color: "white" }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}