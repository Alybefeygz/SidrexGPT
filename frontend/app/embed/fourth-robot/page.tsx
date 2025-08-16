"use client"

import FourthRobot from "@/components/robots/fourth-robot/FourthRobot"
import { useWidgetCommunication } from "@/hooks/use-widget-communication"

export default function EmbedFourthRobot() {
  // Widget iletişim hook'u - mevcut fonksiyonları bozmadan ekler
  const { notifyParent, notifyRobotClicked, notifyOpenChatbox, notifyCloseChatbox } = useWidgetCommunication({
    onOpen: () => console.log('Fourth Robot Widget opened'),
    onClose: () => console.log('Fourth Robot Widget closed'),
    enableParentCommunication: true
  })

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
    // Yeni özellik: Parent'a durum bildir
    if (isOpen) {
      notifyParent('ready')
      notifyOpenChatbox() // Chatbox açıldı
    } else {
      notifyCloseChatbox() // Chatbox kapandı
    }
  }

  // Robot tıklama handler'ı
  const handleRobotClick = () => {
    notifyRobotClicked() // Robot'a tıklandı, iframe büyütülecek
  }

  return (
    <>
      {/* Robot Sağ Alt Köşede - Tek Pozisyon */}
      <div className="fixed bottom-4 right-4 z-[9999] pointer-events-auto" onClick={handleRobotClick}>
        <FourthRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>

      {/* Chatbox Positioning Styles + Transparency Fix */}
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
        
        .markamind-chatbox {
          position: fixed !important;
          bottom: 20px !important; /* Robot ile aynı hizada */
          right: 136px !important; /* Robot'un solunda (robot 96px + margin 16px + gap 24px) */
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
            height: 400px !important; /* Mobilde daha küçük yükseklik */
            margin: 0 !important; /* Margin kaldır */
          }
        }
        
        /* Ensure robot components maintain their styling */
        .robot-mascot-container {
          background: transparent !important;
        }
        
        /* Preserve robot head colors while keeping background transparent */
        .robot-head-fourth {
          background-color: #EAF6FE !important;
          border: 2px solid #1A5BBC !important;
        }
      `}</style>
    </>
  )
}