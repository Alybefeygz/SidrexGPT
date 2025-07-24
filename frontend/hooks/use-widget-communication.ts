/**
 * Widget Communication Hook
 * PostMessage sistemi için hook - mevcut sistemi bozmadan ekler
 */
"use client"

import { useEffect } from 'react'

interface WidgetCommunicationOptions {
  onOpen?: () => void
  onClose?: () => void
  enableParentCommunication?: boolean
}

export function useWidgetCommunication(options: WidgetCommunicationOptions = {}) {
  const { onOpen, onClose, enableParentCommunication = true } = options

  useEffect(() => {
    if (!enableParentCommunication) return

    // Parent window'a mesaj gönderme fonksiyonu
    const sendToParent = (message: string) => {
      if (window.parent && window.parent !== window) {
        try {
          window.parent.postMessage(message, '*')
        } catch (error) {
          console.warn('Widget communication error:', error)
        }
      }
    }

    // Parent'dan gelen mesajları dinle
    const handleMessage = (event: MessageEvent) => {
      try {
        const { data } = event
        
        if (data === 'openWidget') {
          onOpen?.()
        } else if (data === 'closeWidget') {
          onClose?.()
        }
      } catch (error) {
        console.warn('Widget message handling error:', error)
      }
    }

    window.addEventListener('message', handleMessage)

    return () => {
      window.removeEventListener('message', handleMessage)
    }
  }, [onOpen, onClose, enableParentCommunication])

  // Robot tıklama bildirimi
  const notifyRobotClicked = () => {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage('robotClicked', '*')
    }
  }

  // Chatbox açılma bildirimi - Orbina style
  const notifyOpenChatbox = () => {
    if (window.parent && window.parent !== window) {
      console.log("🚀 Sending openChatbox to parent")
      window.parent.postMessage('openChatbox', '*')
    }
    onOpen?.()
  }

  // Chatbox kapanma bildirimi - Orbina style
  const notifyCloseChatbox = () => {
    if (window.parent && window.parent !== window) {
      console.log("🚀 Sending closeChatbox to parent")
      window.parent.postMessage('closeChatbox', '*')
    }
    onClose?.()
  }

  // Widget tamamen kapanma bildirimi
  const notifyWidgetClosed = () => {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage('widgetClosed', '*')
    }
  }

  // Widget durumunu parent'a bildir
  const notifyParent = (status: 'ready' | 'loading' | 'error') => {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(`widget-${status}`, '*')
    }
  }

  // Legacy fonksiyonlar (geriye uyumluluk için)
  const openWidget = notifyOpenChatbox
  const closeWidget = notifyCloseChatbox

  return {
    openWidget,
    closeWidget,
    notifyParent,
    notifyRobotClicked,
    notifyOpenChatbox,
    notifyCloseChatbox,
    notifyWidgetClosed
  }
}