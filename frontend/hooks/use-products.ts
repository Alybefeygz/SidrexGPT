'use client'

import { useState, useEffect } from 'react'

export interface ProductImage {
  id: number
  supabase_path: string
  public_url: string
  is_primary: boolean
  order: number
  alt_text: string
}

export interface ProductFeature {
  id: number
  feature: string
  order: number
}

export interface ProductReview {
  id: number
  name: string
  rating: number
  comment: string
  date: string
  order: number
}

export interface Product {
  id: number
  name: string
  slug: string
  brand: string
  price: string
  original_price?: string
  rating: number
  review_count: number
  bg_color: string
  primary_image?: ProductImage
  // Detay sayfası için ek alanlar
  description?: string
  ingredients?: string
  usage?: string
  warnings?: string
  images?: ProductImage[]
  features?: ProductFeature[]
  reviews?: ProductReview[]
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useProducts() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProducts() {
      try {
        setLoading(true)
        const response = await fetch(`${API_BASE_URL}/api/products/`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setProducts(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ürünler yüklenirken bir hata oluştu')
        console.error('Products fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  return { products, loading, error }
}

export function useProduct(slug: string) {
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return

    async function fetchProduct() {
      try {
        setLoading(true)
        const response = await fetch(`${API_BASE_URL}/api/products/${slug}/`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setProduct(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ürün yüklenirken bir hata oluştu')
        console.error('Product fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [slug])

  return { product, loading, error }
} 