"use client"

import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"
import { AuthProvider } from "@/contexts/AuthContext"

export default function ThirdRobotPage() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Handle chat toggle for iframe context
  }

  return (
    <AuthProvider>
      <div className="w-full h-screen flex items-center justify-center relative">
        <div className="relative top-[200px]">
          <ThirdRobot 
            isFloating={false}
            onChatToggle={handleChatToggle}
            isOtherChatOpen={false}
          />
        </div>
      </div>
    </AuthProvider>
  )
}
