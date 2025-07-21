"use client"

import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"

export default function EmbedThirdRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
  }

  return (
    <>
      {/* Desktop: Sağ alt köşede */}
      <div className="hidden sm:block fixed bottom-4 right-4 z-[9999] pointer-events-auto">
        <ThirdRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>
      
      {/* Mobile: Sağ alt köşede ama daha küçük */}
      <div className="sm:hidden fixed bottom-2 right-2 z-[9999] pointer-events-auto transform scale-75">
        <ThirdRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>

      {/* Mobile Responsive Styles */}
      <style jsx global>{`
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