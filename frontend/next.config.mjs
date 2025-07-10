import path from 'path';
import { fileURLToPath } from 'url';

// ⚡ PERFORMANS: Bundle analyzer import
const withBundleAnalyzer = process.env.ANALYZE === 'true' 
  ? (await import('@next/bundle-analyzer')).default({ enabled: true })
  : (config) => config;

// ES Modüllerinde __dirname karşılığı
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Sadece build'in geçip geçmediğini test etmek için temel ayar
  reactStrictMode: true,

  // ⚡ PERFORMANS: Compiler optimizasyonları
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error']
    } : false,
    reactRemoveProperties: process.env.NODE_ENV === 'production',
  },

  // ⚡ PERFORMANS: Experimental features
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'hebbkx1anhila5yf.public.blob.vercel-storage.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        // Bu hostname'i kendi Supabase proje URL'inizle değiştirin
        // Örneğin: abcdefgh.supabase.co
        hostname: '*.supabase.co',
        port: '',
        pathname: '/storage/v1/object/public/**',
      },
    ],
    // ⚡ PERFORMANS: Image optimizasyonu
    formats: ['image/webp'],
    minimumCacheTTL: 60,
  },

  // ESLint sadece warning'leri göster, build'i durdurma
  eslint: {
    ignoreDuringBuilds: false, // ESLint çalışsın ama build'i durdurmasın
    dirs: ['app', 'components', 'lib', 'hooks', 'contexts'] // Sadece bu klasörleri kontrol et
  },

  // ⚡ PERFORMANS: BASİT AMA ETKİLİ WEBPACK YAPILANDIRMASI
  webpack: (config, { dev, isServer }) => {
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
    
    // ⚡ PERFORMANS: Production optimizasyonları
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
            },
          },
        },
      };
    }
    
    // Debug logging
    if (dev) {
      console.log('🔧 Webpack __dirname:', __dirname);
      console.log('🔧 Webpack @ alias:', config.resolve.alias['@']);
    }
    
    return config;
  },
};

// ⚡ PERFORMANS: Bundle analyzer ile export
export default withBundleAnalyzer(nextConfig);