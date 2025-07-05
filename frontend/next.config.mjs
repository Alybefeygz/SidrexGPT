import path from 'path';
import { fileURLToPath } from 'url';

// ES Modüllerinde __dirname karşılığı
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Sadece build'in geçip geçmediğini test etmek için temel ayar
  reactStrictMode: true,

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'hebbkx1anhila5yf.public.blob.vercel-storage.com',
        port: '',
        pathname: '/**',
      },
    ],
  },

  // ESLint sadece warning'leri göster, build'i durdurma
  eslint: {
    ignoreDuringBuilds: false, // ESLint çalışsın ama build'i durdurmasın
    dirs: ['app', 'components', 'lib', 'hooks', 'contexts'] // Sadece bu klasörleri kontrol et
  },

  // BASİT AMA ETKİLİ WEBPACK YAPILANDIRMASI
  webpack: (config, { dev }) => {
    // Alias yapılandırması - Render ve Bun için optimize edilmiş
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    };
    
    // Daha agresif module resolution
    config.resolve.modules = [
      path.resolve(__dirname),
      path.resolve(__dirname, 'node_modules'),
      'node_modules'
    ];
    
    // File extensions - priority order
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];
    
    // Debug logging
    if (dev) {
      console.log('🔧 Webpack __dirname:', __dirname);
      console.log('🔧 Webpack @ alias:', config.resolve.alias['@']);
    }
    
    return config;
  },
};

export default nextConfig;