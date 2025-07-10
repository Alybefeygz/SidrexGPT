"use client"

import type React from "react"
import FloatingRobot from "../components/robots/FloatingRobot"
import FloatingSecondRobot from "../components/robots/FloatingSecondRobot"
import FloatingThirdRobot from "../components/robots/FloatingThirdRobot"
import { Toaster } from "@/components/ui/toaster"
import { usePathname } from "next/navigation"
import { AssetProvider } from "../contexts/AssetContext"

export default function ClientLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const pathname = usePathname()
  const isHomePage = pathname === '/' || pathname === '/index' || pathname === '/home'
  const isMag4EverPage = pathname?.includes('/product/mag4ever')
  const isImuntusKidsPage = pathname?.includes('/product/imuntus-kids')

  const shouldShowRobot = isHomePage || isMag4EverPage || isImuntusKidsPage

  const getRobotComponent = () => {
    if (isImuntusKidsPage) {
      return <FloatingThirdRobot />
    } else if (isMag4EverPage) {
      return <FloatingSecondRobot />
    } else if (isHomePage) {
      return <FloatingRobot />
    }
    return null
  }

  return (
    <AssetProvider>
      {children}
      {shouldShowRobot && getRobotComponent()}
      <Toaster />
    </AssetProvider>
  )
}
