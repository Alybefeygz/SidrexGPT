"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import { Send, BookOpen, Info } from "lucide-react"
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

interface FirstRobotChatBoxProps {
  messages: Message[]
  inputValue: string
  setInputValue: (value: string) => void
  sendMessage: () => void
  handleKeyPress: (e: React.KeyboardEvent) => void
  onClose: () => void
  position: { top: number; left: number }
  dimensions: { width: number; height: number }
  isFloating?: boolean
  isLoading?: boolean
}

export default function FirstRobotChatBox({
  messages,
  inputValue,
  setInputValue,
  sendMessage,
  handleKeyPress,
  onClose,
  position,
  dimensions,
  isFloating = false,
  isLoading = false,
}: FirstRobotChatBoxProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set())

  // Auto-scroll to bottom when new messages arrive - only scroll within chatbox container
  useEffect(() => {
    if (messagesEndRef.current) {
      const chatContainer = messagesEndRef.current.closest('.overflow-y-auto')
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight
      }
    }
  }, [messages])

  const toggleCitationExpansion = (messageId: number) => {
    setExpandedCitations(prev => {
      const newSet = new Set(prev)
      if (newSet.has(messageId)) {
        newSet.delete(messageId)
      } else {
        newSet.add(messageId)
      }
      return newSet
    })
  }

  const getPdfTypeColor = (pdfType: string) => {
    switch (pdfType) {
      case 'beyan': return 'bg-red-100 text-red-700 border-red-200'
      case 'rol': return 'bg-purple-100 text-purple-700 border-purple-200'
      case 'kural': return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'bilgi': return 'bg-blue-100 text-blue-700 border-blue-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getPdfTypeIcon = (pdfType: string) => {
    switch (pdfType) {
      case 'beyan': return '🚨'
      case 'rol': return '🔴'
      case 'kural': return '🟠'
      case 'bilgi': return '📘'
      default: return '📄'
    }
  }

  return (
    <div
      className={`z-50 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col animate-in slide-in-from-bottom-2 duration-300 ${
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
      {/* Chat Header */}
      <div
        className="text-white p-5 rounded-t-lg flex justify-between items-center"
        style={{ backgroundColor: "#17a2b8" }}
      >
        <h3 className="font-semibold text-lg">SidrexGPT</h3>
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
                style={message.isUser ? { backgroundColor: "#17a2b8" } : {}}
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
                      <p>{message.text}</p>
                    ) : (
                      <>
                        <ReactMarkdown
                          components={{
                            strong: ({ node, ...props }) => <span className="font-bold" {...props} />,
                          }}
                        >
                          {message.text}
                        </ReactMarkdown>
                        
                        {/* Citations Section */}
                        {message.citations && message.citations.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <BookOpen size={14} className="text-gray-500" />
                                <span className="text-xs text-gray-600 font-medium">
                                  Kaynaklar ({message.citations.length})
                                </span>
                                {message.context_used && (
                                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                    RAG Aktif
                                  </span>
                                )}
                              </div>
                              <button
                                onClick={() => toggleCitationExpansion(message.id)}
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                {expandedCitations.has(message.id) ? 'Gizle' : 'Göster'}
                              </button>
                            </div>
                            
                            {expandedCitations.has(message.id) && (
                              <div className="space-y-2">
                                {message.citations.map((citation, index) => (
                                  <div 
                                    key={index} 
                                    className={`p-2 rounded text-xs border ${getPdfTypeColor(citation.pdf_type)}`}
                                  >
                                    <div className="flex items-center justify-between mb-1">
                                      <div className="flex items-center space-x-1">
                                        <span>{getPdfTypeIcon(citation.pdf_type)}</span>
                                        <span className="font-medium truncate max-w-[200px]">
                                          {citation.source}
                                        </span>
                                      </div>
                                      <span className="text-xs opacity-70">
                                        %{Math.round(citation.similarity * 100)}
                                      </span>
                                    </div>
                                    <p className="text-xs opacity-80 line-clamp-2">
                                      {citation.content}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {/* Auto-scroll anchor */}
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
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="w-12 h-12 rounded-full text-white hover:opacity-90 transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: "#17a2b8" }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
