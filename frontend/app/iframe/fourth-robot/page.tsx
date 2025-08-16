"use client"

import FourthRobot from "@/components/robots/fourth-robot/FourthRobot"
import { AuthProvider } from "@/contexts/AuthContext"

export default function FourthRobotPage() {
  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Handle chat toggle for iframe context
  }

  return (
    <AuthProvider>
      <div className="w-full h-screen flex items-center justify-center relative">
        <div className="relative top-[200px]">
          <FourthRobot 
            isFloating={false}
            onChatToggle={handleChatToggle}
            isOtherChatOpen={false}
          />
        </div>
      </div>
    </AuthProvider>
  )
}