"use client"

import SecondRobot from "@/components/robots/second-robot/SecondRobot"
import { useEffect } from "react"

export default function EmbedSecondRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // İframe boyutunu parent window'a bildir
    if (typeof window !== 'undefined' && window.parent) {
      const isMobile = window.innerWidth <= 640
      
      if (isOpen) {
        // Chatbox açık - iframe'i genişlet
        window.parent.postMessage({
          type: 'SIDREX_RESIZE',
          action: 'expand',
          width: isMobile ? '350px' : '400px',
          height: isMobile ? '500px' : '600px'
        }, '*')
      } else {
        // Chatbox kapalı - iframe'i küçült
        window.parent.postMessage({
          type: 'SIDREX_RESIZE',
          action: 'collapse',
          width: isMobile ? '80px' : '120px',
          height: isMobile ? '80px' : '120px'
        }, '*')
      }
    }
  }
  
  // Sayfa yüklenince varsayılan boyutu ayarla
  useEffect(() => {
    if (typeof window !== 'undefined' && window.parent) {
      const isMobile = window.innerWidth <= 640
      window.parent.postMessage({
        type: 'SIDREX_RESIZE',
        action: 'init',
        width: isMobile ? '80px' : '120px',
        height: isMobile ? '80px' : '120px'
      }, '*')
    }
  }, [])

  return (
    <>
      {/* Desktop: Köşede konumlandır */}
      <div className="hidden sm:block fixed bottom-2 right-2 z-[9999] pointer-events-auto">
        <SecondRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>
      
      {/* Mobile: Köşede konumlandır */}
      <div className="sm:hidden fixed bottom-1 right-1 z-[9999] pointer-events-auto">
        <SecondRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>

      {/* Dinamik İframe için Optimize Edilmiş Styles */}
      <style jsx global>{`
        body {
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
        
        /* Desktop Styles */
        @media (min-width: 641px) {
          .hidden.sm\:block [class*="z-50"] {
            position: fixed !important;
            bottom: 125px !important;
            right: 5px !important;
            width: 390px !important;
            height: 495px !important;
          }
        }
        
        /* Mobile Styles */
        @media (max-width: 640px) {
          .sm\:hidden button {
            width: 60px !important;
            height: 60px !important;
          }
          
          .sm\:hidden [class*="z-50"] {
            position: fixed !important;
            bottom: 65px !important;
            right: 5px !important;
            left: 5px !important;
            width: calc(100% - 10px) !important;
            height: 430px !important;
          }
          
          .sm\:hidden [class*="p-5"] {
            padding: 10px !important;
          }
          
          .sm\:hidden input {
            padding: 8px 10px !important;
            font-size: 14px !important;
          }
        }
      `}</style>
    </>
  )
}