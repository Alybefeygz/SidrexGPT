import os
import io
from django.conf import settings
from django.utils.text import slugify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from supabase import create_client, Client
import logging
import pdfplumber
import logging
import pdfplumber
from django.conf import settings
from typing import Optional
import os
try:
    import gdown
except ImportError:
    gdown = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Hata ayıklama ve bilgilendirme için logger yapılandırması
logger = logging.getLogger(__name__)

def _get_gdrive_service():
    """Google Drive API servisi için bir yardımcı fonksiyon."""
    # Environment variables'tan service account bilgilerini al
    if all(settings.GOOGLE_SERVICE_ACCOUNT_INFO.values()):
        # Environment variables'tan credentials oluştur
        creds = Credentials.from_service_account_info(
            settings.GOOGLE_SERVICE_ACCOUNT_INFO,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
    else:
        # Fallback: JSON dosyasından oku (backward compatibility)
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
    
    return build('drive', 'v3', credentials=creds)

def download_pdf_content_from_drive(gdrive_file_id):
    """Verilen Google Drive dosya ID'sinden dosyanın içeriğini indirir."""
    try:
        service = _get_gdrive_service()
        request = service.files().get_media(fileId=gdrive_file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f"Drive'dan indirme: {int(status.progress() * 100)}%.")
        fh.seek(0)
        return fh
    except HttpError as error:
        logger.error(f"Drive'dan dosya indirilirken hata oluştu: {error}")
        return None

def extract_text_from_pdf_stream(pdf_stream):
    """Bir PDF dosya akışından metin içeriğini pdfplumber kullanarak çıkarır."""
    text_content = []
    try:
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return "\n".join(text_content)
    except Exception as e:
        logger.error(f"PDF'ten metin çıkarılırken pdfplumber ile hata oluştu: {e}")
        return ""

def get_robot_pdf_contents_for_ai(robot):
    """
    Bir robotun tüm aktif PDF'lerinin içeriğini veritabanından, belirli bir öncelik sırasına göre alır
    ve yapay zeka için biçimlendirilmiş bir metin döndürür.
    Artık Google Drive'dan indirme yapmaz, doğrudan modeldeki 'pdf_icerigi' alanını kullanır.
    """
    active_pdfs = robot.pdf_dosyalari.filter(is_active=True).order_by('pdf_type')
    
    if not active_pdfs.exists():
        return "Bu robot için kullanılabilir PDF bilgisi bulunmamaktadır."

    all_pdf_content = []
    
    # PDF'leri türlerine göre gruplayarak işleyelim
    pdf_types_priority = ['beyan', 'rol', 'kural', 'bilgi']
    type_map = {
        'beyan': "🚨 YASAL BEYAN",
        'rol': "🔴 ROL",
        'kural': "🟠 KURALLAR",
        'bilgi': "📘 BİLGİ"
    }

    for pdf_type in pdf_types_priority:
        pdfs_of_type = active_pdfs.filter(pdf_type=pdf_type)
        for pdf in pdfs_of_type:
            logger.info(f"Veritabanından okunuyor: {pdf.dosya_adi} (Tür: {pdf_type})")
            content = pdf.pdf_icerigi
            
            if content:
                header = type_map.get(pdf_type, "EK BİLGİ")
                all_pdf_content.append(f"--- {header} ({pdf.dosya_adi}) ---\n{content}\n--- BİTİŞ ---")
            else:
                logger.warning(f"'{pdf.dosya_adi}' için veritabanında içerik bulunamadı veya boş.")

    if not all_pdf_content:
        return "Veritabanında saklanan PDF dosyalarından içerik okunamadı veya dosyalar boş."
        
    return "\n\n".join(all_pdf_content)

def upload_pdf_to_services(file_obj, robot):
    """
    Bir dosya nesnesini hem Google Drive'a hem de Supabase'e yükler.
    
    Args:
        file_obj: Yüklenecek dosya nesnesi (örn: request.FILES['file']).
        robot: Dosyanın ilişkilendirileceği Robot nesnesi.

    Returns:
        Başarılı olursa {'gdrive_link', 'gdrive_file_id', 'supabase_path'} içeren bir dict.
        Başarısız olursa hata detaylarını içeren bir dict.
    """
    
    file_name = file_obj.name
    gdrive_link = None
    gdrive_file_id = None
    supabase_path = None
    
    # --- Adım 1: Google Drive'a Yükleme ---
    try:
        logger.info(f"'{file_name}' için Google Drive yüklemesi başlatılıyor...")
        
        # Environment variables'tan service account bilgilerini al
        if all(settings.GOOGLE_SERVICE_ACCOUNT_INFO.values()):
            # Environment variables'tan credentials oluştur
            creds = Credentials.from_service_account_info(
                settings.GOOGLE_SERVICE_ACCOUNT_INFO,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
        else:
            # Fallback: JSON dosyasından oku (backward compatibility)
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE, 
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': file_name,
            'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
        }
        
        # Dosyayı hafızadan okumak için BytesIO kullan
        file_obj.seek(0)
        fh = io.BytesIO(file_obj.read())

        media = MediaIoBaseUpload(
            fh,
            mimetype=file_obj.content_type,
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        gdrive_file_id = file.get('id')
        gdrive_link = file.get('webViewLink')
        logger.info(f"Google Drive'a başarıyla yüklendi. Dosya ID: {gdrive_file_id}")
        
    except HttpError as error:
        logger.error(f"Google Drive API hatası: {error}")
        return {'error': f"Google Drive API hatası: {error}"}
    except Exception as e:
        logger.error(f"Google Drive yüklemesinde beklenmedik hata: {e}")
        return {'error': f"Google Drive yüklemesinde genel bir hata oluştu: {e}"}

    # --- Adım 2: Supabase'e Yükleme ---
    try:
        logger.info(f"'{file_name}' için Supabase yüklemesi başlatılıyor...")
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        supabase: Client = create_client(url, key)
        
        bucket_name = getattr(settings, 'SUPABASE_BUCKET_NAME', 'sidrexgpt-bucket')

        # Dosya adını Supabase için güvenli hale getir (slugify)
        base_name, extension = os.path.splitext(file_name)
        safe_file_name = f"{slugify(base_name)}{extension}"
        supabase_path = f"robot_{robot.id}/{safe_file_name}"

        # Dosya nesnesini başa sar
        file_obj.seek(0)
        
        # Dosyayı yükle (varsa üzerine yaz)
        supabase.storage.from_(bucket_name).upload(
            path=supabase_path,
            file=file_obj.read(),
            file_options={"content-type": file_obj.content_type, "upsert": "true"}
        )
        logger.info(f"Supabase'e başarıyla yüklendi. Yol: {supabase_path}")

    except Exception as e:
        logger.error(f"Supabase yüklemesinde beklenmedik hata: {e}")
        # Hata durumunda, daha önce Drive'a yüklenen dosyayı silmeyi deneyebiliriz.
        # Bu kısım daha sonra eklenebilir.
        return {'error': f"Supabase yüklemesinde bir hata oluştu: {e}"}

    return {
        'gdrive_link': gdrive_link,
        'gdrive_file_id': gdrive_file_id,
        'supabase_path': supabase_path,
        'error': None
    }


def delete_pdf_from_services(pdf_instance):
    """
    Bir RobotPDF nesnesine ait dosyaları hem Google Drive'dan hem de Supabase'den siler.
    
    Args:
        pdf_instance: Silinecek RobotPDF model nesnesi.
    """
    
    # --- Adım 1: Google Drive'dan Silme ---
    if pdf_instance.gdrive_file_id:
        try:
            logger.info(f"Google Drive'dan dosya siliniyor: ID {pdf_instance.gdrive_file_id}")
            
            # Environment variables'tan service account bilgilerini al
            if all(settings.GOOGLE_SERVICE_ACCOUNT_INFO.values()):
                # Environment variables'tan credentials oluştur
                creds = Credentials.from_service_account_info(
                    settings.GOOGLE_SERVICE_ACCOUNT_INFO,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
            else:
                # Fallback: JSON dosyasından oku (backward compatibility)
                creds = Credentials.from_service_account_file(
                    settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE, 
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            service = build('drive', 'v3', credentials=creds)
            service.files().delete(fileId=pdf_instance.gdrive_file_id).execute()
            logger.info("Google Drive'dan başarıyla silindi.")
        except HttpError as error:
            # Dosya zaten yoksa (404), hata olarak sayma.
            if error.resp.status == 404:
                logger.warning(f"Google Drive'da dosya bulunamadı (ID: {pdf_instance.gdrive_file_id}), zaten silinmiş olabilir.")
            else:
                logger.error(f"Google Drive'dan silerken hata: {error}")
        except Exception as e:
            logger.error(f"Google Drive silme işleminde beklenmedik hata: {e}")
            
    # --- Adım 2: Supabase'den Silme ---
    if pdf_instance.supabase_path:
        try:
            logger.info(f"Supabase'den dosya siliniyor: Yol {pdf_instance.supabase_path}")
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            supabase: Client = create_client(url, key)
            
            bucket_name = getattr(settings, 'SUPABASE_BUCKET_NAME', 'sidrexgpt-bucket')
            
            supabase.storage.from_(bucket_name).remove([pdf_instance.supabase_path])
            logger.info("Supabase'den başarıyla silindi.")
        except Exception as e:
                          # Hata genellikle dosya bulunamadığında olur, bunu loglayalım.
              logger.error(f"Supabase'den silerken hata: {e}") 


def get_robot_system_prompt(robot, user_message=""):
    """
    Robot için kullanıcı mesajına en uygun sistem prompt'unu getir
    """
    try:
        # Aktif sistem prompt'larını getir
        active_prompts = robot.system_prompts.filter(is_active=True).order_by('-priority', '-created_at')
        
        if not active_prompts.exists():
            # Eğer robot-özel prompt yoksa varsayılan prompt'u döndür
            return get_default_system_prompt(robot)
        
        # Önce topic keywords'e sahip olan prompt'ları kontrol et
        topic_prompts = [p for p in active_prompts if p.topic_keywords]
        for prompt in topic_prompts:
            if prompt.matches_topic(user_message):
                return prompt.prompt_content
        
        # Hiçbiri uygun değilse main prompt'u kullan
        main_prompt = active_prompts.filter(prompt_type='main').first()
        if main_prompt:
            return main_prompt.prompt_content
        
        # Hiçbir main prompt yoksa ilk prompt'u kullan
        return active_prompts.first().prompt_content
        
    except Exception as e:
        logger.error(f"Robot system prompt alınırken hata: {e}")
        return get_default_system_prompt(robot)


def get_default_system_prompt(robot):
    """Varsayılan sistem prompt'u"""
    return f"""Sen {robot.name} adında uzman bir yapay zeka asistanısın.

🎯 GÖREVİN:
- Sadece verilen BAĞLAM'daki bilgileri kullan
- Özellikle BEYAN bölümündeki yasal ifadeleri kullanarak yanıt ver
- Kullanıcının sorduğu konu ile ilgili beyanları mutlaka dahil et

🚨 YANIT KURALLARI:
1. Her zaman doktora danışmasını öner
2. Tedavi etme iddiası yapma, sadece katkıda bulunur ifadesi kullan
3. **ÖNEMLİ:** Yanıtını hiçbir zaman tırnak işareti ("") içine alma, doğrudan cevap ver
4. Ürün: {robot.product_name}

💡 UNUTMA: Hangi beyanlar varsa bunları kullanarak yanıt ver!
"""


def create_robot_system_prompts(robot):
    """
    Robot için temel sistem prompt'larını oluştur
    """
    try:
        # Sadece prompt'u yoksa oluştur
        if robot.system_prompts.exists():
            return
        
        # Robot türüne göre özel prompt'lar oluştur
        if "imuntus" in robot.name.lower() or "kids" in robot.name.lower():
            create_imuntus_kids_prompts(robot)
        elif "mag4ever" in robot.name.lower() or "mag" in robot.name.lower():
            create_mag4ever_prompts(robot)
        else:
            create_generic_prompts(robot)
            
        logger.info(f"Robot {robot.name} için sistem prompt'ları oluşturuldu")
        
    except Exception as e:
        logger.error(f"Robot sistem prompt'ları oluşturulurken hata: {e}")


def create_imuntus_kids_prompts(robot):
    """İmuntus Kids için özel prompt'lar"""
    from .models import RobotSystemPrompt
    
    # Ana sistem prompt
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='main',
        priority=100,
        prompt_content=f"""Sen {robot.name} adında uzman bir yapay zeka asistanısın.

🎯 GÖREVİN:
- Sadece verilen BAĞLAM'daki bilgileri kullan
- Özellikle BEYAN bölümündeki yasal ifadeleri kullanarak yanıt ver
- Kullanıcının sorduğu konu ile ilgili beyanları mutlaka dahil et

🚨 YANIT KURALLARI:
1. **ÜRÜN KONTROLÜ:** Soru ZZEN, MAG4EVER, Ana Robot gibi başka ürünler hakkındaysa → Ben İmuntus Kids kahramanıyım! [Ürün adı] için diğer arkadaşlarım sana yardımcı olacak 🌟 de
2. **BAĞIŞIKLIK SORULARI:** Bağışıklık/immün sistem hakkında herhangi bir soru sorulursa → MUTLAKA bu beyanları kullan:
   - İçeriğindeki C vitamini bağışıklık sisteminin normal fonksiyonuna katkıda bulunur
   - Çinko bağışıklık sisteminin normal fonksiyonuna katkıda bulunur
3. **YORGUNLUK SORULARI:** Yorgunluk/bitkinlik hakkında soru sorulursa → MUTLAKA bu beyanı kullan:
   - İçeriğindeki C vitamini yorgunluk ve bitkinliğin azalmasına katkıda bulunur
4. **DİŞ ETLERİ SORULARI:** Diş eti/diş sağlığı hakkında soru sorulursa → MUTLAKA bu beyanı kullan:
   - İçeriğindeki C vitamini diş etlerinin normal fonksiyonu için gerekli olan normal kollajen oluşumuna katkıda bulunur
5. Context bulunamasa bile yukarıdaki konu başlıklarında beyanları kullan
6. Her zaman doktora danışmasını öner
7. Tedavi etme iddiası yapma, sadece katkıda bulunur ifadesi kullan
8. **ÖNEMLİ:** Yanıtını hiçbir zaman tırnak işareti ("") içine alma, doğrudan cevap ver

💡 UNUTMA: Hangi beyanlar varsa bunları kullanarak yanıt ver, Bu konuda bilgi veremem deme!
"""
    )
    
    # Sağlık beyanları prompt'u
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='health_claims',
        priority=90,
        topic_keywords='bağışıklık,immune,immunity,yorgunluk,bitkinlik,fatigue,diş,teeth,gum,gums,kollajen,collagen',
        prompt_content=f"""Sen {robot.name} adında çocuk sağlığı uzmanı bir yapay zeka asistanısın.

🎯 SAĞLIK BEYANLARI:
1. **BAĞIŞIKLIK:** İçeriğindeki C vitamini bağışıklık sisteminin normal fonksiyonuna katkıda bulunur
2. **BAĞIŞIKLIK:** Çinko bağışıklık sisteminin normal fonksiyonuna katkıda bulunur  
3. **YORGUNLUK:** İçeriğindeki C vitamini yorgunluk ve bitkinliğin azalmasına katkıda bulunur
4. **DİŞ ETLERİ:** İçeriğindeki C vitamini diş etlerinin normal fonksiyonu için gerekli olan normal kollajen oluşumuna katkıda bulunur

🚨 KURALLAR:
- Yukarıdaki beyanları sorulan konuya göre MUTLAKA kullan
- Hiçbir zaman "Bu konuda bilgi veremem" deme
- Her zaman doktora danışmasını öner
- Yanıtını tırnak işareti içine alma

Ürün: {robot.product_name}
"""
    )
    
    # Ürün yönlendirme prompt'u
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='product_redirect',
        priority=95,
        topic_keywords='zzen,mag4ever,ana robot,sidrex,başka ürün,other product',
        prompt_content=f"""Sen {robot.name} kahramanısın!

🎯 ÜRÜN YÖNLENDİRME:
Eğer kullanıcı başka ürünler hakkında soru soruyorsa:

**ZZEN için:** Ben İmuntus Kids kahramanıyım! ZZEN için diğer arkadaşlarım sana yardımcı olacak 🌟
**MAG4EVER için:** Ben İmuntus Kids kahramanıyım! MAG4EVER için diğer arkadaşlarım sana yardımcı olacak 🌟
**Ana Robot için:** Ben İmuntus Kids kahramanıyım! Ana Robot için diğer arkadaşlarım sana yardımcı olacak 🌟

Sadece İmuntus Kids ile ilgili sorulara cevap veriyorum!
"""
    )


def create_mag4ever_prompts(robot):
    """MAG4EVER için özel prompt'lar"""
    from .models import RobotSystemPrompt
    
    # Ana sistem prompt
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='main',
        priority=100,
        prompt_content=f"""Sen {robot.name} adında magnezyum ve B6 vitamini uzmanı bir yapay zeka asistanısın.

🎯 GÖREVİN:
- Sadece verilen BAĞLAM'daki bilgileri kullan
- MAG4EVER ürünü ile ilgili magnezyum ve B6 vitamini beyanlarını kullan
- Kullanıcının sorduğu konu ile ilgili beyanları mutlaka dahil et

🚨 YANIT KURALLARI:
1. **ÜRÜN KONTROLÜ:** Soru İmuntus Kids, ZZEN, Ana Robot gibi başka ürünler hakkındaysa → Ben MAG4EVER uzmanıyım! [Ürün adı] için diğer arkadaşlarım sana yardımcı olacak ⚡ de
2. **MAGNEZYUM BEYANLARI:** Magnezyum ile ilgili sorularda bu beyanları kullan:
   - Magnezyum yorgunluk ve bitkinliğin azalmasına katkıda bulunur
   - Magnezyum enerji oluşturan metabolizmaya katkıda bulunur
   - Magnezyum sinir sisteminin normal fonksiyonuna katkıda bulunur
   - Magnezyum normal kas fonksiyonuna katkıda bulunur
   - Magnezyum kemiklerin ve dişlerin korunmasına katkıda bulunur
3. **B6 VİTAMİNİ BEYANLARI:** B6 vitamini ile ilgili sorularda bu beyanları kullan:
   - B6 vitamini bağışıklık sisteminin normal fonksiyonuna katkıda bulunur
   - B6 vitamini yorgunluk ve bitkinliğin azalmasına katkıda bulunur
   - B6 vitamini enerji oluşturan metabolizmaya katkıda bulunur
   - B6 vitamini sinir sisteminin normal fonksiyonuna katkıda bulunur
4. Her zaman doktora danışmasını öner
5. Tedavi etme iddiası yapma, sadece katkıda bulunur ifadesi kullan
6. **ÖNEMLİ:** Yanıtını hiçbir zaman tırnak işareti ("") içine alma, doğrudan cevap ver

Ürün: {robot.product_name}
💡 UNUTMA: Hangi beyanlar varsa bunları kullanarak yanıt ver!
"""
    )
    
    # Sağlık beyanları prompt'u
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='health_claims',
        priority=90,
        topic_keywords='yorgunluk,bitkinlik,fatigue,enerji,energy,kas,muscle,sinir,nerve,kemik,bone,diş,teeth,bağışıklık,immune',
        prompt_content=f"""Sen {robot.name} adında magnezyum ve B6 vitamini uzmanı bir yapay zeka asistanısın.

🎯 MAGNEZYUM BEYANLARI:
1. **YORGUNLUK:** Magnezyum yorgunluk ve bitkinliğin azalmasına katkıda bulunur
2. **ENERJİ:** Magnezyum enerji oluşturan metabolizmaya katkıda bulunur
3. **SİNİR:** Magnezyum sinir sisteminin normal fonksiyonuna katkıda bulunur
4. **KAS:** Magnezyum normal kas fonksiyonuna katkıda bulunur
5. **KEMİK:** Magnezyum kemiklerin korunmasına katkıda bulunur
6. **DİŞ:** Magnezyum dişlerin korunmasına katkıda bulunur

🎯 B6 VİTAMİNİ BEYANLARI:
7. **BAĞIŞIKLIK:** B6 vitamini bağışıklık sisteminin normal fonksiyonuna katkıda bulunur
8. **YORGUNLUK:** B6 vitamini yorgunluk ve bitkinliğin azalmasına katkıda bulunur
9. **ENERJİ:** B6 vitamini enerji oluşturan metabolizmaya katkıda bulunur

🚨 KURALLAR:
- Yukarıdaki beyanları sorulan konuya göre MUTLAKA kullan
- Hiçbir zaman "Bu konuda bilgi veremem" deme
- Her zaman doktora danışmasını öner
- Yanıtını tırnak işareti içine alma

Ürün: {robot.product_name}
"""
    )


