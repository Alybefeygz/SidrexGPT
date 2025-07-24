/**
 * Widget Helper Functions
 * Mobil optimizasyon ve genel widget işlemleri için yardımcı fonksiyonlar
 */

// Mobil cihaz tespiti
export function isMobileDevice(): boolean {
  if (typeof window === 'undefined') return false
  
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
         ('ontouchstart' in window) ||
         (navigator.maxTouchPoints > 0)
}

// Güvenli viewport yüksekliği hesaplama (mobil tarayıcılar için)
export function getSafeViewportHeight(): string {
  if (typeof window !== 'undefined') {
    // Mobil browser'larda dinamik toolbar'lar için window.innerHeight kullan
    return window.innerHeight + 'px'
  }
  return '100vh'
}

// Cihaz orientation tespiti
export function getDeviceOrientation(): 'portrait' | 'landscape' {
  if (typeof window !== 'undefined') {
    return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
  }
  return 'portrait'
}

// Viewport yüksekliğini güncelle (orientation change için)
export function updateViewportHeight(): void {
  if (isMobileDevice() && typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--vh', (window.innerHeight * 0.01) + 'px')
  }
}

// Widget pozisyon hesaplaması
export function calculateWidgetPosition(
  position: 'left' | 'right',
  isMobile: boolean,
  defaultOffsets: { desktop: string; mobile: string }
): { [key: string]: string } {
  const offset = isMobile ? defaultOffsets.mobile : defaultOffsets.desktop
  
  return position === 'left' 
    ? { left: offset, right: 'unset' }
    : { right: offset, left: 'unset' }
}

// CSS media query matcher
export function createMediaQueryMatcher(query: string, callback: (matches: boolean) => void): () => void {
  if (typeof window === 'undefined') return () => {}
  
  const mediaQuery = window.matchMedia(query)
  
  const handler = (e: MediaQueryListEvent) => callback(e.matches)
  
  // İlk kontrol
  callback(mediaQuery.matches)
  
  // Listener ekle
  mediaQuery.addListener(handler)
  
  // Cleanup fonksiyonu döndür
  return () => mediaQuery.removeListener(handler)
}

// Widget boyutu hesaplama
export function calculateWidgetSize(
  isMobile: boolean,
  isExpanded: boolean,
  customSizes?: {
    mobile: { width: string; height: string }
    desktop: { width: string; height: string }
    expanded: { width: string; height: string }
  }
): { width: string; height: string } {
  const defaultSizes = {
    mobile: { width: '50px', height: '50px' },
    desktop: { width: '60px', height: '60px' },
    expanded: { width: '400px', height: '600px' }
  }
  
  const sizes = { ...defaultSizes, ...customSizes }
  
  if (isExpanded) {
    return isMobile 
      ? { width: '100vw', height: getSafeViewportHeight() }
      : sizes.expanded
  }
  
  return isMobile ? sizes.mobile : sizes.desktop
}

// Safe area insets desteği (iPhone X+ için)
export function getSafeAreaInsets(): {
  top: string
  right: string
  bottom: string
  left: string
} {
  if (typeof window === 'undefined') {
    return { top: '0px', right: '0px', bottom: '0px', left: '0px' }
  }
  
  const computedStyle = getComputedStyle(document.documentElement)
  
  return {
    top: computedStyle.getPropertyValue('--safe-area-inset-top') || '0px',
    right: computedStyle.getPropertyValue('--safe-area-inset-right') || '0px', 
    bottom: computedStyle.getPropertyValue('--safe-area-inset-bottom') || '0px',
    left: computedStyle.getPropertyValue('--safe-area-inset-left') || '0px'
  }
}

// Widget z-index yönetimi
export function getOptimalZIndex(priority: 'low' | 'medium' | 'high' = 'medium'): number {
  const zIndexMap = {
    low: 9999,
    medium: 99999,
    high: 999999
  }
  
  return zIndexMap[priority]
}

// Touch-friendly minimum boyut kontrolü
export function ensureTouchFriendlySize(size: number): number {
  const minTouchSize = 44 // Apple HIG önerisi
  return Math.max(size, minTouchSize)
}

// Widget animasyon durumu
export function getAnimationConfig(isMobile: boolean): {
  duration: string
  easing: string
} {
  return {
    duration: isMobile ? '0.2s' : '0.3s', // Mobilde daha hızlı
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)' // Material Design easing
  }
}