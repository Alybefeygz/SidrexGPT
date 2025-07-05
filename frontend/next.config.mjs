import path from 'path';
import { fileURLToPath } from 'url';

// ES Modüllerinde __dirname karşılığı
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Sadece build'in geçip geçmediğini test etmek için temel ayar
  reactStrictMode: true,

  // Experimental features for better compatibility
  experimental: {
    // These can help with module resolution
    esmExternals: true,
    appDir: true,
  },

  // RENDER + BUN İÇİN GÜÇLÜ WEBPACK YAPILANDIRMASI
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Mevcut alias'ları tamamen override et
    config.resolve.alias = {
      ...config.resolve.alias,
      // Ana alias
      '@': path.resolve(__dirname),
      
      // Spesifik klasör alias'ları
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
      
      // Tam dosya yolu alias'ları (Bun için)
      '@/lib/api': path.resolve(__dirname, 'lib', 'api.ts'),
      '@/lib/utils': path.resolve(__dirname, 'lib', 'utils.ts'),
    };
    
    // Module resolution için fallback'ler ekle
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      os: false,
    };
    
    // Module resolution extensions - sıralama önemli
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json', '.mjs'];
    
    // Daha esnek module resolution
    config.resolve.symlinks = false;
    config.resolve.preferRelative = true;
    
    // Bun compatibility için
    if (process.env.NODE_ENV === 'production') {
      config.resolve.conditionNames = ['import', 'module', 'browser', 'default'];
    }
    
    // Debug için alias'ları logla
    if (dev) {
      console.log('🔍 Webpack Aliases:', config.resolve.alias);
    }
    
    return config;
  },
};

export default nextConfig;