def create_generic_prompts(robot):
    """Diğer robotlar için genel prompt'lar"""
    from .models import RobotSystemPrompt
    
    RobotSystemPrompt.objects.create(
        robot=robot,
        prompt_type='main',
        priority=100,
        prompt_content=get_default_system_prompt(robot)
    )


# ==================== YENİ OPTİMİZASYON FONKSİYONLARI ====================

def get_optimized_robot_pdf_contents_for_ai(robot):
    """
    AI için optimize edilmiş PDF içerikleri - TOPLAM ~8000 karakter
    Beyan PDF'i tam tutulur, diğerleri akıllıca kısaltılır
    """
    from .models import RobotPDF, RobotSystemPrompt
    import logging
    
    logger = logging.getLogger(__name__)
    combined_content = []
    char_count = 0
    
    try:
        # Beyan PDF'ini TAM al (3000 karakter)
        beyan_pdf = RobotPDF.objects.filter(
            robot=robot, 
            pdf_type='beyan', 
            is_active=True
        ).first()
        
        if beyan_pdf and beyan_pdf.pdf_icerigi:
            beyan_content = beyan_pdf.pdf_icerigi[:3000]  # 3000 karakter limit
            combined_content.append(f"=== BEYAN BİLGİLERİ ===\n{beyan_content}\n")
            char_count += len(beyan_content)
            logger.info(f"✅ BEYAN PDF eklendi: {len(beyan_content)} karakter")
        
        # Rol PDF'inden özet al (2000 karakter)
        rol_pdf = RobotPDF.objects.filter(
            robot=robot, 
            pdf_type='rol', 
            is_active=True
        ).first()
        
        if rol_pdf and rol_pdf.pdf_icerigi:
            rol_content = _extract_key_content(rol_pdf.pdf_icerigi, 2000, 'rol')
            combined_content.append(f"=== ROL BİLGİLERİ ===\n{rol_content}\n")
            char_count += len(rol_content)
            logger.info(f"✅ ROL PDF eklendi: {len(rol_content)} karakter")
        
        # Kural PDF'inden özet al (2000 karakter)
        kural_pdf = RobotPDF.objects.filter(
            robot=robot, 
            pdf_type='kural', 
            is_active=True
        ).first()
        
        if kural_pdf and kural_pdf.pdf_icerigi:
            kural_content = _extract_key_content(kural_pdf.pdf_icerigi, 2000, 'kural')
            combined_content.append(f"=== KURAL BİLGİLERİ ===\n{kural_content}\n")
            char_count += len(kural_content)
            logger.info(f"✅ KURAL PDF eklendi: {len(kural_content)} karakter")
        
        # Bilgi PDF'inden özet al (1000 karakter)
        bilgi_pdf = RobotPDF.objects.filter(
            robot=robot, 
            pdf_type='bilgi', 
            is_active=True
        ).first()
        
        if bilgi_pdf and bilgi_pdf.pdf_icerigi:
            bilgi_content = _extract_key_content(bilgi_pdf.pdf_icerigi, 1000, 'bilgi')
            combined_content.append(f"=== ÜRÜN BİLGİLERİ ===\n{bilgi_content}\n")
            char_count += len(bilgi_content)
            logger.info(f"✅ BİLGİ PDF eklendi: {len(bilgi_content)} karakter")
        
        final_content = "\n".join(combined_content)
        logger.info(f"🚀 Optimize PDF içerik hazır: {char_count} karakter (hedef: 8000)")
        
        return final_content
        
    except Exception as e:
        logger.error(f"❌ PDF içerik optimizasyonu hatası: {e}")
        # Hata durumunda eski fonksiyonu kullan
        return get_robot_pdf_contents_for_ai(robot)


