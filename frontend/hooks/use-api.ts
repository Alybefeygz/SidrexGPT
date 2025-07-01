import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';

// Generic API hook
export function useApi<T>(
  apiCall: () => Promise<{ data: T }>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall();
        setData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.message || err.message || 'Bir hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error, refetch: () => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall();
        setData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.message || err.message || 'Bir hata oluştu');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }};
}

// Authentication hooks
export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (credentials: { username: string; password: string }) => {
    try {
      const response = await api.auth.login(credentials);
      const token = response.data.key;
      localStorage.setItem('authToken', token);
      
      // Kullanıcı bilgilerini al
      const userResponse = await api.auth.getUser();
      setUser(userResponse.data);
      
      return { success: true, data: response.data };
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Giriş başarısız' 
      };
    }
  };

  const register = async (userData: { 
    username: string; 
    email: string; 
    password1: string; 
    password2: string; 
  }) => {
    try {
      const response = await api.auth.register(userData);
      const token = response.data.key;
      localStorage.setItem('authToken', token);
      
      // Kullanıcı bilgilerini al
      const userResponse = await api.auth.getUser();
      setUser(userResponse.data);
      
      return { success: true, data: response.data };
    } catch (error: any) {
      let errorMessage = 'Kayıt başarısız';
      
      if (error.response?.data) {
        const errorData = error.response.data;
        
        // Şifre doğrulama hatalarını Türkçe'ye çevir
        if (errorData.non_field_errors) {
          errorMessage = errorData.non_field_errors.map((err: string) => {
            if (err.includes('too similar to the username')) {
              return 'Şifre kullanıcı adına çok benzer. Daha farklı bir şifre seçin.';
            }
            if (err.includes('too short')) {
              return 'Şifre çok kısa. En az 8 karakter olmalı.';
            }
            if (err.includes('too common')) {
              return 'Bu şifre çok yaygın. Daha güvenli bir şifre seçin.';
            }
            if (err.includes('entirely numeric')) {
              return 'Şifre sadece sayılardan oluşamaz.';
            }
            return err;
          }).join('\n');
        } else if (errorData.password1) {
          errorMessage = errorData.password1.map((err: string) => {
            if (err.includes('too similar to the username')) {
              return 'Şifre kullanıcı adına çok benzer. Daha farklı bir şifre seçin.';
            }
            if (err.includes('too short')) {
              return 'Şifre çok kısa. En az 8 karakter olmalı.';
            }
            if (err.includes('too common')) {
              return 'Bu şifre çok yaygın. Daha güvenli bir şifre seçin.';
            }
            if (err.includes('entirely numeric')) {
              return 'Şifre sadece sayılardan oluşamaz.';
            }
            return err;
          }).join('\n');
        } else {
          errorMessage = JSON.stringify(errorData);
        }
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      // Logout hatasını ignore et
    } finally {
      localStorage.removeItem('authToken');
      setUser(null);
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const response = await api.auth.getUser();
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('authToken');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  return {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };
}

// Profiles hooks
export function useProfiles() {
  return useApi(() => api.profiles.list());
}

export function useProfile(id: number) {
  return useApi(() => api.profiles.get(id), [id]);
}

// Robots hooks
export function useRobots() {
  return useApi(() => api.robots.list());
}

export function useRobot(id: number) {
  return useApi(() => api.robots.get(id), [id]);
}

export function useRobotBySlug(slug: string) {
  return useApi(() => api.robots.getBySlug(slug), [slug]);
}

export function useRobotPDFs(robotId: number) {
  return useApi(() => api.robots.getPDFs(robotId), [robotId]);
}

export function useRobotActivePDFs(robotId: number) {
  return useApi(() => api.robots.getActivePDFs(robotId), [robotId]);
}

// Robot PDF Management hooks
export function useRobotPDFList(robotId?: number, isActive?: boolean, pdfType?: string) {
  return useApi(() => api.robotPDFs.list(robotId, isActive, pdfType), [robotId, isActive, pdfType]);
}

export function useRobotPDFActions() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadPDF = async (robotId: number, file: File, pdfType: 'kural' | 'rol' | 'bilgi' | 'beyan', description?: string) => {
    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('robot_id', robotId.toString());
      formData.append('pdf_dosyasi', file);
      formData.append('pdf_type', pdfType);
      formData.append('dosya_adi', file.name);
      if (description) {
        formData.append('aciklama', description);
      }

      const response = await api.robotPDFs.create(formData);
      return { success: true, data: response.data };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'PDF yükleme başarısız';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const deletePDF = async (pdfId: number) => {
    try {
      setLoading(true);
      setError(null);

      await api.robotPDFs.delete(pdfId);
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'PDF silme başarısız';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const togglePDFActive = async (pdfId: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.robotPDFs.toggleActive(pdfId);
      return { success: true, data: response.data };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'PDF aktivasyon durumu değiştirme başarısız';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const updatePDF = async (pdfId: number, updates: { 
    pdf_type?: 'kural' | 'rol' | 'bilgi' | 'beyan';
    is_active?: boolean;
    aciklama?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.robotPDFs.update(pdfId, updates);
      return { success: true, data: response.data };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'PDF güncelleme başarısız';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return {
    uploadPDF,
    deletePDF,
    togglePDFActive,
    updatePDF,
    loading,
    error,
  };
}

// Robot Chat hook
export function useRobotChat(robotSlug: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const sendMessage = async (message: string, conversationId?: string) => {
    if (!message.trim()) return null;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.chat.sendMessage(robotSlug, message, conversationId);
      return response.data;
    } catch (err: any) {
      // Handle abort error
      if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
        console.log('Chat request cancelled');
        return null;
      }

      // Handle network errors  
      if (err.response?.status === 499) {
        const errorMessage = 'Bağlantı kesildi, lütfen tekrar deneyin';
        setError(errorMessage);
        throw new Error(errorMessage);
      }

      const errorMessage = err.response?.data?.error || 'Mesaj gönderilemedi';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const getRobotInfo = async () => {
    try {
      const response = await api.chat.getRobotInfo(robotSlug);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Robot bilgileri alınamadı';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const cancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  return {
    sendMessage,
    getRobotInfo,
    cancelRequest,
    isLoading,
    error,
    clearError: () => setError(null)
  };
} 