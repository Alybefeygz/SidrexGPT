"use client"

import { AuthProvider } from "@/contexts/AuthContext"
import { Toaster } from "@/components/ui/toaster"
import { ReactNode } from "react"

interface ClientWrapperProps {
  children: ReactNode
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  return (
    <AuthProvider>
      <div className="antialiased">
        {children}
        <Toaster />
      </div>
    </AuthProvider>
  )
} 