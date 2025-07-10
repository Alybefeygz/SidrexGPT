"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// API'den dönecek olan veri tipi
type AssetData = { [key: string]: string };

interface AssetContextType {
  assets: AssetData;
  getAssetUrl: (key: string) => string;
  isLoading: boolean;
}

const AssetContext = createContext<AssetContextType | undefined>(undefined);

// Varsayılan bir placeholder görsel
const FALLBACK_IMAGE = "/placeholder.svg";

export const AssetProvider = ({ children }: { children: ReactNode }) => {
  const [assets, setAssets] = useState<AssetData>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Django API endpoint'inize göre adresi güncelleyin
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    fetch(`${apiUrl}/api/statik-varliklar/`)
      .then((res) => res.json())
      .then((data) => {
        setAssets(data);
      })
      .catch((error) => {
        console.error("Statik varlıklar alınamadı:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const getAssetUrl = (key: string): string => {
    return assets[key] || FALLBACK_IMAGE;
  };

  return (
    <AssetContext.Provider value={{ assets, getAssetUrl, isLoading }}>
      {children}
    </AssetContext.Provider>
  );
};

export const useAssets = (): AssetContextType => {
  const context = useContext(AssetContext);
  if (context === undefined) {
    throw new Error('useAssets, AssetProvider içinde kullanılmalıdır');
  }
  return context;
}; 