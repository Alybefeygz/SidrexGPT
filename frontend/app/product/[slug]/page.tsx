"use client"

import { ChevronLeft, ChevronRight, Heart, Search, ShoppingCart, User } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import SecondRobot from "@/components/robots/second-robot/SecondRobot"
import ThirdRobot from "@/components/robots/third-robot/ThirdRobot"
import PDFUploader from '@/components/PDFUploader'

// Product data - in a real app this would come from a database
const productData = {
  mag4ever: {
    id: 1,
    name: "Mag4Ever",
    brand: "SIDREX®",
    price: "₺820.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 2,
    description:
      "Mag4Ever Magnezyum Kompleksi ile günlük magnezyum ihtiyacınızı karşılayın. Kas fonksiyonları, enerji metabolizması ve sinir sistemi için özel formül.",
    features: ["Yüksek biyoyararlanım", "4 farklı magnezyum formu", "Günlük 1 kapsül", "Doğal kaynaklı"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/mag4ever-4x4luk-destek.jpg-ktYX6n70Q2oi1i4w10LmIXBKAVo5QU.jpeg",
      "/placeholder.svg?height=400&width=400&text=Mag4Ever+Yan+Görsel",
      "/placeholder.svg?height=400&width=400&text=Mag4Ever+Arka+Görsel",
      "/placeholder.svg?height=400&width=400&text=Mag4Ever+İçerik",
    ],
    ingredients:
      "Magnezyum Sitrat, Magnezyum Malat, Magnezyum Taurat, Magnezyum Bisglisinat, P5P (Piridoksal 5-Fosfat)",
    usage: "Günde 1 kapsül, yemekle birlikte alınız.",
    warnings: "Hamilelik ve emzirme döneminde doktor tavsiyesi ile kullanınız.",
    reviews: [
      {
        id: 1,
        name: "Ahmet K.",
        rating: 5,
        date: "15 Ocak 2024",
        comment: "Ürünü 2 aydır kullanıyorum. Kas kramplarım azaldı ve uyku kalitem arttı. Kesinlikle tavsiye ederim.",
      },
      {
        id: 2,
        name: "Zeynep M.",
        rating: 5,
        date: "8 Ocak 2024",
        comment: "Harika bir ürün! Enerji seviyem arttı ve yorgunluk hissetmiyorum.",
      },
    ],
  },
  "imuntus-kids": {
    id: 2,
    name: "Imuntus Kids",
    brand: "SIDREX®",
    price: "₺340.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 1,
    description:
      "Çocuklar için özel geliştirilmiş bağışıklık destek kompleksi. Doğal C vitamini ve çinko ile güçlendirilmiş formül.",
    features: ["Çocuklar için özel formül", "Doğal C vitamini", "Çinko desteği", "Lezzetli portakal aroması"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/kids1-utA0hSBXrL9EkUPhZWFJ7lwKZJLnU2.webp",
      "/placeholder.svg?height=400&width=400&text=Imuntus+Kids+Yan",
      "/placeholder.svg?height=400&width=400&text=Imuntus+Kids+Arka",
      "/placeholder.svg?height=400&width=400&text=Imuntus+Kids+İçerik",
    ],
    ingredients: "Doğal C Vitamini, Çinko, Ekinezya Ekstraktı, Propolis",
    usage: "4-12 yaş arası çocuklar için günde 1 çay kaşığı.",
    warnings: "Çocukların ulaşamayacağı yerde saklayınız.",
    reviews: [
      {
        id: 1,
        name: "Ayşe T.",
        rating: 5,
        date: "20 Ocak 2024",
        comment: "Çocuğum çok seviyor ve hastalık geçirme sıklığı azaldı.",
      },
    ],
  },
  imuntus: {
    id: 3,
    name: "Imuntus",
    brand: "SIDREX®",
    price: "₺350.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 1,
    description:
      "Yetişkinler için güçlü bağışıklık destek kompleksi. C vitamini, D vitamini ve çinko ile desteklenmiş formül.",
    features: ["Yüksek doz C vitamini", "D3 vitamini desteği", "Çinko ve selenyum", "Zencefilli kompleks"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/imuntus2-Tv1KhhIXJlhyXiJ0V9NvZ3WZQxMIKT.webp",
      "/placeholder.svg?height=400&width=400&text=Imuntus+Yan",
      "/placeholder.svg?height=400&width=400&text=Imuntus+Arka",
      "/placeholder.svg?height=400&width=400&text=Imuntus+İçerik",
    ],
    ingredients: "C Vitamini, D3 Vitamini, Çinko, Selenyum, Ekinezya, Propolis",
    usage: "Günde 1 kapsül, yemekle birlikte alınız.",
    warnings: "Hamilelik döneminde doktor kontrolünde kullanınız.",
    reviews: [
      {
        id: 1,
        name: "Mehmet Y.",
        rating: 5,
        date: "12 Ocak 2024",
        comment: "Kış aylarında bağışıklığımı desteklemek için kullanıyorum. Çok memnunum.",
      },
    ],
  },
  zzen: {
    id: 4,
    name: "Zzen",
    brand: "SIDREX®",
    price: "₺450.00",
    originalPrice: null,
    rating: 4,
    reviewCount: 3,
    description:
      "Stresli günlerde rahatlamanıza yardımcı olan bitkisel formül. St. John's wort, Passiflora ve Valerian içeren özel kompleks.",
    features: ["Doğal bitkisel içerik", "St. John's wort", "Passiflora", "Valerian", "60 kapsül"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/zzen-min-XuU3njKhYs1pyLYt7ewsyrJRaGQs34.webp",
      "/placeholder.svg?height=400&width=400&text=Zzen+Yan",
      "/placeholder.svg?height=400&width=400&text=Zzen+Arka",
      "/placeholder.svg?height=400&width=400&text=Zzen+İçerik",
    ],
    ingredients: "St. John's wort, Passiflora, Valerian, Magnezyum",
    usage: "Günde 1 kapsül, akşam yemeğinden sonra alınız.",
    warnings: "Antidepresan kullananlar doktor kontrolünde kullanmalıdır. Hamilelik ve emzirme döneminde kullanılmaz.",
    reviews: [
      {
        id: 1,
        name: "Selin A.",
        rating: 5,
        date: "5 Şubat 2024",
        comment: "Yoğun iş temposunda rahatlamama yardımcı oluyor. Uyku kalitem arttı.",
      },
      {
        id: 2,
        name: "Burak T.",
        rating: 4,
        date: "28 Ocak 2024",
        comment: "Yaklaşık 2 haftadır kullanıyorum, stres seviyem azaldı diyebilirim.",
      },
      {
        id: 3,
        name: "Deniz K.",
        rating: 4,
        date: "15 Ocak 2024",
        comment: "Doğal içerikli olması tercih sebebim. Etkisinden memnunum.",
      },
    ],
  },
  "milk-thistle-complex": {
    id: 5,
    name: "Milk Thistle Complex",
    brand: "SIDREX®",
    price: "₺380.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 2,
    description:
      "Karaciğer sağlığınızı desteklemek için özel geliştirilmiş bitkisel kompleks. Milk Thistle ve Artichoke ile güçlendirilmiş formül.",
    features: ["Karaciğer desteği", "Milk Thistle ekstraktı", "Artichoke içeriği", "Doğal detoks", "60 kapsül"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/milk-thistle-min-PW6K3sRggfQMXxLg6o9o3lnH60TIyP.webp",
      "/placeholder.svg?height=400&width=400&text=Milk+Thistle+Yan",
      "/placeholder.svg?height=400&width=400&text=Milk+Thistle+Arka",
      "/placeholder.svg?height=400&width=400&text=Milk+Thistle+İçerik",
    ],
    ingredients: "Milk Thistle Ekstraktı, Artichoke Ekstraktı, Dandelion, Kurkuma",
    usage: "Günde 1 kapsül, yemekle birlikte alınız.",
    warnings:
      "Hamilelik ve emzirme döneminde doktor tavsiyesi ile kullanınız. Safra taşı olanlar dikkatli kullanmalıdır.",
    reviews: [
      {
        id: 1,
        name: "Fatma S.",
        rating: 5,
        date: "10 Şubat 2024",
        comment: "Karaciğer değerlerimde iyileşme gözlemliyorum. Doktor tavsiyesi ile kullanıyorum.",
      },
      {
        id: 2,
        name: "Okan M.",
        rating: 5,
        date: "3 Şubat 2024",
        comment: "Detoks programımın bir parçası olarak kullanıyorum. Kendimi daha enerjik hissediyorum.",
      },
    ],
  },
  "repro-womens-once-daily": {
    id: 6,
    name: "Repro Women's Once Daily",
    brand: "SIDREX®",
    price: "₺520.00",
    originalPrice: null,
    rating: 4,
    reviewCount: 4,
    description:
      "Kadın üreme sağlığını desteklemek için özel geliştirilmiş formül. Inositol, Black Cohosh ve Chaste Tree içeren günlük destek kompleksi.",
    features: ["Kadın sağlığı desteği", "Inositol içeriği", "Black Cohosh", "Chaste Tree", "30 saşe", "Vişne aromalı"],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/repro-UouuFfi8lwFW93zCZjXojwCNhTPKZj.webp",
      "/placeholder.svg?height=400&width=400&text=Repro+Women+Yan",
      "/placeholder.svg?height=400&width=400&text=Repro+Women+Arka",
      "/placeholder.svg?height=400&width=400&text=Repro+Women+İçerik",
    ],
    ingredients: "Inositol, Black Cohosh Ekstraktı, Chaste Tree Ekstraktı, Folik Asit, B6 Vitamini",
    usage: "Günde 1 saşe, bol su ile karıştırarak alınız.",
    warnings: "Hamilelik ve emzirme döneminde kullanılmaz. Hormon tedavisi alanlar doktor kontrolünde kullanmalıdır.",
    reviews: [
      {
        id: 1,
        name: "Elif K.",
        rating: 5,
        date: "18 Şubat 2024",
        comment: "Düzensiz döngülerim düzelmeye başladı. Doktor tavsiyesi ile kullanıyorum.",
      },
      {
        id: 2,
        name: "Seda M.",
        rating: 4,
        date: "12 Şubat 2024",
        comment: "Vişne aroması çok güzel, içmesi kolay. Etkilerini görmeye başladım.",
      },
      {
        id: 3,
        name: "Aylin T.",
        rating: 4,
        date: "8 Şubat 2024",
        comment: "Doğal içerikli olması beni memnun ediyor. Düzenli kullanıyorum.",
      },
      {
        id: 4,
        name: "Merve A.",
        rating: 4,
        date: "1 Şubat 2024",
        comment: "Saşe formatı çok pratik. Çantamda taşıyabiliyorum.",
      },
    ],
  },
  "slm-x": {
    id: 7,
    name: "Slm-X",
    brand: "SIDREX®",
    price: "₺480.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 1,
    description:
      "Kilo yönetimi ve metabolizma desteği için özel geliştirilmiş formül. Bromelain, CLA ve Yeşil Çay ekstraktı içeren doğal kompleks.",
    features: [
      "Metabolizma desteği",
      "Bromelain enzimi",
      "CLA içeriği",
      "Yeşil çay ekstraktı",
      "30 saşe",
      "Ananas aromalı",
    ],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/slm-x-2000x1500-lwKm2kXPzFgkv3s4RJVq6BxpGWgPvT.webp",
      "/placeholder.svg?height=400&width=400&text=Slm-X+Yan",
      "/placeholder.svg?height=400&width=400&text=Slm-X+Arka",
      "/placeholder.svg?height=400&width=400&text=Slm-X+İçerik",
    ],
    ingredients: "Bromelain, CLA (Konjuge Linoleik Asit), Yeşil Çay Ekstraktı, L-Karnitin, Krom",
    usage: "Günde 1 saşe, yemeklerden 30 dakika önce bol su ile karıştırarak alınız.",
    warnings: "Hamilelik ve emzirme döneminde kullanılmaz. Kalp rahatsızlığı olanlar doktor kontrolünde kullanmalıdır.",
    reviews: [
      {
        id: 1,
        name: "Gizem Y.",
        rating: 5,
        date: "22 Şubat 2024",
        comment: "Ananas aroması harika! 3 haftada 2 kilo verdim. Diyet ve sporla birlikte kullanıyorum.",
      },
    ],
  },
  olivia: {
    id: 8,
    name: "Olivia",
    brand: "SIDREX®",
    price: "₺650.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 5,
    description:
      "Eklem sağlığı ve hareket kabiliyetinizi desteklemek için özel geliştirilmiş formül. Zeytin yaprağı, Tip II kolajen ve yumurta kabuğu zarı içeren doğal kompleks.",
    features: [
      "Eklem sağlığı desteği",
      "Zeytin yaprağı ekstraktı",
      "Tip II kolajen",
      "Yumurta kabuğu zarı",
      "60 tablet",
      "Doğal antioksidan",
    ],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/olivia-min-0XPLLm2bMIeF0uCYl0bUhPVyiRcjdt.webp",
      "/placeholder.svg?height=400&width=400&text=Olivia+Yan",
      "/placeholder.svg?height=400&width=400&text=Olivia+Arka",
      "/placeholder.svg?height=400&width=400&text=Olivia+İçerik",
    ],
    ingredients: "Zeytin Yaprağı Ekstraktı, Tip II Kolajen, Yumurta Kabuğu Zarı, Glukozamin, Kondroitin",
    usage: "Günde 2 tablet, yemekle birlikte alınız.",
    warnings:
      "Hamilelik ve emzirme döneminde doktor tavsiyesi ile kullanınız. Yumurta alerjisi olanlar kullanmamalıdır.",
    reviews: [
      {
        id: 1,
        name: "Mehmet A.",
        rating: 5,
        date: "25 Şubat 2024",
        comment: "Eklem ağrılarım azaldı. 1 aydır kullanıyorum ve çok memnunum.",
      },
      {
        id: 2,
        name: "Fatma K.",
        rating: 5,
        date: "20 Şubat 2024",
        comment: "Doğal içerikli olması çok güzel. Hareket kabiliyetim arttı.",
      },
      {
        id: 3,
        name: "Ali S.",
        rating: 5,
        date: "15 Şubat 2024",
        comment: "Spor sonrası eklem ağrılarım için kullanıyorum. Etkili bir ürün.",
      },
      {
        id: 4,
        name: "Zeynep T.",
        rating: 5,
        date: "10 Şubat 2024",
        comment: "Yaşlılık nedeniyle olan eklem problemlerim için doktor tavsiyesi ile başladım. Çok iyi geldi.",
      },
      {
        id: 5,
        name: "Hasan Y.",
        rating: 5,
        date: "5 Şubat 2024",
        comment: "Kaliteli bir ürün. Tablet formunda olması kullanımını kolaylaştırıyor.",
      },
    ],
  },
  "lipo-iron-complex": {
    id: 9,
    name: "Lipo Iron Complex",
    brand: "SIDREX®",
    price: "₺420.00",
    originalPrice: null,
    rating: 4,
    reviewCount: 2,
    description:
      "Enerji metabolizması ve kan oluşumunu desteklemek için özel geliştirilmiş demir kompleksi. C vitamini, folik asit ve B vitaminleri ile güçlendirilmiş formül.",
    features: [
      "Yüksek emilimli demir",
      "C vitamini desteği",
      "Folik asit içeriği",
      "B1, B6, B12 vitaminleri",
      "30 kapsül",
      "Enerji metabolizması desteği",
    ],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/lipo-min-isGkebP1l5Sirltc6pwh4git4SU34G.webp",
      "/placeholder.svg?height=400&width=400&text=Lipo+Iron+Yan",
      "/placeholder.svg?height=400&width=400&text=Lipo+Iron+Arka",
      "/placeholder.svg?height=400&width=400&text=Lipo+Iron+İçerik",
    ],
    ingredients: "Demir Bisglisinat, C Vitamini, Folik Asit, B1 Vitamini, B6 Vitamini, B12 Vitamini",
    usage: "Günde 1 kapsül, aç karnına veya yemekle birlikte alınız.",
    warnings:
      "Hamilelik ve emzirme döneminde doktor tavsiyesi ile kullanınız. Demir fazlalığı olanlar kullanmamalıdır.",
    reviews: [
      {
        id: 1,
        name: "Ayşe D.",
        rating: 4,
        date: "28 Şubat 2024",
        comment: "Yorgunluğum azaldı. 2 haftadır kullanıyorum ve enerji seviyem arttı.",
      },
      {
        id: 2,
        name: "Mehmet K.",
        rating: 4,
        date: "22 Şubat 2024",
        comment: "Doktor tavsiyesi ile başladım. Mide rahatsızlığı yapmıyor, iyi tolere ediyorum.",
      },
    ],
  },
  "pro-mens-once-daily": {
    id: 10,
    name: "Pro Men's Once Daily",
    brand: "SIDREX®",
    price: "₺390.00",
    originalPrice: null,
    rating: 5,
    reviewCount: 3,
    description:
      "Erkek sağlığını desteklemek için özel geliştirilmiş formül. Saw Palmetto, Kabak Çekirdeği ve Tribulus içeren günlük destek kompleksi.",
    features: [
      "Erkek sağlığı desteği",
      "Saw Palmetto ekstraktı",
      "Kabak çekirdeği ekstraktı",
      "Tribulus içeriği",
      "30 tablet",
      "Prostat sağlığı desteği",
    ],
    images: [
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/pro-mens-min-p26ZoavCZ6iC5x5q8RQGvKLk7LdB9v.webp",
      "/placeholder.svg?height=400&width=400&text=Pro+Men+Yan",
      "/placeholder.svg?height=400&width=400&text=Pro+Men+Arka",
      "/placeholder.svg?height=400&width=400&text=Pro+Men+İçerik",
    ],
    ingredients: "Saw Palmetto Ekstraktı, Kabak Çekirdeği Ekstraktı, Tribulus Terrestris, Çinko, Selenyum",
    usage: "Günde 1 tablet, yemekle birlikte alınız.",
    warnings: "Hormon tedavisi alanlar doktor kontrolünde kullanmalıdır.",
    reviews: [
      {
        id: 1,
        name: "Ali Y.",
        rating: 5,
        date: "25 Şubat 2024",
        comment: "40 yaş üstü erkekler için ideal bir ürün. İdrar problemlerimde azalma oldu.",
      },
      {
        id: 2,
        name: "Mehmet S.",
        rating: 5,
        date: "18 Şubat 2024",
        comment: "Doktor tavsiyesi ile kullanıyorum. Prostat sağlığımı desteklemek için ideal.",
      },
      {
        id: 3,
        name: "Hakan T.",
        rating: 5,
        date: "10 Şubat 2024",
        comment: "Tablet formunda olması kullanımını kolaylaştırıyor. Etkisinden memnunum.",
      },
    ],
  },
}

