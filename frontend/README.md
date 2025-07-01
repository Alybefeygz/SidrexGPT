# SidrexGPT Frontend

Next.js 15 ile geliştirilmiş modern React frontend uygulaması.

## 🛠️ Teknolojiler

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - UI bileşenleri
- **Axios** - HTTP client
- **React Hook Form** - Form yönetimi
- **Zod** - Schema validation

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Node.js 18+
- npm, yarn, veya pnpm

### Kurulum

```bash
# Dependencies yükleyin
npm install
# veya
pnpm install

# Environment variables ayarlayın
cp env.example .env.local
# .env.local dosyasını düzenleyin

# Development server başlatın
npm run dev
# veya
pnpm dev
```

Uygulama [http://localhost:3000](http://localhost:3000) adresinde çalışacak.

## 📁 Proje Yapısı

```
frontend/
├── app/                 # Next.js App Router
│   ├── api-test/       # API test sayfası
│   ├── brands/         # Marka sayfaları
│   ├── product/        # Ürün sayfaları
│   ├── users/          # Kullanıcı yönetimi
│   └── yonetim/        # Admin paneli
├── components/          # React bileşenleri
│   ├── robots/         # Robot bileşenleri
│   └── ui/             # Temel UI bileşenleri
├── contexts/           # React contexts
├── hooks/              # Custom hooks
├── lib/                # Utility fonksiyonları
└── public/             # Static dosyalar
```

## 🌍 Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Development server başlat
npm run build        # Production build
npm run start        # Production server başlat

# Code Quality
npm run lint         # ESLint çalıştır
npm run lint:fix     # ESLint hatalarını düzelt
npm run type-check   # TypeScript type check
npm run format       # Prettier ile format
npm run format:check # Format kontrolü

# Utilities
npm run clean        # Build dosyalarını temizle
npm run analyze      # Bundle analyzer
```

## 🎨 Styling

- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Headless UI primitives
- **CVA** - Class Variance Authority
- **Lucide React** - Icon library

## 🔌 API Integration

API entegrasyonu `lib/api.ts` dosyasında yapılandırılmıştır:

```typescript
import { api } from '@/lib/api';

// Kullanım
const response = await api.auth.login({
  username: 'user',
  password: 'pass'
});
```

## 🛡️ Type Safety

- **TypeScript** - Full type coverage
- **Zod** - Runtime validation
- **Type-safe** - API responses

## 📱 Components

### Robot Components
- `FirstRobot` - Ana chatbot
- `SecondRobot` - İkincil chatbot
- `ThirdRobot` - Üçüncü chatbot
- `RobotManager` - Robot yönetim sistemi

### UI Components
- Shadcn/ui tabanlı bileşenler
- Fully accessible
- Dark mode support

## 🚀 Deployment

### Vercel (Önerilen)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t sidrexgpt-frontend .
docker run -p 3000:3000 sidrexgpt-frontend
```

### Manual Build
```bash
npm run build
npm run start
```

## 🔧 Development

### Code Style
- ESLint + Prettier
- Husky git hooks
- Conventional commits

### Best Practices
- TypeScript strict mode
- Component isolation
- Custom hooks for logic
- Context for state management

## 📦 Bundle Analysis

Bundle boyutunu analiz etmek için:

```bash
npm run analyze
```

## 🤝 Contributing

1. Feature branch oluşturun
2. Changes yapın
3. Tests ekleyin
4. Linting/formatting kontrol edin
5. Pull request oluşturun

## 📄 License

MIT License 