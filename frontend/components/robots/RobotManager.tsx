"use client"

import { useState } from "react"
import FirstRobot from "./first-robot/FirstRobot"
import SecondRobot from "./second-robot/SecondRobot"
import ThirdRobot from "./third-robot/ThirdRobot"
import Link from "next/link"

export default function RobotManager() {
  const [activeChatRobot, setActiveChatRobot] = useState<string | null>(null)

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    setActiveChatRobot(isOpen ? robotId : null)
  }

  return (
    <>
      {/* First Row - Original position robots */}
      <div className="flex items-end justify-center min-h-[80vh] py-12 pb-24">
        <div className="flex flex-row items-center space-x-[32rem] ml-48">
          <div className="flex flex-col items-center">
            <FirstRobot
              onChatToggle={handleChatToggle}
              isOtherChatOpen={activeChatRobot !== null && activeChatRobot !== "first"}
            />
            <Link 
              href="/sidrexgpt/ana-robot" 
              className="mt-8 text-cyan-500 hover:text-cyan-600 font-medium transition-colors z-10 relative bg-white py-2 px-4 rounded-md shadow-sm"
            >
              Detayını gör
            </Link>
          </div>
          <div className="flex flex-col items-center">
            <SecondRobot
              onChatToggle={handleChatToggle}
              isOtherChatOpen={activeChatRobot !== null && activeChatRobot !== "second"}
            />
            <Link 
              href="/sidrexgpt/mag4ever" 
              className="mt-8 text-indigo-600 hover:text-indigo-700 font-medium transition-colors z-10 relative bg-white py-2 px-4 rounded-md shadow-sm"
            >
              Detayını gör
            </Link>
          </div>
        </div>
      </div>

      {/* Second Row - New robots with more spacing */}
      <div className="flex items-center justify-center py-24 mt-48 -ml-96">
        <div className="flex flex-row items-center" style={{ marginLeft: "-40px" }}>
          <div className="flex flex-col items-center">
            <ThirdRobot
              onChatToggle={handleChatToggle}
              isOtherChatOpen={activeChatRobot !== null && activeChatRobot !== "third"}
            />
            <Link 
              href="/sidrexgpt/imuntus-kids" 
              className="mt-8 text-yellow-500 hover:text-yellow-600 font-medium transition-colors z-10 relative bg-white py-2 px-4 rounded-md shadow-sm"
            >
              Detayını gör
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}
