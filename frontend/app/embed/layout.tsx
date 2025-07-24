"use client"

import "../globals.css"
import { useEffect } from "react"

export default function EmbedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Client-side CSS injection for transparency
  useEffect(() => {
    // Create and inject global styles for embed transparency
    const style = document.createElement('style')
    style.textContent = `
      html, body {
        background-color: transparent !important;
        background: transparent !important;
        margin: 0;
        padding: 0;
      }
      
      /* Override Tailwind's bg-background */
      body {
        background-color: transparent !important;
      }
      
      /* Ensure robot remains properly styled while keeping transparency */
      .robot-mascot-container {
        background: transparent !important;
      }
      
      /* Ensure robot head backgrounds are preserved */
      .robot-head,
      .robot-head-second,
      .robot-head-third {
        background-color: inherit;
      }
    `
    document.head.appendChild(style)
    
    // Cleanup function
    return () => {
      document.head.removeChild(style)
    }
  }, [])
  
  return (
    <div className="bg-transparent pointer-events-none" style={{ margin: 0, padding: 0, background: 'transparent', width: '100%', height: '100%' }}>
      {children}
    </div>
  )
}