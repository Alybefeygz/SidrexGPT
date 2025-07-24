"""
Widget Loader Views - MarkaMind Widget System
Bu dosya mevcut sistemi bozmadan yeni widget özelliklerini ekler.
"""
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json


@method_decorator(csrf_exempt, name='dispatch')
class WidgetLoaderView(View):
    """
    Widget loader JavaScript dosyasını dinamik olarak üretir
    Orbina benzeri script sistemi için
    """
    
    def get(self, request):
        # Widget ID parametresini al (isteğe bağlı)
        widget_id = request.GET.get('id', 'default')
        
        # JavaScript içeriğini oluştur
        js_content = self.generate_widget_script(widget_id)
        
        # Response headers - Cache'i devre dışı bırak (development için)
        response = HttpResponse(js_content, content_type='application/javascript')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Cache yok
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        
        return response
    
    def generate_widget_script(self, widget_id):
        """Widget JavaScript kodunu üret"""
        
        # Mevcut domain'i al
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        base_url = f"{protocol}://{domain}"
        
        # F-string kullanarak daha güvenli format
        js_template = f"""
(function() {{
  "use strict";
  
  // MarkaMind Smart Widget Script
  // Version: 2.0.0 - URL Based Robot Selection
  
  function initMarkaMindWidget(config) {{
    // Configuration defaults
    const defaults = {{
      robotId: "auto", // "auto" = URL'ye göre otomatik seç
      brandId: "sidrex", 
      position: "right",
      width: "250px",
      height: "250px",
      right: "20px",
      left: "20px",
      bottom: "20px",
      mobileRight: "10px",
      mobileLeft: "10px",
      borderRadius: "0px",
      zIndex: 99999,
      backgroundColor: "transparent",
      mode: "embed"
    }};
    
    const settings = Object.assign({{}}, defaults, config);
    
    // Frontend URL (embed sayfaları frontend'de)
    const backendUrl = "{base_url}";
    const frontendUrl = "http://localhost:3000";  // Frontend URL'i
    
    // URL bazlı robot seçimi
    function selectRobotByUrl() {{
      const currentUrl = window.location.href.toLowerCase();
      
      console.log("🔍 MarkaMind Widget Debug - Current URL:", currentUrl);
      
      // URL mapping'i
      if (currentUrl.includes('imuntus-kids') || currentUrl.includes('cocuklar-icin')) {{
        console.log("✅ MarkaMind Widget - Third Robot seçildi (Kids URL)");
        return 'third-robot'; // Kids product için third robot
      }} else if (currentUrl.includes('mag4ever')) {{
        console.log("✅ MarkaMind Widget - Second Robot seçildi (Mag4ever URL)");
        return 'second-robot'; // Mag4ever için second robot  
      }}
      
      console.log("❌ MarkaMind Widget - Hiçbir robot URL'si eşleşmedi");
      // Varsayılan: robot gösterme
      return null;
    }}
    
    // Robot ID belirle
    let robotId;
    if (settings.robotId === "auto") {{
      robotId = selectRobotByUrl();
      if (!robotId) {{
        console.log("MarkaMind Widget: Bu sayfa için robot tanımlanmamış, widget yüklenmeyecek");
        return; // Widget yükleme
      }}
    }} else {{
      robotId = settings.robotId;
    }}
    
    // Robot ID kontrolü
    if (!robotId) {{
      console.error("MarkaMind Widget: robotId belirlenemedi");
      return;
    }}
    
    console.log(`MarkaMind Widget: ${{robotId}} yükleniyor için ${{window.location.href}}`);
    
    // Settings'i güncelle
    settings.robotId = robotId;
    
    // Dil tespiti
    const userLang = navigator.language.toLowerCase();
    const langCode = userLang.startsWith("en") ? "en" : "tr";
    
    // Iframe oluştur (Frontend'den embed sayfasını yükle)
    const iframe = document.createElement("iframe");
    iframe.id = "markamind-widget-iframe";
    iframe.src = `${{frontendUrl}}/embed/${{robotId}}`;
    
    // Position ayarları
    const positionStyles = settings.position === "left" 
      ? `left: ${{settings.left}};`
      : `right: ${{settings.right}};`;
    
    iframe.style.cssText = `
      position: fixed;
      color-scheme: normal;
      width: ${{settings.width}};
      height: ${{settings.height}};
      ${{positionStyles}}
      bottom: ${{settings.bottom}};
      border: none;
      z-index: ${{settings.zIndex}};
      border-radius: ${{settings.borderRadius}};
      background-color: transparent;
      opacity: 0;
      transition: opacity 0.5s ease-in-out;
    `;
    
    // DOM'a ekle ama gizli
    document.body.appendChild(iframe);
    
    // 2 saniye gecikme ile iframe'i göster
    setTimeout(function() {{
      iframe.style.opacity = "1";
      console.log("🎬 Widget iframe shown after 2 second delay");
    }}, 2000);
    
    // Iframe yüklenme listener - state senkronizasyonu için
    iframe.addEventListener('load', function() {{
      console.log("🔄 Iframe loaded, checking for state sync...");
      
      // localStorage'dan mevcut state'i kontrol et ve iframe'e gönder
      setTimeout(function() {{
        const currentState = localStorage.getItem('markamind-chat-state');
        if (currentState === 'open') {{
          console.log("🔄 Found open state in localStorage, syncing with iframe...");
          iframe.contentWindow.postMessage('forceOpenChatbox', '*');
        }}
      }}, 500);
    }});
    
    // Mobil tespit fonksiyonu
    function isMobileDevice() {{
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
             ("ontouchstart" in window) ||
             (navigator.maxTouchPoints > 0);
    }}

    // Mobile detection for widget (Orbina style)
    function isMobileDevice() {{
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
             ("ontouchstart" in window) ||
             (navigator.maxTouchPoints > 0);
    }}

    // Calculate safe viewport height for mobile (Orbina style)
    function getSafeViewportHeight() {{
      if (typeof window !== "undefined") {{
        return window.innerHeight + "px";
      }}
      return "100vh";
    }}

    // Update viewport height when orientation changes
    function updateViewportHeight() {{
      if (isMobileDevice()) {{
        document.documentElement.style.setProperty("--vh", (window.innerHeight * 0.01) + "px");
      }}
    }}

    // Set initial viewport height
    updateViewportHeight();
    
    // Update on resize and orientation change
    window.addEventListener("resize", updateViewportHeight);
    window.addEventListener("orientationchange", function() {{
      setTimeout(updateViewportHeight, 100);
    }});

    // Overlay functions - Orbina style
    function createChatOverlay() {{
      const overlay = document.createElement('div');
      overlay.id = 'markamind-chat-overlay';
      overlay.style.cssText = `
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.3);
        z-index: 99998;
        pointer-events: auto;
        backdrop-filter: blur(2px);
        transition: opacity 0.3s ease;
      `;
      
      // Overlay'e tıklanınca chatbox'ı kapat
      overlay.addEventListener('click', function() {{
        const iframe = document.getElementById('markamind-widget-iframe');
        if (iframe && iframe.contentWindow) {{
          iframe.contentWindow.postMessage('closeChat', '*');
        }}
      }});
      
      document.body.appendChild(overlay);
      console.log("✨ Chat overlay created");
    }}
    
    function removeChatOverlay() {{
      const overlay = document.getElementById('markamind-chat-overlay');
      if (overlay) {{
        overlay.remove();
        console.log("✨ Chat overlay removed");
      }}
    }}
    
    function disableSiteElements() {{
      document.querySelectorAll('a, button, input, select, textarea').forEach(function(el) {{
        if (el.id !== 'markamind-widget-iframe') {{
          el.style.pointerEvents = 'none';
          el.classList.add('markamind-disabled');
        }}
      }});
      console.log("🔒 Site elements disabled");
    }}
    
    function enableSiteElements() {{
      document.querySelectorAll('.markamind-disabled').forEach(function(el) {{
        el.style.pointerEvents = 'auto';
        el.classList.remove('markamind-disabled');
      }});
      console.log("🔓 Site elements enabled");
    }}

    // PostMessage listener - Orbina style basitleştirilmiş sistem
    window.addEventListener("message", function(event) {{
      const iframe = document.getElementById("markamind-widget-iframe");
      
      // Debug log
      console.log("PostMessage received:", event.data, "from origin:", event.origin);
      
      if (iframe) {{
        // Chatbox açıldı - Orbina style + Overlay + State sync
        if (event.data === "openChatbox") {{
          console.log("🤖 Opening chatbox - enlarging iframe");
          
          // Overlay ve site element disable
          createChatOverlay();
          disableSiteElements();
          
          if (isMobileDevice()) {{
            // Mobile: Full screen with dynamic height
            const safeHeight = getSafeViewportHeight();
            iframe.style.width = "100vw";
            iframe.style.height = safeHeight;
            iframe.style.top = "0";
            iframe.style.left = "0";
            iframe.style.right = "unset";
            iframe.style.bottom = "unset";
            iframe.style.borderRadius = "0";
            iframe.style.position = "fixed";
            iframe.style.zIndex = "999999";
            iframe.style.maxHeight = "none";
            iframe.style.minHeight = safeHeight;
          }} else {{
            // Desktop: Normal messenger
            iframe.style.width = "800px";
            iframe.style.maxWidth = "100vw";
            iframe.style.height = "650px";
            iframe.style.maxHeight = "800px";
            iframe.style.borderRadius = "0px";
            iframe.style.zIndex = "999999";
            
            // Position ayarı
            if (settings.position === "left") {{
              iframe.style.left = settings.left;
              iframe.style.right = "unset";
            }} else {{
              iframe.style.right = settings.right;
              iframe.style.left = "unset";
            }}
          }}
          
          // State senkronizasyonu - iframe resize sonrası chatbox'ın açık kalması için
          setTimeout(function() {{
            iframe.contentWindow.postMessage('forceOpenChatbox', '*');
            console.log("🔄 Sent forceOpenChatbox to iframe for state sync");
          }}, 300);
          
          console.log("✅ Iframe enlarged to:", iframe.getBoundingClientRect().width, "x", iframe.getBoundingClientRect().height);
        }}
        
        // Chatbox kapandı - Orbina style + Overlay cleanup + State sync
        else if (event.data === "closeChatbox") {{
          console.log("❌ Closing chatbox - shrinking iframe");
          
          // Overlay kaldır ve site elementleri aktif et
          removeChatOverlay();
          enableSiteElements();
          
          // Orijinal boyutlara dön
          iframe.style.width = settings.width;
          iframe.style.height = settings.height;
          iframe.style.borderRadius = settings.borderRadius;
          iframe.style.top = "unset";
          iframe.style.left = settings.position === "left" ? settings.left : "unset";
          iframe.style.right = settings.position === "right" ? settings.right : "unset";
          iframe.style.bottom = settings.bottom;
          iframe.style.position = "fixed";
          iframe.style.zIndex = settings.zIndex;
          iframe.style.maxHeight = "none";
          iframe.style.minHeight = "unset";
          
          // State senkronizasyonu - iframe resize sonrası chatbox'ın kapalı kalması için
          setTimeout(function() {{
            iframe.contentWindow.postMessage('forceCloseChatbox', '*');
            console.log("🔄 Sent forceCloseChatbox to iframe for state sync");
          }}, 300);
          
          console.log("✅ Iframe shrunk to:", iframe.getBoundingClientRect().width, "x", iframe.getBoundingClientRect().height);
        }}
      }}
    }});
    
    // Mobil responsive handling
    const mobileMediaQuery = window.matchMedia("(max-width: 768px)");
    
    function handleMobileChange(e) {{
      const iframe = document.getElementById("markamind-widget-iframe");
      if (iframe) {{
        if (settings.position === "left") {{
          iframe.style.left = e.matches ? settings.mobileLeft : settings.left;
        }} else {{
          iframe.style.right = e.matches ? settings.mobileRight : settings.right;
        }}
      }}
    }}
    
    handleMobileChange(mobileMediaQuery);
    mobileMediaQuery.addListener(handleMobileChange);
    
    console.log("MarkaMind Widget initialized successfully!");
  }}
  
  // Otomatik başlatma
  if (typeof window.MarkaMindConfig !== "undefined") {{
    if (document.readyState === "loading") {{
      document.addEventListener("DOMContentLoaded", function() {{
        initMarkaMindWidget(window.MarkaMindConfig);
      }});
    }} else {{
      initMarkaMindWidget(window.MarkaMindConfig);
    }}
  }}
  
  // Global fonksiyon olarak expose et
  window.MarkaMindWidget = {{
    init: initMarkaMindWidget
  }};
  
}})();
"""
        
        return js_template


class WidgetConfigView(View):
    """
    Widget konfigürasyon bilgilerini döner
    Debug ve test amaçlı
    """
    
    def get(self, request):
        config = {
            'available_robots': ['first-robot', 'second-robot', 'third-robot'],
            'available_positions': ['left', 'right'],
            'default_config': {
                'robotId': 'first-robot',
                'position': 'right',
                'width': '60px',
                'height': '60px'
            },
            'version': '1.0.0'
        }
        
        return JsonResponse(config)