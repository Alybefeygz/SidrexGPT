"use client"

import SecondRobot from "@/components/robots/second-robot/SecondRobot"

export default function EmbedSecondRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] pointer-events-auto">
      <SecondRobot
        onChatToggle={handleChatToggle}
        isOtherChatOpen={false}
        isFloating={true}
      />
    </div>
  )
}