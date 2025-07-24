"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import { Send } from "lucide-react"
import ReactMarkdown from 'react-markdown'

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
  status?: 'loading' | 'ok' | 'error'
}

interface ThirdRobotChatBoxProps {
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

export default function ThirdRobotChatBox({
  messages,
  inputValue,
  setInputValue,
  sendMessage,
  handleKeyPress,
  onClose,
  position,
  isFloating = false,
  isLoading = false,
}: ThirdRobotChatBoxProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Fixed dimensions - no responsive behavior
  const dimensions = { width: 384, height: 480 }

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
      className={`markamind-chatbox z-50 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col animate-in slide-in-from-bottom-2 duration-300 ${
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
      <div
        className="text-white p-5 rounded-t-lg flex justify-between items-center"
        style={{ backgroundColor: "#FFC429" }}
      >
        <h3 className="font-semibold text-lg">SidrexGPT</h3>
        <button onClick={onClose} className="text-white hover:text-gray-200 text-xl">
          ×
        </button>
      </div>
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
                style={message.isUser ? { backgroundColor: "#FFC429" } : {}}
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
                      <ReactMarkdown
                        components={{
                          strong: ({ node, ...props }) => <span className="font-bold" {...props} />,
                          p: ({ node, ...props }) => <p className="mb-2" {...props} />,
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
          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="p-5 border-t border-gray-200 bg-white rounded-b-lg">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="w-12 h-12 rounded-full text-white hover:opacity-90 transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: "#FFC429" }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
