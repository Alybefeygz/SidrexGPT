import axios from 'axios';
import { AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime';

// Backend API base URL - Environment variables'tan alınır
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
                     (process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL + '/api' : 'http://localhost:8000/api');

// Debug: API URL'ini konsola yazdır
console.log('🌐 API Base URL:', API_BASE_URL);
console.log('🔍 Environment Variables:', {
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
});

// ⚡ PERFORMANS: Response Cache için basit Map
const responseCache = new Map();
const CACHE_DURATION = 60000; // 1 dakika

// Router instance for navigation
let router: AppRouterInstance | null = null;

export const setApiRouter = (routerInstance: AppRouterInstance) => {
  router = routerInstance;
};

// Axios instance oluşturma
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // ⚡ PERFORMANS: 60 saniye timeout (eski: 30 saniye)
  withCredentials: true
});

// Add Authorization header for authenticated requests
apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ⚡ PERFORMANS: Cache helper fonksiyonları
function getCacheKey(config: any): string {
  return `${config.method}-${config.url}-${JSON.stringify(config.params)}`;
}

function getCachedResponse(cacheKey: string) {
  const cached = responseCache.get(cacheKey);
  if (cached && (Date.now() - cached.timestamp < CACHE_DURATION)) {
    return cached.data;
  }
  return null;
}

function setCachedResponse(cacheKey: string, data: any) {
  responseCache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  
  // Cache boyutunu sınırla (maksimum 100 entry)
  if (responseCache.size > 100) {
    const firstKey = responseCache.keys().next().value;
    responseCache.delete(firstKey);
  }
}

// Helper function to get CSRF token from cookies


// CSRF token alma - zorunlu
export const ensureCSRFToken = async (): Promise<void> => {
  try {
    console.log('🔄 CSRF token alınıyor...');
    const response = await apiClient.get('/csrf/');
    const csrfTokenValue = response.data.csrf_token;

    if (csrfTokenValue) {
      localStorage.setItem('csrfTokenValue', csrfTokenValue);
      console.log("CSRF token başarıyla alındı ve localStorage'a kaydedildi.");
    } else {
      throw new Error('CSRF token yanıt gövdesinde bulunamadı.');
    }
  } catch (error) {
    console.error('❌ CSRF token alınırken hata:', error);
    throw new Error('CSRF token alınamadı. Lütfen sayfayı yenileyin.');
  }
};

// Auto-retry with CSRF token
async function apiCallWithCSRF<T>(apiCall: () => Promise<T>, retryOnce = true): Promise<T> {
  try {
    return await apiCall();
  } catch (error: any) {
    // CSRF hatası ve retry hakkımız varsa
    if (retryOnce && error.response?.status === 403 && 
        error.response?.data?.detail?.includes('CSRF')) {
      
      console.log('🔄 CSRF hatası tespit edildi, token yenileniyor...');
      await ensureCSRFToken();
      return await apiCall(); // Tekrar dene
    }
    throw error;
  }
}

