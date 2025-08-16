"use client"
import { useState, useRef, useEffect } from "react"

interface FourthRobotProps {
  onChatToggle: (robotId: string, isOpen: boolean) => void
  isOtherChatOpen: boolean
  messages?: string[]
  isFloating?: boolean
}

// Message type with ID and closing state
interface MessageItem {
  id: number
  text: string
  isClosing: boolean
}

export default function FourthRobot({ onChatToggle, isOtherChatOpen, messages: propMessages, isFloating = false }: FourthRobotProps) {
  // Default messages if no props provided
  const defaultMessages = [
    "Zzen sayesinde mutlu bir uykuyu yaşıyorum.",
    "Zzen var, uykular artık daha derin, daha dingin.",
    "Şuanda uyuyorum!!!",
    "Zzen sayesinde huzurlu bir uyku artık benimle."
  ]
  
  // Messages state that updates when props change
  const [messages, setMessages] = useState<string[]>(
    propMessages && propMessages.length > 0 ? propMessages : defaultMessages
  )
  
  // Update messages when props change
  useEffect(() => {
    const newMessages = propMessages && propMessages.length > 0 ? propMessages : defaultMessages
    setMessages(newMessages)
    console.log('FourthRobot mesajları güncellendi:', newMessages)
  }, [propMessages])

  // Animation state
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)
  const [hasBeenClicked, setHasBeenClicked] = useState(false) // Permanent click state
  const [activeMessages, setActiveMessages] = useState<MessageItem[]>([]) // Array of active messages
  const [lastMessageIndex, setLastMessageIndex] = useState(0) // Track last message to avoid repetition
  const [animationKey, setAnimationKey] = useState(0) // Key to restart animations
  const [messageIdCounter, setMessageIdCounter] = useState(0) // Counter for unique message IDs

  const handleMouseEnter = () => {
    setIsHovered(true)
  }

  const handleMouseLeave = () => {
    if (!hasBeenClicked) {
      // Only reset hover if never clicked
      setIsHovered(false)
      // Restart animations to maintain synchronization
      setAnimationKey((prev) => prev + 1)
    }
  }

  // Function to get a random message different from the last one
  const getRandomMessage = () => {
    let availableMessages = messages.filter((_, index) => index !== lastMessageIndex)
    
    // If only one message left (shouldn't happen with 4 messages), allow all
    if (availableMessages.length === 0) {
      availableMessages = messages
    }
    
    const randomIndex = Math.floor(Math.random() * availableMessages.length)
    const selectedMessage = availableMessages[randomIndex]
    
    // Find the original index of the selected message
    const originalIndex = messages.findIndex(msg => msg === selectedMessage)
    setLastMessageIndex(originalIndex)
    
    return selectedMessage
  }

  // Function to remove a message by ID
  const removeMessage = (messageId: number) => {
    setActiveMessages(prev => prev.filter(msg => msg.id !== messageId))
  }

  // Function to start closing animation for a message
  const startMessageClosing = (messageId: number) => {
    setActiveMessages(prev => 
      prev.map(msg => 
        msg.id === messageId ? { ...msg, isClosing: true } : msg
      )
    )
    
    // Remove after animation completes
    setTimeout(() => {
      removeMessage(messageId)
    }, 300) // 300ms animation duration
  }

  const handleClick = () => {
    setHasBeenClicked(true) // Permanent state - robot stays in hover mode
    setIsHovered(true) // Keep hover state active
    
    // Get new random message
    const newMessage = getRandomMessage()
    const newMessageId = messageIdCounter
    setMessageIdCounter(prev => prev + 1)
    
    // Add new message to active messages array
    const newMessageItem: MessageItem = {
      id: newMessageId,
      text: newMessage,
      isClosing: false
    }
    
    setActiveMessages(prev => {
      const updatedMessages = [...prev, newMessageItem]
      
      // If we exceed 5 messages, remove the oldest one immediately
      if (updatedMessages.length > 5) {
        const oldestMessage = updatedMessages[0]
        // Start closing animation for the oldest message
        startMessageClosing(oldestMessage.id)
        // Return only the last 5 messages
        return updatedMessages.slice(1)
      }
      
      return updatedMessages
    })
    
    // Set timer for this specific message
    setTimeout(() => {
      startMessageClosing(newMessageId)
    }, 5000) // 5 seconds for each message
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        className={`w-28 h-28 rounded-full shadow-2xl hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer flex items-center justify-center relative overflow-visible ${
          isHovered || hasBeenClicked ? "fourth-robot-active" : ""
        }`}
        style={{
          backgroundColor: "#EAF6FE",
          border: "2px solid #1A5BBC",
        }}
        key={animationKey} // This will restart CSS animations
      >
        {/* Z harfleri for fourth robot only - positioned in top-right corner */}
        <div className="absolute -top-2 -right-2 pointer-events-none fourth-robot-z">
          {/* Ana Z - en küçük */}
          <div
            className="absolute w-4 h-4 flex items-center justify-center text-yellow-400 font-bold text-sm"
            style={{ top: "0px", right: "0px" }}
          >
            Z
          </div>
          {/* Üst Z - normal boyut */}
          <div
            className="absolute w-6 h-6 flex items-center justify-center text-yellow-400 font-bold text-lg"
            style={{ top: "-20px", right: "-12px" }}
          >
            Z
          </div>
          {/* Orta Z - biraz küçük */}
          <div
            className="absolute w-5 h-5 flex items-center justify-center text-yellow-400 font-bold text-base"
            style={{ top: "-16px", right: "12px" }}
          >
            Z
          </div>
        </div>
        {/* Coffee Cup for fourth robot only - positioned in bottom-right corner, visible in normal state */}
        <div className="absolute pointer-events-none fourth-robot-coffee" style={{ bottom: "-16px", right: "-25px" }}>
          <div
            className="w-16 h-16 bg-contain bg-no-repeat bg-center"
            style={{
              backgroundImage: "url('/images/coffee-cup.png')",
            }}
          />
        </div>
        {/* Alarm Clock for fourth robot only - positioned in bottom-left corner, visible in normal state - moved 3px down */}
        <div className="absolute pointer-events-none fourth-robot-clock" style={{ bottom: "-19px", left: "-25px" }}>
          <div
            className="w-16 h-16 bg-contain bg-no-repeat bg-center"
            style={{
              backgroundImage: "url('/images/alarm-clock.png')",
            }}
          />
        </div>
        {/* Robot Mascot */}
        <div className="robot-mascot-container">
          <div className="robot-head-fourth">
            {/* Robot Antenna - Blue antenna for fourth robot */}
            <div className="robot-antenna-blue"></div>

            {/* Robot Ears */}
            <div className="robot-ear-fourth robot-ear-left"></div>
            <div className="robot-ear-fourth robot-ear-right"></div>
            <div className="robot-face-fourth">
              {/* Fourth robot normal eyes - visible in normal state, similar to third robot hover eyes */}
              <div className="robot-fourth-normal-eyes left"></div>
              <div className="robot-fourth-normal-eyes right"></div>
              {/* Fourth robot sleepy eyes - visible on hover */}
              <div className="robot-fourth-sleepy-eyes"></div>
              {/* Fourth robot hover eyes - circular eyes that appear on hover */}
              <div className="robot-fourth-hover-eyes left"></div>
              <div className="robot-fourth-hover-eyes right"></div>
              {/* Fourth robot yawning mouth - visible in normal state */}
              <div className="robot-fourth-yawning-mouth"></div>
              {/* Fourth robot sleepy mouth - visible on hover */}
              <div className="robot-fourth-sleepy-mouth"></div>
              {/* Fourth robot normal mouth - appears on hover */}
              <div className="robot-fourth-hover-mouth"></div>
            </div>
          </div>
        </div>
        {/* Robot Pillow - appears on hover */}
        <div className="robot-pillow"></div>
      </button>

      {/* Multiple messages stack - positioned to the left of the robot */}
      {activeMessages.length > 0 && (
        <div className="absolute z-50" style={{ right: "140px", top: "calc(50% + 25px)", bottom: "calc(50% - 25px)" }}>
          <div 
            className="flex flex-col-reverse gap-2 items-end" 
            style={{ 
              position: "absolute",
              bottom: 0,
              right: 0
            }}
          >
            {activeMessages.map((message, index) => (
              <div
                key={message.id}
                className={`rounded-lg shadow-xl p-4 transition-all duration-300 inline-block ${
                  message.isClosing 
                    ? "animate-out slide-out-to-right-2 fade-out" 
                    : "animate-in slide-in-from-right-2 duration-300"
                }`}
                style={{
                  backgroundColor: "#D5F1FF",
                  border: "2px solid #3594E7",
                  // Add slight offset for stacking visual effect
                  marginRight: `${index * 4}px`,
                  zIndex: 50 - index,
                  width: "fit-content",
                }}
              >
                <div className="flex items-center gap-2 text-sm font-medium whitespace-nowrap" style={{ color: "#3592E5" }}>
                  <img src="/images/moon.png" alt="moon" className="w-6 h-6" />
                  <span className="pr-4">{message.text}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
