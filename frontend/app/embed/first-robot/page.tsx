"use client"

import FirstRobot from "@/components/robots/first-robot/FirstRobot"

export default function EmbedFirstRobot() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Embed modunda diğer robotlar yok, bu yüzden boş
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] pointer-events-auto">
      <FirstRobot
        onChatToggle={handleChatToggle}
        isOtherChatOpen={false}
        isFloating={true}
      />
    </div>
  )
}