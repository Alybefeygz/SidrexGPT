"use client"

import { useState } from "react"
import FirstRobot from "./first-robot/FirstRobot"

export default function FloatingRobot() {
  const [activeChatRobot, setActiveChatRobot] = useState<string | null>(null)

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    setActiveChatRobot(isOpen ? robotId : null)
  }

  return (
    <div className="fixed bottom-8 right-8 z-50 scale-75 origin-bottom-right">
      <FirstRobot
        onChatToggle={handleChatToggle}
        isOtherChatOpen={false}
        isFloating={true}
      />
    </div>
  )
} 