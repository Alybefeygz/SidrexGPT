"use client"

import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"

export default function EmbedThirdRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] pointer-events-auto">
      <ThirdRobot
        onChatToggle={handleChatToggle}
        isOtherChatOpen={false}
        isFloating={true}
      />
    </div>
  )
}