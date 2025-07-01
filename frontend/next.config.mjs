/** @type {import('next').NextConfig} */
const nextConfig = {
  // Build optimizasyonları
  eslint: {
    ignoreDuringBuilds: process.env.NODE_ENV === 'production' ? false : true,
  },
  typescript: {
    ignoreBuildErrors: process.env.NODE_ENV === 'production' ? false : true,
  },
  
  experimental: {
    allowedDevOrigins: ["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.1.16:3000"],
  },

  // Image optimizasyonu - production'da optimize et
  images: {
    unoptimized: process.env.NODE_ENV === 'development',
    domains: ['localhost', '127.0.0.1', '192.168.1.16'],
    formats: ['image/webp', 'image/avif'],
  },

  // Performance optimizasyonları
  // swcMinify: true,
  compress: true,

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN', // İframe kullanımına izin ver
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Access-Control-Allow-Credentials',
            value: 'true',
          },
          {
            key: 'Access-Control-Allow-Origin',
            value: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET,POST,PUT,DELETE,OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version',
          },
        ],
      },
      {
        // İframe sayfaları için özel ayarlar
        source: '/iframe/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'ALLOWALL', // İframe sayfaları için tam izin
          },
        ],
      },
    ]
  },

  // Environment variables validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
    NEXT_PUBLIC_FRONTEND_URL: process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000',
  },

  // Production build optimizasyonları
  ...(process.env.NODE_ENV === 'production' && {
    output: 'standalone',
    productionBrowserSourceMaps: false,
  }),
}

export default nextConfig
