"use client"

import { ChevronLeft, ChevronRight } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Navbar } from "@/components/Navbar"
import FirstRobot from "@/components/robots/first-robot/FirstRobot"
import { useProducts } from "@/hooks/use-products"

export default function HomePage() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [activeChatRobot, setActiveChatRobot] = useState<boolean>(false)
  const { products, loading, error } = useProducts()

  const handleChatToggle = (robotId: string, isOpen: boolean) => {
    setActiveChatRobot(isOpen)
  }



  // Add quantity state
  const [quantities, setQuantities] = useState<{ [key: number]: number }>({})

  const updateQuantity = (productId: number, change: number) => {
    setQuantities((prev) => ({
      ...prev,
      [productId]: Math.max(1, (prev[productId] || 1) + change),
    }))
  }

  const slides = [
    {
      image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/banner1-PQ6KwiOBAUfmip58IxI7QNdoXYgxOC.webp",
      alt: "Sidrex Imuntus ve Imuntus Kids Ürünleri",
    },
    {
      image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/banner2-pnVTo9Cy5d898JjQGlgZczZlAZte5L.webp",
      alt: "Sidrex Mag4Ever - 4/4'lük Destek Doğasında Var",
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      <Navbar currentPage="products" />

      {/* Hero Banner Carousel */}
      <section className="relative overflow-hidden">
        <div className="relative w-full h-96 bg-gray-100">
          <Image
            src={slides[currentSlide].image || "/placeholder.svg"}
            alt={slides[currentSlide].alt}
            fill
            className="object-cover object-center transition-opacity duration-500"
            priority
            sizes="100vw"
          />
        </div>

        {/* Navigation Arrows */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:bg-white/20 bg-black/20 backdrop-blur-sm"
          onClick={() => setCurrentSlide(currentSlide > 0 ? currentSlide - 1 : slides.length - 1)}
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:bg-white/20 bg-black/20 backdrop-blur-sm"
          onClick={() => setCurrentSlide(currentSlide < slides.length - 1 ? currentSlide + 1 : 0)}
        >
          <ChevronRight className="h-6 w-6" />
        </Button>

        {/* Dots Indicator */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
          {slides.map((_, index) => (
            <button
              key={index}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                index === currentSlide ? "bg-white scale-110" : "bg-white/50 hover:bg-white/70"
              }`}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </section>

      {/* Scrolling Banner */}
      <div className="bg-emerald-400 text-white py-2 overflow-hidden">
        <div className="animate-scroll whitespace-nowrap">
          <span className="mx-8">Üye Olanlara İlk Alışverişinde Sepette Ekstra %5 İndirim</span>
          <span className="mx-8">Üye Olanlara İlk Alışverişinde Sepette Ekstra %5 İndirim</span>
          <span className="mx-8">Üye Olanlara İlk Alışverişinde Sepette Ekstra %5 İndirim</span>
        </div>
      </div>

      {/* Products Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-slate-800 mb-12">Sizin Sidrex'iniz Hangisi?</h2>

          {loading && (
            <div className="text-center py-8">
              <p className="text-gray-600">Ürünler yükleniyor...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-8">
              <p className="text-red-600">Hata: {error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {products.map((product) => (
              <Link key={product.id} href={`/product/${product.slug}`}>
                <Card
                  className={`${product.bg_color} border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-pointer`}
                >
                  <CardContent className="p-6">
                    {/* Square Product Display */}
                    <div className="relative w-full h-48 mb-6 overflow-hidden rounded-lg">
                      <Image
                        src={product.primary_image?.public_url || "/placeholder.svg"}
                        alt={product.primary_image?.alt_text || product.name}
                        fill
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        className="object-cover"
                      />
                    </div>

                    {/* Brand and Product Name */}
                    <div className="text-left mb-4">
                      <p className="text-sm text-gray-600 mb-1">{product.brand}</p>
                      <h3 className="text-xl font-bold text-gray-800">{product.name}</h3>
                    </div>

                    {/* Rating */}
                    <div className="flex items-center justify-start mb-4">
                      <div className="flex text-yellow-400 mr-2">
                        {[...Array(5)].map((_, i) => (
                          <span key={i} className={i < product.rating ? "text-yellow-400" : "text-gray-300"}>
                            ★
                          </span>
                        ))}
                      </div>
                      <span className="text-sm text-gray-600">
                        {product.review_count} değerlendirme
                      </span>
                    </div>

                    {/* Price */}
                    <div className="text-left mb-6">
                      <span className="text-2xl font-bold text-gray-800">{product.price}</span>
                    </div>

                    {/* Quantity Selector and Add to Cart - Side by Side */}
                    <div className="flex items-center gap-4" onClick={(e) => e.preventDefault()}>
                      {/* Quantity Selector */}
                      <div className="flex items-center">
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 rounded-full"
                          onClick={(e) => {
                            e.stopPropagation()
                            updateQuantity(product.id, -1)
                          }}
                        >
                          -
                        </Button>
                        <input
                          type="number"
                          value={quantities[product.id] || 1}
                          onChange={(e) => {
                            e.stopPropagation()
                            setQuantities((prev) => ({
                              ...prev,
                              [product.id]: Math.max(1, Number.parseInt(e.target.value) || 1),
                            }))
                          }}
                          className="w-12 h-8 text-center border border-gray-300 rounded mx-2"
                          min="1"
                          onClick={(e) => e.stopPropagation()}
                        />
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 rounded-full"
                          onClick={(e) => {
                            e.stopPropagation()
                            updateQuantity(product.id, 1)
                          }}
                        >
                          +
                        </Button>
                      </div>

                      {/* Add to Cart Button */}
                      <Button
                        className="flex-1 bg-white border-2 border-gray-800 text-gray-800 hover:bg-gray-800 hover:text-white font-semibold py-2 px-4 rounded transition-colors duration-200"
                        onClick={(e) => e.stopPropagation()}
                      >
                        SEPETE EKLE
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Floating Robot Chat - Fixed Bottom Right */}
      <div className="fixed bottom-6 right-6 z-50">
        <FirstRobot
          onChatToggle={handleChatToggle}
          isOtherChatOpen={false}
          isFloating={true}
        />
      </div>
    </div>
  )
}
