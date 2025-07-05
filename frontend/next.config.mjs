import path from 'path';
import { fileURLToPath } from 'url';

// ES Modüllerinde __dirname karşılığı
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Sadece build'in geçip geçmediğini test etmek için temel ayar
  reactStrictMode: true,

  // YOL KISAYOLU (PATH ALIAS) İÇİN WEBPACK YAPILANDIRMASI
  // Bu, sorunu çözmesi gereken kilit kısımdır.
  webpack: (config) => {
    // Mevcut alias'ları koruyarak yenilerini ekle
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/app': path.resolve(__dirname, 'app'),
      '@/components': path.resolve(__dirname, 'components'),
      '@/lib': path.resolve(__dirname, 'lib'),
      '@/hooks': path.resolve(__dirname, 'hooks'),
      '@/contexts': path.resolve(__dirname, 'contexts'),
      '@/utils': path.resolve(__dirname, 'utils'),
      '@/types': path.resolve(__dirname, 'types'),
      '@/constants': path.resolve(__dirname, 'constants'),
      '@/styles': path.resolve(__dirname, 'styles'),
      '@/public': path.resolve(__dirname, 'public'),
    };
    
    // Module resolution extensions
    config.resolve.extensions = ['.js', '.jsx', '.ts', '.tsx', '.json', ...config.resolve.extensions];
    
    return config;
  },
};

export default nextConfig;