// Request interceptor to add CSRF token and handle content type
apiClient.interceptors.request.use(
  (config) => {
    // ⚡ PERFORMANS: GET istekleri için cache kontrolü
    if (config.method === 'get') {
      const cacheKey = getCacheKey(config);
      const cachedResponse = getCachedResponse(cacheKey);
      if (cachedResponse) {
        // Cache'den veri varsa, isteği iptal et ve cache'den döndür
        (config as any).adapter = () => Promise.resolve({
          data: cachedResponse,
          status: 200,
          statusText: 'OK (from cache)',
          headers: {},
          config
        });
      }
    }
    
    // Add CSRF token for all methods except GET and HEAD
    if (typeof window !== 'undefined' && config.method && !['GET', 'HEAD'].includes(config.method.toUpperCase())) {
      const csrfToken = localStorage.getItem('csrfTokenValue');
      if (csrfToken && config.headers) {
        config.headers['X-CSRFToken'] = csrfToken;
      } else {
        console.warn('CSRF token not found in localStorage');
      }
    }

    // Set default content type if not set
    if (config.headers && !config.headers['Content-Type']) {
      if (config.data instanceof FormData) {
        // FormData için content type'ı axios'un otomatik belirlemesine izin ver
        delete config.headers['Content-Type'];
      } else {
        config.headers['Content-Type'] = 'application/json';
      }
    }

    // Set Accept header
    if (config.headers) {
      config.headers['Accept'] = 'application/json';
      config.headers['X-Requested-With'] = 'XMLHttpRequest';
    }
    
    // Credentials'ı her zaman gönder
    config.withCredentials = true;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for better error handling and token management
apiClient.interceptors.response.use(
  (response) => {
    // ⚡ PERFORMANS: GET isteklerini cache'le
    if (response.config.method === 'get') {
      const cacheKey = getCacheKey(response.config);
      setCachedResponse(cacheKey, response.data);
    }
    
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Router kullanarak soft navigation yap (hard redirect yerine)
      if (router) {
        router.push('/yonetim');
      } else if (typeof window !== 'undefined') {
        // Fallback olarak hard redirect (sadece router yoksa)
        console.warn('Router not available, using hard redirect as fallback');
        window.location.href = '/yonetim';
      }
    }
    
    // CSRF token hatası durumunda yeniden dene
    if (error.response?.status === 403 && 
        error.response?.data?.detail?.includes('CSRF')) {
      try {
        await apiClient.get('/csrf/');
        // Original request'i yeniden dene
        return apiClient.request(error.config);
      } catch (csrfError) {
        console.error('CSRF token yenileme hatası:', csrfError);
      }
    }
    
    return Promise.reject(error);
  }
);

// API endpoint'leri için yardımcı fonksiyonlar
export const api = {
  // Authentication endpoints
  auth: {
    getCSRFToken: () => ensureCSRFToken(),
    
    login: async (credentials: { username: string; password: string }) => {
      return apiCallWithCSRF(async () => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        return await apiClient.post('/rest-auth/login/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      });
    },
    
    register: (userData: { username: string; email: string; password1: string; password2: string }) => {
      const formData = new URLSearchParams();
      formData.append('username', userData.username);
      formData.append('email', userData.email);
      formData.append('password1', userData.password1);
      formData.append('password2', userData.password2);
      return apiClient.post('/rest-auth/registration/', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
    },
    
    logout: () => apiCallWithCSRF(async () => await apiClient.post('/rest-auth/logout/')),
    getUser: () => apiClient.get('/rest-auth/user/'),
  },

  // Profiller endpoints
  profiles: {
    list: () => apiClient.get('/profile/profilleri/'),
    get: (id: number) => apiClient.get(`/profile/profilleri/${id}/`),
    
    create: (data: any) => {
      const formData = new FormData();
      // FormData'ya değerleri ekle
      Object.entries(data).forEach(([key, value]) => {
        // File tipindeki değerleri direkt ekle
        if (value instanceof File) {
          formData.append(key, value);
        }
        // null, undefined veya 'none' değerleri için boş string gönder
        else if (value === null || value === undefined || value === 'none') {
          formData.append(key, '');
        }
        // Diğer tüm değerleri stringe çevir
        else {
          formData.append(key, String(value));
        }
      });
      
      // Debug için FormData içeriğini logla
      console.log('FormData entries:');
      for (const pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
      }
      
      return apiClient.post('/profile/profilleri/', formData);
    },
    
    update: (id: number, data: any) => {
      console.log('🔍 API UPDATE - Input data:', data);
      
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value === null || value === undefined) {
          formData.append(key, 'none');
        } else {
          formData.append(key, value.toString());
        }
      });
      
      // Debug için FormData içeriğini logla
      console.log('🔍 API UPDATE - FormData entries:');
      for (const pair of formData.entries()) {
        console.log(`${pair[0]}: '${pair[1]}'`);
      }
      
      return apiClient.patch(`/profile/profilleri/${id}/`, formData);
    },
    
    delete: (id: number) => apiClient.delete(`/profile/profilleri/${id}/`),
    
    toggleActive: (id: number) => {
      const formData = new FormData();
      formData.append('toggle_active', 'true');
      return apiClient.post(`/profile/profilleri/${id}/toggle_active/`, formData);
    },
  },

  // Robots endpoints (robots app'inizden)
  robots: {
    list: () => apiClient.get('/robots/'),
    get: (id: number) => apiClient.get(`/robots/${id}/`),
    getBySlug: (slug: string) => apiClient.get(`/robots/${slug}/`),
    create: (data: any) => apiClient.post('/robots/', data),
    update: (id: number, data: any) => apiClient.patch(`/robots/${id}/`, data),
    delete: (id: number) => apiClient.delete(`/robots/${id}/`),
    
    // PDF Yükleme
    uploadPdf: (robotId: number, file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      // Gerekirse ek veri de gönderebiliriz, örn: formData.append('pdf_type', 'beyan');
      
      return apiClient.post(`/robots/${robotId}/upload_pdf/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    // PDF Silme
    deletePdf: (pdfId: number) => {
      // RobotPDFViewSet'in standart delete metodunu kullanıyoruz
      return apiClient.delete(`/robot-pdfs/${pdfId}/`);
    },

    // PDF durumunu (aktif/pasif) değiştirme
    togglePdfActive: (pdfId: number) => {
      return apiClient.post(`/robot-pdfs/${pdfId}/toggle_active/`);
    },

    // PDF türünü değiştirme
    changePdfType: (pdfId: number, pdfType: string) => {
      return apiClient.post(`/robot-pdfs/${pdfId}/change_type/`, { pdf_type: pdfType });
    },

    // Robot PDF'lerini listeleme
    listPdfs: (robotId: number) => apiClient.get(`/robots/${robotId}/pdf_dosyalari/`),

    // Sohbet
    chat: (slug: string, message: string, history: any[]) => {
      // ... existing code ...
    },

    // Robot PDF işlemleri
    getPDFs: (robotId: number) => apiClient.get(`/robots/${robotId}/pdf_dosyalari/`),
    getActivePDFs: (robotId: number) => apiClient.get(`/robots/${robotId}/aktif_pdf_dosyalari/`),
  },

  // Robot PDF endpoints
  robotPDFs: {
    list: (robotId?: number, isActive?: boolean, pdfType?: string) => {
      const params = new URLSearchParams();
      if (robotId) params.append('robot_id', robotId.toString());
      if (isActive !== undefined) params.append('is_active', isActive.toString());
      if (pdfType) params.append('pdf_type', pdfType);
      
      const queryString = params.toString();
      return apiClient.get(`/robot-pdfs/${queryString ? '?' + queryString : ''}`);
    },
    
    get: (id: number) => apiClient.get(`/robot-pdfs/${id}/`),
    
    create: (data: FormData) => apiClient.post('/robot-pdfs/', data),
    
    update: (id: number, data: FormData | any) => apiClient.put(`/robot-pdfs/${id}/`, data),
    
    delete: (id: number) => apiClient.delete(`/robot-pdfs/${id}/`),
    
    toggleActive: (id: number) => apiClient.post(`/robot-pdfs/${id}/toggle_active/`),
  },

  // Brand endpoints
  brands: {
    list: () => apiClient.get('/brands/'),
    
    get: (id: number) => apiClient.get(`/brands/${id}/`),
    
    update: (id: number, data: any) => apiClient.patch(`/brands/${id}/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  },

  // Robot Endpoints  
  robotEndpoints: {
    list: '/robots/',
    detail: (id: number) => `/robots/${id}/`,
    bySlug: (slug: string) => `/robots/${slug}/`,
    
    // Robot PDF endpoints
    pdfs: {
      list: '/robot-pdfs/',
      detail: (id: number) => `/robot-pdfs/${id}/`,
      byRobot: (robotId: number) => `/robot-pdfs/?robot_id=${robotId}`,
      active: (robotId: number) => `/robot-pdfs/?robot_id=${robotId}&is_active=true`,
      create: '/robot-pdfs/',
      update: (id: number) => `/robot-pdfs/${id}/`,
      delete: (id: number) => `/robot-pdfs/${id}/`,
      toggleActive: (id: number) => `/robot-pdfs/${id}/toggle_active/`,
    },

    // Robot Chat endpoints
    chat: {
      sidrexgpt: '/robots/sidrexgpt/chat/',
      sidrexgptMag: '/robots/sidrexgpt-mag/chat/',
      sidrexgptKids: '/robots/sidrexgpt-kids/chat/',
      bySlug: (slug: string) => `/robots/${slug}/chat/`,
    }
  },

  // Robot Chat API functions
  chat: {
    // Send chat message to specific robot
    sendMessage: (slug: string, message: string, conversationId?: string) => apiClient.post(`/robots/${slug}/chat/`, {
      message,
      conversation_id: conversationId || `robot_${slug}`
    }),

    // Get robot info for chat
    getRobotInfo: (slug: string) => apiClient.get(`/robots/${slug}/chat/`),
  }
};

export default apiClient; 