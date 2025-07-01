"use client"

import React from "react"
import FirstRobot from "@/components/robots/first-robot/FirstRobot"

export default function FirstRobotFrame() {
  return (
    <div className="w-screen h-screen relative bg-transparent">
      <div className="fixed bottom-4 right-4">
        <FirstRobot
          onChatToggle={() => {}} // İframe içinde diğer robotlarla etkileşim yok
          isOtherChatOpen={false}  // Her zaman false çünkü tek robot var
          isFloating={true}        // İframe içinde floating pozisyon kullan
        />
      </div>
    </div>
  )
} 