"use client"

import React from "react"
import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"

export default function ThirdRobotFrame() {
  return (
    <div className="w-screen h-screen relative bg-transparent">
      <div className="fixed bottom-4 right-4">
        <ThirdRobot
          onChatToggle={() => {}} // İframe içinde diğer robotlarla etkileşim yok
          isOtherChatOpen={false}  // Her zaman false çünkü tek robot var
          isFloating={true}        // İframe içinde floating pozisyon kullan
        />
      </div>
    </div>
  )
} 