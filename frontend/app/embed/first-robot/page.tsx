"use client"

import FirstRobot from "@/components/robots/first-robot/FirstRobot"
import { useEffect } from "react"

export default function EmbedFirstRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // İframe boyutunu parent window'a bildir
    if (typeof window !== 'undefined' && window.parent) {
      if (isOpen) {
        // Chatbox açık - iframe'i genişlet
        window.parent.postMessage({
          type: 'SIDREX_IFRAME_RESIZE',
          width: window.innerWidth < 640 ? '100%' : '400px',
          height: window.innerWidth < 640 ? '500px' : '600px'
        }, '*')
      } else {
        // Chatbox kapalı - iframe'i küçült
        window.parent.postMessage({
          type: 'SIDREX_IFRAME_RESIZE', 
          width: window.innerWidth < 640 ? '80px' : '100px',
          height: window.innerWidth < 640 ? '80px' : '100px'
        }, '*')
      }
    }
  }
  
  // Sayfa yüklenince varsayılan boyutu ayarla
  useEffect(() => {
    if (typeof window !== 'undefined' && window.parent) {
      window.parent.postMessage({
        type: 'SIDREX_IFRAME_RESIZE',
        width: window.innerWidth < 640 ? '80px' : '100px', 
        height: window.innerWidth < 640 ? '80px' : '100px'
      }, '*')
    }
  }, [])

  return (
    <>
      {/* Desktop: Sağ alt köşede */}
      <div className="hidden sm:block fixed bottom-0 right-0 z-[9999] pointer-events-auto">
        <FirstRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>
      
      {/* Mobile: Sağ alt köşede */}
      <div className="sm:hidden fixed bottom-0 right-0 z-[9999] pointer-events-auto">
        <FirstRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>

      {/* Dinamik İframe Boyutu İçin Styles */}
      <style jsx global>{`
        body {
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
        
        @media (max-width: 640px) {
          /* Mobil robot boyutu */
          .sm\:hidden button {
            width: 60px !important;
            height: 60px !important;
          }
          
          /* Mobil chatbox tam ekran */
          .sm\:hidden [class*="z-50"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 70px !important;
            width: 100% !important;
            height: calc(100% - 70px) !important;
            max-width: none !important;
          }
          
          /* Mobil input küçült */
          .sm\:hidden input {
            padding: 10px !important;
            font-size: 14px !important;
          }
        }
        
        @media (min-width: 641px) {
          /* Desktop chatbox pozisyonu */
          .hidden.sm\:block [class*="z-50"] {
            position: fixed !important;
            bottom: 110px !important;
            right: 10px !important;
            width: 380px !important;
            height: 500px !important;
          }
        }
      `}</style>
    </>
  )
}