"use client"

import { AuthProvider } from "@/contexts/AuthContext"
import { Toaster } from "@/components/ui/toaster"
import { ReactNode, useEffect } from "react"
import { api } from "@/lib/api"

interface ClientWrapperProps {
  children: ReactNode
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  useEffect(() => {
    // Uygulama ilk açıldığında CSRF token al
    api.auth.getCSRFToken();
  }, []);
  return (
    <AuthProvider>
      <div className="antialiased">
        {children}
        <Toaster />
      </div>
    </AuthProvider>
  )
} 