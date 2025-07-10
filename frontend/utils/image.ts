export function getOptimizedImageUrl(url: string, width: number = 400) {
  // Supabase Storage transform parametreleri
  const params = new URLSearchParams({
    width: width.toString(),
    quality: "80",
    format: "webp"  // Modern format
  })
  
  return `${url}?${params.toString()}`
} 