"use client"

import { useState } from "react"
import ThirdRobot from "./third-robot/ThirdRobot"

export default function FloatingThirdRobot() {
  const [activeChatRobot, setActiveChatRobot] = useState<string | null>(null)

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    setActiveChatRobot(isOpen ? robotId : null)
  }

  return (
    <div className="fixed bottom-8 right-8 z-50 scale-75 origin-bottom-right">
      <ThirdRobot
        onChatToggle={handleChatToggle}
        isOtherChatOpen={false}
        isFloating={true}
      />
    </div>
  )
} 