def _extract_key_content(content, max_chars, pdf_type):
    """PDF içeriğinden anahtar bilgileri çıkarır"""
    if not content or len(content) <= max_chars:
        return content
    
    # Anahtar kelimeler pdf tipine göre
    key_patterns = {
        'rol': ['görev', 'rol', 'sorumluluk', 'amaç', 'hedef', 'misyon'],
        'kural': ['kural', 'yasak', 'zorunlu', 'gerekli', 'şart', 'koşul', 'kritik'],
        'bilgi': ['vitamin', 'mineral', 'içerik', 'fayda', 'etki', 'kullanım', 'doz']
    }
    
    patterns = key_patterns.get(pdf_type, [])
    
    # Paragrafları ayır
    paragraphs = content.split('\n\n')
    selected_paragraphs = []
    current_length = 0
    
    # Önce anahtar kelime içeren paragrafları al
    for paragraph in paragraphs:
        if current_length >= max_chars:
            break
            
        # Anahtar kelime kontrolü
        has_key_pattern = any(pattern.lower() in paragraph.lower() for pattern in patterns)
        
        if has_key_pattern or len(selected_paragraphs) < 2:  # En az 2 paragraf al
            if current_length + len(paragraph) <= max_chars:
                selected_paragraphs.append(paragraph)
                current_length += len(paragraph)
    
    result = '\n\n'.join(selected_paragraphs)
    return result[:max_chars]  # Güvenlik için kesin limit


