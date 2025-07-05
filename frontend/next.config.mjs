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
    config.resolve.alias['@'] = path.resolve(__dirname);
    return config;
  },
};

export default nextConfig;