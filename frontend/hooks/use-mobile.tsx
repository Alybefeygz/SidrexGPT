import { useState, useEffect } from 'react'

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkDevice = () => {
      setIsMobile(window.innerWidth < 1000)
    }
    
    checkDevice()
    window.addEventListener('resize', checkDevice)
    
    return () => window.removeEventListener('resize', checkDevice)
  }, [])

  return isMobile
}