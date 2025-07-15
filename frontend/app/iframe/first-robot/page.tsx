"use client"

import FirstRobot from "@/components/robots/first-robot/FirstRobot"
import { AuthProvider } from "@/contexts/AuthContext"

export default function FirstRobotPage() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Handle chat toggle for iframe context
  }

  return (
    <AuthProvider>
      <div className="w-full h-screen flex items-center justify-center relative">
        <div className="relative top-[200px]">
          <FirstRobot 
            isFloating={false}
            onChatToggle={handleChatToggle}
            isOtherChatOpen={false}
          />
        </div>
      </div>
    </AuthProvider>
  )
}
