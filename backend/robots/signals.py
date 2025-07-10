from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import RobotPDF
from .services import delete_pdf_from_services
from .rag_services import RAGService
import logging

logger = logging.getLogger(__name__)

@receiver(post_delete, sender=RobotPDF)
def delete_files_on_pdf_delete(sender, instance, **kwargs):
    """
    Bir RobotPDF nesnesi veritabanından silindikten sonra,
    ilişkili dosyaları Google Drive ve Supabase'den siler.
    Ayrıca RAG sistemindeki chunk'ları da temizler.
    """
    logger.info(f"RobotPDF (ID: {instance.id}, Adı: {instance.dosya_adi}) silindi. İlişkili dosyalar temizleniyor.")
    
    # Önce RAG chunks'larını temizle
    try:
        rag_service = RAGService()
        deleted_chunks = rag_service.delete_chunks_for_pdf(instance.id)
        logger.info(f"RobotPDF (ID: {instance.id}) için {deleted_chunks} chunk silindi.")
    except Exception as e:
        logger.error(f"RAG chunks silinirken hata oluştu: {e}")
    
    # Sonra dosyaları sil
    delete_pdf_from_services(instance) 