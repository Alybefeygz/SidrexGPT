import Image from 'next/image'
import { useState } from 'react'

interface ProductImageProps {
  src: string
  alt: string
  width?: number
  height?: number
}

export function ProductImage({ src, alt, width = 400, height = 400 }: ProductImageProps) {
  const [isLoading, setLoading] = useState(true)

  return (
    <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        className={`
          duration-700 ease-in-out
          ${isLoading ? 'scale-105 blur-lg' : 'scale-100 blur-0'}
        `}
        onLoadingComplete={() => setLoading(false)}
        priority={true}  // LCP için önemli görsellerde kullan
        quality={80}     // Kalite/boyut optimizasyonu
      />
    </div>
  )
} 