interface ProductPageProps {
  params: Promise<{
    slug: string
  }>
}

export default function ProductPage({ params }: ProductPageProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [quantity, setQuantity] = useState(1)
  const [activeTab, setActiveTab] = useState("description")
  const [slug, setSlug] = useState<string>("")
  
  // Chat state for robot
  const [activeChatRobot, setActiveChatRobot] = useState<string | null>(null)

  // Handle async params in useEffect for client component
  useEffect(() => {
    params.then(({ slug }) => setSlug(slug))
  }, [params])

  // Get product data based on slug
  const product = slug ? productData[slug as keyof typeof productData] : null

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Ürün Bulunamadı</h1>
          <p className="text-gray-600 mb-8">Aradığınız ürün mevcut değil.</p>
          <Link href="/">
            <Button>Ana Sayfaya Dön</Button>
          </Link>
        </div>
      </div>
    )
  }

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % product.images.length)
  }

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + product.images.length) % product.images.length)
  }

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    // Chat toggle logic
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Top Banner */}
      <div className="bg-emerald-400 text-white text-center py-2 text-sm font-medium">TÜM ÜYELERİ KARGO BEDAVA</div>

      {/* Navigation */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex-shrink-0">
              <Link href="/" className="text-2xl font-bold text-slate-800">
                Sidrex
              </Link>
            </div>

            <nav className="hidden md:flex space-x-8">
              <Link href="/" className="text-emerald-500 hover:text-emerald-600 font-medium">
                Ürünlerimiz
              </Link>
              <Link href="/sidrexgpt" className="text-slate-700 hover:text-slate-900">
                SidrexGPT's
              </Link>
              <Link href="/yonetim" className="text-slate-700 hover:text-slate-900">
                Yönetim
              </Link>
            </nav>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="icon">
                <Search className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="relative">
                <ShoppingCart className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  0
                </span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="bg-gray-50 py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="text-sm">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              Tüm Ürünler
            </Link>
            <span className="mx-2 text-gray-400">{">"}</span>
            <Link href="#" className="text-gray-500 hover:text-gray-700">
              Oral Takviyeler
            </Link>
            <span className="mx-2 text-gray-400">{">"}</span>
            <span className="text-gray-900">{product.name}</span>
          </nav>
        </div>
      </div>

      {/* Product Details */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative bg-gray-100 rounded-lg overflow-hidden aspect-square">
              <Image
                src={product.images[currentImageIndex] || "/placeholder.svg"}
                alt={product.name}
                fill
                className="object-cover"
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white"
                onClick={prevImage}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white"
                onClick={nextImage}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Thumbnail Images */}
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((image, index) => (
                <button
                  key={index}
                  className={`relative aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 ${
                    index === currentImageIndex ? "border-emerald-500" : "border-transparent"
                  }`}
                  onClick={() => setCurrentImageIndex(index)}
                >
                  <Image
                    src={image || "/placeholder.svg"}
                    alt={`${product.name} ${index + 1}`}
                    fill
                    className="object-cover"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-emerald-600 font-medium">{product.brand}</span>
                <Button variant="ghost" size="icon">
                  <Heart className="h-5 w-5" />
                </Button>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <span key={i} className={i < product.rating ? "text-yellow-400" : "text-gray-300"}>
                      ★
                    </span>
                  ))}
                </div>
                <span className="text-sm text-gray-600">{product.reviewCount} değerlendirme</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-6">{product.price}</div>
            </div>

            <div className="space-y-4">
              <p className="text-gray-600">{product.description}</p>

              <div className="space-y-2">
                <h3 className="font-semibold text-gray-900">Özellikler:</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {product.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Quantity and Add to Cart */}
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-gray-700">Adet:</span>
                <div className="flex items-center">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  >
                    -
                  </Button>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, Number.parseInt(e.target.value) || 1))}
                    className="w-16 h-8 text-center border border-gray-300 rounded mx-2"
                    min="1"
                  />
                  <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setQuantity(quantity + 1)}>
                    +
                  </Button>
                </div>
              </div>

              <Button className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3">
                SEPETE EKLE
              </Button>

              <Button variant="outline" className="w-full border-emerald-500 text-emerald-500 hover:bg-emerald-50">
                📱 WHATSAPP
              </Button>
            </div>

            {/* Product Details Tabs */}
            <div className="space-y-4">
              <div className="border-b">
                <nav className="flex space-x-8">
                  <button
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "description"
                        ? "border-emerald-500 text-emerald-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setActiveTab("description")}
                  >
                    Ürün Açıklaması
                  </button>
                  <button
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "ingredients"
                        ? "border-emerald-500 text-emerald-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setActiveTab("ingredients")}
                  >
                    İçerik
                  </button>
                  <button
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "usage"
                        ? "border-emerald-500 text-emerald-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setActiveTab("usage")}
                  >
                    Kullanım
                  </button>
                </nav>
              </div>

              <div className="py-4">
                {activeTab === "description" && (
                  <div className="text-gray-600">
                    <p>{product.description}</p>
                  </div>
                )}
                {activeTab === "ingredients" && (
                  <div className="text-gray-600">
                    <p>{product.ingredients}</p>
                  </div>
                )}
                {activeTab === "usage" && (
                  <div className="text-gray-600">
                    <p>
                      <strong>Kullanım:</strong> {product.usage}
                    </p>
                    <p className="mt-2">
                      <strong>Uyarılar:</strong> {product.warnings}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Yorumlar</h2>
          <div className="space-y-6">
            {product.reviews.map((review) => (
              <Card key={review.id} className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-gray-900">{review.name}</span>
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <span key={i} className={i < review.rating ? "text-yellow-400" : "text-gray-300"}>
                            ★
                          </span>
                        ))}
                      </div>
                      <span className="text-sm text-gray-500">{review.date}</span>
                    </div>
                    <p className="text-gray-600">{review.comment}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Floating Second Robot for mag4ever and related products */}
      {(slug === 'mag4ever' || product.name === 'Mag4Ever') && (
        <div className="fixed bottom-6 right-6 z-50">
          <SecondRobot
            onChatToggle={handleChatToggle}
            isOtherChatOpen={activeChatRobot !== null && activeChatRobot !== "second"}
            isFloating={true}
          />
        </div>
      )}

      {/* Floating Third Robot for imuntus-kids and related products */}
      {(slug === 'imuntus-kids' || product.name === 'Imuntus Kids') && (
        <div className="fixed bottom-6 right-6 z-50">
          <ThirdRobot
            onChatToggle={handleChatToggle}
            isOtherChatOpen={activeChatRobot !== null && activeChatRobot !== "third"}
            isFloating={true}
          />
        </div>
      )}

      <PDFUploader 
        robotId={product.id} 
        initialPdfs={[]} 
        refetchPdfs={() => {}}
      />
    </div>
  )
}
