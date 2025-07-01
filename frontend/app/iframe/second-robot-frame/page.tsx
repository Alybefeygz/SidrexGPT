"use client"

import React from "react"
import SecondRobot from "@/components/robots/second-robot/SecondRobot"

export default function SecondRobotFrame() {
  return (
    <div className="w-screen h-screen relative bg-transparent">
      <div className="fixed bottom-4 right-4">
        <SecondRobot
          onChatToggle={() => {}} // İframe içinde diğer robotlarla etkileşim yok
          isOtherChatOpen={false}  // Her zaman false çünkü tek robot var
          isFloating={true}        // İframe içinde floating pozisyon kullan
        />
      </div>
    </div>
  )
} 