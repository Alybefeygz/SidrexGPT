"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import { Send, Heart, BookOpen, Info } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { useIsMobile } from "../../../hooks/use-mobile"

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

interface SixthRobotChatBoxProps {
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

export default function SixthRobotChatBox({
  messages,
  inputValue,
  setInputValue,
  sendMessage,
  handleKeyPress,
  onClose,
  position,
  isFloating = false,
  isLoading = false,
}: SixthRobotChatBoxProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()
  
  // Calculate responsive dimensions
  const [dimensions, setDimensions] = useState({ width: 384, height: 480 })
  
  useEffect(() => {
    const updateDimensions = () => {
      const screenWidth = window.innerWidth
      
      if (screenWidth < 500) {
        // Scale down proportionally for screens under 500px
        const scale = screenWidth / 500
        setDimensions({
          width: Math.max(280, 384 * scale), // Minimum 280px width
          height: Math.max(360, 480 * scale), // Minimum 360px height
        })
      } else {
        // Default dimensions for screens 500px and above
        setDimensions({ width: 384, height: 480 })
      }
    }
    
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Auto-scroll to bottom when new messages arrive - only scroll within chatbox container
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
      className={`repro-womens-chatbox z-50 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col animate-in slide-in-from-bottom-2 duration-300 ${
        isFloating ? "fixed bottom-4 right-32" : "absolute"
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
            }
      }
    >
      {/* Chat Header - with pink/women's health theme */}
      <div
        className="text-white p-5 rounded-t-lg flex justify-between items-center"
        style={{ backgroundColor: "#E78EEB" }}
      >
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold text-lg">Repro Women's Once Daily</h3>
        </div>
        <button onClick={onClose} className="text-white hover:text-gray-200 text-xl">
          ×
        </button>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 p-5 overflow-y-auto bg-gradient-to-b from-pink-50 to-white">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] p-4 rounded-lg shadow-sm ${
                  message.isUser
                    ? "text-white rounded-br-none"
                    : "bg-white text-gray-700 rounded-bl-none border border-pink-100"
                } ${message.status === 'error' ? 'bg-red-100 text-red-700' : ''}`}
                style={message.isUser ? { backgroundColor: "#E78EEB" } : {}}
              >
                {message.status === 'loading' ? (
                  <p className="text-sm flex items-center space-x-1">
                    <span className="animate-bounce text-pink-500">💗</span>
                    <span className="animate-bounce text-pink-400" style={{ animationDelay: "0.2s" }}>💗</span>
                    <span className="animate-bounce text-pink-500" style={{ animationDelay: "0.4s" }}>💗</span>
                  </p>
                ) : (
                  <div className="text-sm">
                    {message.isUser ? (
                      <p>{message.text}</p>
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

                {/* Citations display for AI messages */}
                {!message.isUser && message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-pink-100">
                    <div className="flex items-center space-x-1 text-xs text-pink-600 mb-2">
                      <BookOpen size={12} />
                      <span>Kaynak bilgileri:</span>
                    </div>
                    <div className="space-y-1">
                      {message.citations.slice(0, 3).map((citation, index) => (
                        <div key={index} className="text-xs p-2 bg-pink-50 rounded border-l-2 border-pink-300">
                          <div className="flex items-center space-x-1 font-medium text-pink-700">
                            <Info size={10} />
                            <span>{citation.source}</span>
                            <span className="text-pink-500">({Math.round(citation.similarity * 100)}% uyumluluk)</span>
                          </div>
                          <p className="text-pink-600 mt-1 line-clamp-2">{citation.content.substring(0, 120)}...</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Context usage indicator */}
                {!message.isUser && message.context_used && (
                  <div className="mt-2 flex items-center space-x-1 text-xs text-pink-500">
                    <Info size={10} />
                    <span>Bu yanıt özel dokümanlarımızdan hazırlandı</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input - with pink theme */}
      <div className="p-5 border-t border-pink-100 bg-white rounded-b-lg">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın..."
            className="flex-1 px-4 py-3 rounded-full text-sm focus:outline-none focus:ring-2 focus:border-transparent custom-placeholder"
            style={{ 
              border: '1px solid #A3A9B5',
              '--tw-ring-color': '#FCCC56'
            } as React.CSSProperties}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="w-12 h-12 rounded-full text-white hover:opacity-90 transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
            style={{ backgroundColor: "#FCCC56" }}
          >
            <Send size={18} />
          </button>
        </div>
        
        {/* Quick suggestion buttons for women's health topics */}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => setInputValue("Folat nedir ve neden önemlidir?")}
            className="px-3 py-1 text-xs rounded-full transition-colors"
            style={{ backgroundColor: "#FFDAEF", color: "white" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#E78EEB"
              e.currentTarget.style.color = "white"
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FFDAEF"
              e.currentTarget.style.color = "white"
            }}
            disabled={isLoading}
          >
            💊 Folat
          </button>
          <button
            onClick={() => setInputValue("Vitamin D kadın sağlığı için neden gerekli?")}
            className="px-3 py-1 text-xs rounded-full transition-colors"
            style={{ backgroundColor: "#FFDAEF", color: "white" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#E78EEB"
              e.currentTarget.style.color = "white"
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FFDAEF"
              e.currentTarget.style.color = "white"
            }}
            disabled={isLoading}
          >
            ☀️ Vitamin D
          </button>
          <button
            onClick={() => setInputValue("Hamilelik öncesi hangi vitaminleri almalıyım?")}
            className="px-3 py-1 text-xs rounded-full transition-colors"
            style={{ backgroundColor: "#FFDAEF", color: "white" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#E78EEB"
              e.currentTarget.style.color = "white"
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FFDAEF"
              e.currentTarget.style.color = "white"
            }}
            disabled={isLoading}
          >
            🤱 Hamilelik
          </button>
        </div>
      </div>
    </div>
  )
}