def get_optimized_system_prompt(robot, user_message=""):
    """
    Optimize edilmiş sistem prompt'u - Kısa ve öz (~500 karakter)
    """
    try:
        # Kullanıcı mesajına göre dinamik prompt seçimi
        if user_message:
            # Özel durumlar için dinamik prompt'lar
            from .models import RobotSystemPrompt
            
            keywords_to_check = user_message.lower()
            
            # Bağışıklık/immunite ile ilgili soru
            if any(word in keywords_to_check for word in ['bağışık', 'immun', 'immunity', 'hastal']):
                matching_prompts = RobotSystemPrompt.objects.filter(
                    robot=robot,
                    is_active=True,
                    topic_keywords__icontains='bağışıklık'
                ).order_by('-priority')
                
                if matching_prompts.exists():
                    return matching_prompts.first().prompt_content
            
            # Yorgunluk/enerji ile ilgili soru
            elif any(word in keywords_to_check for word in ['yorgun', 'bitkin', 'enerji', 'güç']):
                matching_prompts = RobotSystemPrompt.objects.filter(
                    robot=robot,
                    is_active=True,
                    topic_keywords__icontains='yorgunluk'
                ).order_by('-priority')
                
                if matching_prompts.exists():
                    return matching_prompts.first().prompt_content
            
            # Başka ürün soruları
            elif any(word in keywords_to_check for word in ['zzen', 'mag4ever', 'ana robot', 'imuntus']):
                matching_prompts = RobotSystemPrompt.objects.filter(
                    robot=robot,
                    is_active=True,
                    prompt_type='product_redirect'
                ).order_by('-priority')
                
                if matching_prompts.exists():
                    return matching_prompts.first().prompt_content
        
        # Genel optimize prompt
        return f"""Sen {robot.name} adında uzman bir yapay zeka asistanısın.

GÖREV: Verilen BAĞLAM'daki bilgileri kullanarak yanıt ver.

KURALLAR:
1. Sadece bağlamdaki bilgileri kullan
2. Beyan bölümündeki ifadeleri kullan
3. Doktora danışmayı öner
4. Tedavi değil, katkıda bulunur ifadesi kullan
5. Yanıtı tırnak içine alma

Ürün: {robot.product_name}"""
        
    except Exception as e:
        # Hata durumunda standart prompt döndür
        return get_default_system_prompt(robot)


