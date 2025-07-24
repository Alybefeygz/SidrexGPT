"use client"

import FirstRobot from "@/components/robots/first-robot/FirstRobot"
import { useWidgetCommunication } from "@/hooks/use-widget-communication"

export default function EmbedFirstRobot() {
  // Widget iletişim hook'u - mevcut fonksiyonları bozmadan ekler
  const { notifyParent } = useWidgetCommunication({
    onOpen: () => console.log('Widget opened'),
    onClose: () => console.log('Widget closed'),
    enableParentCommunication: true
  })

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
    // Yeni özellik: Parent'a durum bildir
    if (isOpen) {
      notifyParent('ready')
    }
  }

  return (
    <>
      {/* Desktop: Sağ alt köşede */}
      <div className="hidden sm:block fixed bottom-4 right-4 z-[9999] pointer-events-auto">
        <FirstRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>
      
      {/* Mobile: Sağ alt köşede ama daha küçük */}
      <div className="sm:hidden fixed bottom-2 right-2 z-[9999] pointer-events-auto transform scale-75">
        <FirstRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>

      {/* Mobile Responsive Styles + Transparency Fix */}
      <style jsx global>{`
        /* Immediate transparent background - no flash */
        html, body {
          background-color: transparent !important;
          background: transparent !important;
        }
        
        /* Override any potential Tailwind background classes */
        body {
          background-color: transparent !important;
        }
        
        /* Ensure robot components maintain their styling */
        .robot-mascot-container {
          background: transparent !important;
        }
        
        /* Preserve first robot head color */
        .robot-head {
          background-color: #c0c0c0 !important;
        }
        
        /* Chatbox positioning - Desktop */
        .markamind-chatbox {
          position: fixed !important;
          bottom: 20px !important;
          right: 136px !important;
          left: unset !important;
          width: 400px !important;
          height: 500px !important;
        }
        
        /* Mobil ölçülerde chatbox robot üstünde açılsın */
        @media (max-width: 769px) {
          .markamind-chatbox {
            position: fixed !important;
            bottom: 180px !important; /* Robot üstünde + 80px yukarı */
            right: 16px !important; /* Ekranın sağına yapışık */
            left: unset !important; /* Sol margin kaldır */
            width: 350px !important; /* Sabit genişlik */
            max-width: calc(100vw - 32px) !important; /* Ekranı taşmaması için */
            height: 400px !important;
            margin: 0 !important; /* Margin kaldır */
          }
        }
        
        @media (max-width: 640px) {
          /* Robot boyutunu küçült */
          .fixed.bottom-2.right-2 button {
            width: 60px !important;
            height: 60px !important;
          }
          
          /* Chatbox mobilde robot üstüne taşın */
          .fixed.bottom-2.right-2 [class*="absolute"] {
            position: fixed !important;
            bottom: 80px !important;
            right: 10px !important;
            left: 10px !important;
            width: calc(100vw - 20px) !important;
            max-width: 350px !important;
            height: 400px !important;
          }
          
          /* Chatbox padding'ini küçült */
          .fixed.bottom-2.right-2 [class*="p-5"] {
            padding: 12px !important;
          }
          
          /* Input area'yı küçült */
          .fixed.bottom-2.right-2 input {
            padding: 8px 12px !important;
            font-size: 14px !important;
          }
          
          /* Send button'u küçült */
          .fixed.bottom-2.right-2 button[class*="w-12"] {
            width: 40px !important;
            height: 40px !important;
          }
        }
      `}</style>
    </>
  )
}