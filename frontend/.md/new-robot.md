 🔧 ADIM 1: Backend - Veritabanına Robot Modeli Ekleme

  🎯 Prompt:
  "Backend'de yeni bir robot modeli oluştur. Django admin panelinden veya Django shell'den Robot.objects.create() kullanarak yeni robot ekle. Robot ismi 'Dördüncü Robot',
   ürün ismi 'Test Ürün', Sidrex markasına bağla."

  📁 Etkilenen Dosyalar:
  - backend/robots/models.py (mevcut model kullanılacak)
  - Veritabanı (yeni kayıt eklenecek)

  ---
  🔧 ADIM 2: Backend - Robot PDF'lerini Ekleme

  🎯 Prompt:
  "Oluşturulan robot için gerekli PDF dosyalarını RobotPDF modeli üzerinden ekle. 4 tip PDF gerekli: Beyan (pdf_type='beyan'), Rol (pdf_type='rol'), Kural
  (pdf_type='kural'), Bilgi (pdf_type='bilgi'). Her PDF'i Google Drive'a yükleyip URL'lerini veritabanına kaydet."

  📁 Etkilenen Dosyalar:
  - backend/robots/models.py (RobotPDF modeli)
  - Veritabanı (RobotPDF kayıtları)

  ---
  🔧 ADIM 3: Backend - Slug Sistemi Güncelleme

  🎯 Prompt:
  "Robot'un URL slug sistemini güncelle. models.py'deki get_slug() metodunu ve api/urls.py'deki create_robot_slug() fonksiyonunu dördüncü robot için özel slug
  'dorduncu-robot' döndürecek şekilde güncelle."

  📁 Etkilenen Dosyalar:
  - backend/robots/models.py (get_slug metodu)
  - backend/robots/api/urls.py (create_robot_slug fonksiyonu)

  ---
  🔧 ADIM 4: Backend - API Endpoint Test

  🎯 Prompt:
  "API endpoint'lerini test et. /api/robots/dorduncu-robot/ ve /api/robots/dorduncu-robot/chat/ endpoint'lerinin çalıştığını doğrula. Postman veya curl ile GET ve POST   
  istekleri gönder."

  📁 Etkilenen Dosyalar:
  - backend/robots/api/urls.py (test için)
  - backend/robots/api/views.py (test için)

  ---
  🎨 ADIM 5: Frontend - Robot Bileşen Dosyaları Oluşturma

  🎯 Prompt:
  "Frontend'de dördüncü robot için yeni React bileşenleri oluştur. components/robots/fourth-robot/ klasöründe FourthRobot.tsx (ana robot bileşeni) ve
  FourthRobotChatBox.tsx (chat kutusu) dosyalarını oluştur. Mevcut robot bileşenlerini (FirstRobot, SecondRobot, ThirdRobot) referans al."

  📁 Etkilenen Dosyalar:
  - frontend/components/robots/fourth-robot/FourthRobot.tsx (yeni)
  - frontend/components/robots/fourth-robot/FourthRobotChatBox.tsx (yeni)

  ---
  🎨 ADIM 6: Frontend - CSS Tasarım Stilleri

  🎯 Prompt:
  "app/globals.css dosyasına dördüncü robot için CSS stilleri ekle. .robot-head-fourth, .robot-antenna-fourth, .robot-ear-fourth, .robot-face-fourth sınıflarını tanımla. 
  Mevcut robot stillerini (first, second, third) örnek al ve farklı bir renk paleti kullan."

  📁 Etkilenen Dosyalar:
  - frontend/app/globals.css (güncelleme)

  ---
  🎨 ADIM 7: Frontend - Robot Görselleri

  🎯 Prompt:
  "public/images/ klasörüne dördüncü robot için görsel dosyaları ekle: antenna-fourth.png, fourth-robot-eyes.png, fourth-robot-mouth.png. Mevcut robot görsellerini       
  referans alarak yeni tasarım oluştur veya düzenle."

  📁 Etkilenen Dosyalar:
  - frontend/public/images/antenna-fourth.png (yeni)
  - frontend/public/images/fourth-robot-eyes.png (yeni)
  - frontend/public/images/fourth-robot-mouth.png (yeni)

  ---
  🎨 ADIM 8: Frontend - Ana Robot Yöneticisi Güncelleme

  🎯 Prompt:
  "components/robots/RobotManager.tsx dosyasını güncelle. FourthRobot bileşenini import et, robots state array'ine ekle ve onChatToggle mantığına dördüncü robot için     
  'fourth' ID'si ile gerekli kodları ekle."

  📁 Etkilenen Dosyalar:
  - frontend/components/robots/RobotManager.tsx (güncelleme)

  ---
  🎨 ADIM 9: Frontend - Sayfa Entegrasyonu

  🎯 Prompt:
  "Dördüncü robot için sayfa dosyaları oluştur: app/sidrexgpt/dorduncu-robot/page.tsx, app/embed/fourth-robot/page.tsx, app/iframe/fourth-robot/page.tsx. Mevcut robot    
  sayfalarını template olarak kullan ve dördüncü robot için uyarla."

  📁 Etkilenen Dosyalar:
  - frontend/app/sidrexgpt/dorduncu-robot/page.tsx (yeni)
  - frontend/app/embed/fourth-robot/page.tsx (yeni)
  - frontend/app/iframe/fourth-robot/page.tsx (yeni)

  ---
  🎨 ADIM 10: Frontend - API Bağlantısı

  🎯 Prompt:
  "hooks/use-api.ts dosyasını güncelle. useRobotChat hook'una 'dorduncu-robot' slug'ı için case ekle ve backend API endpoint'i ile bağlantıyı sağla. Mevcut robot
  slug'larını (ana-robot, sidrexgpt-mag, sidrexgpt-kids) referans al."

  📁 Etkilenen Dosyalar:
  - frontend/hooks/use-api.ts (güncelleme)