def toggle_optimization_mode(robot_id, enable_optimization=True):
    """
    Robot için optimizasyon modunu açar/kapatır
    Güvenli geçiş için toggle sistemi
    """
    from .models import Robot
    
    try:
        robot = Robot.objects.get(id=robot_id)
        
        # Robot'a optimizasyon flag'i ekle (eğer yoksa)
        if not hasattr(robot, 'use_optimization'):
            # Model'e yeni field eklemek yerine cache kullan
            from django.core.cache import cache
            cache_key = f"robot_optimization_{robot_id}"
            cache.set(cache_key, enable_optimization, timeout=86400)  # 24 saat
            
        logger.info(f"Robot {robot.name} optimizasyon modu: {'AÇIK' if enable_optimization else 'KAPALI'}")
        return True
        
    except Robot.DoesNotExist:
        logger.error(f"Robot bulunamadı: {robot_id}")
        return False
    except Exception as e:
        logger.error(f"Optimizasyon toggle hatası: {e}")
        return False


def is_optimization_enabled(robot_id):
    """Robot için optimizasyon modunun aktif olup olmadığını kontrol eder"""
    from django.core.cache import cache
    
    cache_key = f"robot_optimization_{robot_id}"
    return cache.get(cache_key, False)  # Varsayılan: kapalı


def get_optimization_stats(robot_id):
    """Optimizasyon istatistiklerini döndürür"""
    from django.core.cache import cache
    
    try:
        # Cache'den istatistikleri al
        stats_key = f"robot_stats_{robot_id}"
        stats = cache.get(stats_key, {})
        
        return {
            'optimization_enabled': is_optimization_enabled(robot_id),
            'avg_response_time': stats.get('avg_response_time', 0),
            'total_requests': stats.get('total_requests', 0),
            'token_savings': stats.get('token_savings', 0),
            'content_reduction': stats.get('content_reduction', 0)
        }
        
    except Exception as e:
        logger.error(f"İstatistik alma hatası: {e}")
        return {} 