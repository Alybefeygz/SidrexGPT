"use client"

import SecondRobot from "@/components/robots/second-robot/SecondRobot"
import { AuthProvider } from "@/contexts/AuthContext"

export default function SecondRobotPage() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Handle chat toggle for iframe context
  }

  return (
    <AuthProvider>
      <div className="w-full h-screen flex items-center justify-center relative">
        <div className="relative top-[200px]">
          <SecondRobot 
            isFloating={false}
            onChatToggle={handleChatToggle}
            isOtherChatOpen={false}
          />
        </div>
      </div>
    </AuthProvider>
  )
}
