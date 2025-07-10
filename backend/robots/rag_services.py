import os
import json
import logging
import tiktoken
from typing import List, Dict, Any, Tuple, Optional
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from .rag_config import RAGConfig, EMBEDDING_MODELS
from .models import RobotPDF, Brand
import unicodedata
import re

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """Türkçe karakterleri normalize et ve RAG için optimize et"""
    if not text:
        return ""
    
    # Küçük harfe çevir
    text = text.lower()
    
    # Türkçe karakter normalizasyonu
    text = text.replace('ı', 'i')
    text = text.replace('ğ', 'g')
    text = text.replace('ü', 'u')
    text = text.replace('ş', 's')
    text = text.replace('ç', 'c')
    text = text.replace('ö', 'o')
    
    # Yaygın yanlış yazımları düzelt
    text = text.replace('bağşıklık', 'bağışıklık')  # ş→ş normalizasyonu için
    text = text.replace('bagsiklik', 'bagisiklik')  # s→ş normalizasyonu için
    text = text.replace('bagsıklık', 'bagisiklik')  # karma hata
    
    # Normalize sonrası tekrar türkçe karakter temizlik
    text = text.replace('ı', 'i')
    text = text.replace('ş', 's')
    text = text.replace('ğ', 'g')
    
    # Ekstra boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

class EmbeddingService:
    """Embedding oluşturma ve yönetimi servisi"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or RAGConfig.EMBEDDING_MODEL
        self.model_config = self._get_model_config()
        self.client = None
        self.sentence_model = None
        self._initialize_model()
    
    def _get_model_config(self):
        """Model konfigürasyonunu al"""
        for key, config in EMBEDDING_MODELS.items():
            if config['model'] == self.model_name:
                return config
        # Varsayılan OpenAI small
        return EMBEDDING_MODELS['openai_small']
    
    def _initialize_model(self):
        """Model'i başlat"""
        if 'openai' in self.model_config['name'].lower():
            self.client = OpenAI(api_key=RAGConfig.OPENAI_API_KEY)
        else:
            # Sentence Transformer için
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer(self.model_name)
    
    def create_embedding(self, text: str) -> List[float]:
        """Tekst için embedding oluştur"""
        try:
            if self.client:
                # OpenAI embedding
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=text
                )
                return response.data[0].embedding
            else:
                # Sentence Transformer embedding
                embedding = self.sentence_model.encode(text)
                return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Embedding oluşturma hatası: {e}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Toplu embedding oluştur"""
        embeddings = []
        for text in texts:
            embedding = self.create_embedding(text)
            embeddings.append(embedding)
        return embeddings

class ChunkingService:
    """PDF chunklama servisi"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or RAGConfig.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or RAGConfig.CHUNK_OVERLAP
        
        # Token sayısı için tiktoken
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _token_length(self, text: str) -> int:
        """Token sayısını hesapla"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Metni chunk'lara böl"""
        if not text or not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        
        # Her chunk için metadata ekle
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'chunk_index': i,
                'token_count': self._token_length(chunk),
                'metadata': metadata or {}
            }
            result.append(chunk_data)
        
        return result

class VectorSearchService:
    """Vektör arama servisi"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def search_similar_chunks(
        self, 
        query: str, 
        robot_pdf_ids: List[int] = None,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Benzer chunk'ları ara"""
        
        top_k = top_k or RAGConfig.TOP_K
        similarity_threshold = similarity_threshold or RAGConfig.SIMILARITY_THRESHOLD
        
        # Query'yi normalize et (Türkçe karakter sorunu için)
        normalized_query = normalize_text(query)
        
        # Hem orijinal hem de normalize edilmiş query ile ara
        query_embedding = self.embedding_service.create_embedding(query)
        normalized_embedding = self.embedding_service.create_embedding(normalized_query)
        
        # İki embedding'in ortalamasını al (hibrit yaklaşım)
        hybrid_embedding = [(a + b) / 2 for a, b in zip(query_embedding, normalized_embedding)]
        
        with connection.cursor() as cursor:
            if robot_pdf_ids:
                cursor.execute("""
                    SELECT * FROM search_similar_chunks(
                        %s::vector, %s, %s, %s
                    )
                """, [hybrid_embedding, robot_pdf_ids, top_k, similarity_threshold])
            else:
                cursor.execute("""
                    SELECT * FROM search_similar_chunks(
                        %s::vector, NULL, %s, %s
                    )
                """, [hybrid_embedding, top_k, similarity_threshold])
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
    
    def search_fuzzy_chunks(
        self, 
        query: str, 
        robot_pdf_ids: List[int] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Fuzzy text search ile chunk ara (embedding bulamadığında fallback)"""
        
        # Query'yi normalize et
        normalized_query = normalize_text(query)
        
        with connection.cursor() as cursor:
            if robot_pdf_ids:
                cursor.execute("""
                    SELECT * FROM search_fuzzy_chunks(
                        %s, %s, %s, %s
                    )
                """, [normalized_query, robot_pdf_ids, top_k, similarity_threshold])
            else:
                cursor.execute("""
                    SELECT * FROM search_fuzzy_chunks(
                        %s, NULL, %s, %s
                    )
                """, [normalized_query, top_k, similarity_threshold])
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # Consistency için similarity field'ını ekle
                result['similarity'] = result.get('text_similarity', 0.0)
                results.append(result)
            
            return results

    def search_with_fallback(
        self, 
        query: str, 
        robot_pdf_ids: List[int] = None,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Önce vector search, sonuçsuzsa fuzzy search (Türkçe karakter sorunları için)"""
        
        # Önce normal vector search dene
        vector_results = self.search_similar_chunks(
            query=query,
            robot_pdf_ids=robot_pdf_ids,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        # Eğer yeterli sonuç varsa vector search sonuçlarını döndür
        min_results = 1  # Minimum sonuç sayısı - daha agresif
        if len(vector_results) >= min_results:
            # Ama yine de fuzzy search'i de ekleyelim karmaşık sorular için
            pass
        
        # Yetersizse fuzzy search ile destekle
        fuzzy_results = self.search_fuzzy_chunks(
            query=query,
            robot_pdf_ids=robot_pdf_ids,
            top_k=top_k or 10,
            similarity_threshold=0.2  # Daha düşük threshold
        )
        
        # Her iki sonucu birleştir ve tekrarları temizle
        all_results = vector_results.copy()
        existing_ids = {result['id'] for result in vector_results}
        
        for fuzzy_result in fuzzy_results:
            if fuzzy_result['id'] not in existing_ids:
                all_results.append(fuzzy_result)
                existing_ids.add(fuzzy_result['id'])
        
        # Similarity skoruna göre sırala
        all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Top_k limitini uygula
        final_top_k = top_k or RAGConfig.TOP_K
        return all_results[:final_top_k]
    
    def store_chunks(self, robot_pdf_id: int, chunks: List[Dict[str, Any]]):
        """Chunk'ları veritabanına kaydet"""
        if not chunks:
            return
        
        # Önce mevcut chunk'ları sil
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM pdf_chunks WHERE robot_pdf_id = %s",
                [robot_pdf_id]
            )
        
        # Yeni chunk'ları ekle
        for chunk in chunks:
            # Hem orijinal hem de normalize edilmiş text için embedding oluştur
            original_text = chunk['text']
            normalized_text = normalize_text(original_text)
            
            # Hibrit embedding oluştur
            original_embedding = self.embedding_service.create_embedding(original_text)
            normalized_embedding = self.embedding_service.create_embedding(normalized_text)
            embedding = [(a + b) / 2 for a, b in zip(original_embedding, normalized_embedding)]
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pdf_chunks 
                    (robot_pdf_id, chunk_text, chunk_index, embedding, metadata)
                    VALUES (%s, %s, %s, %s::vector, %s)
                """, [
                    robot_pdf_id,
                    chunk['text'],
                    chunk['chunk_index'],
                    embedding,
                    json.dumps(chunk['metadata'])
                ])

class RAGService:
    """Ana RAG servisi - tüm bileşenleri koordine eder"""
    
    def __init__(self):
        self.chunking_service = ChunkingService()
        self.vector_service = VectorSearchService()
        self.embedding_service = EmbeddingService()
    
    def process_pdf(self, robot_pdf: RobotPDF, scenario: str = 'medium') -> Dict[str, Any]:
        """PDF'i işle ve chunk'la"""
        from .rag_config import CHUNK_SCENARIOS
        
        if not robot_pdf.pdf_icerigi:
            return {
                'success': False,
                'error': 'PDF içeriği bulunamadı'
            }
        
        # Senaryo ayarlarını al
        if scenario in CHUNK_SCENARIOS:
            chunk_config = CHUNK_SCENARIOS[scenario]
            chunking_service = ChunkingService(
                chunk_size=chunk_config['chunk_size'],
                chunk_overlap=chunk_config['chunk_overlap']
            )
        else:
            chunking_service = self.chunking_service
        
        # Metadata hazırla
        metadata = {
            'pdf_id': robot_pdf.id,
            'pdf_name': robot_pdf.dosya_adi,
            'pdf_type': robot_pdf.pdf_type,
            'robot_id': robot_pdf.robot.id,
            'scenario': scenario
        }
        
        # Chunk'la
        chunks = chunking_service.chunk_text(
            robot_pdf.pdf_icerigi, 
            metadata
        )
        
        if not chunks:
            return {
                'success': False,
                'error': 'PDF chunk\'lanamadı'
            }
        
        # Veritabanına kaydet
        try:
            self.vector_service.store_chunks(robot_pdf.id, chunks)
            
            return {
                'success': True,
                'chunks_count': len(chunks),
                'scenario': scenario,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"PDF işleme hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_relevant_context(
        self, 
        query: str, 
        robot_id: int,
        max_context_length: int = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Sorgu için alakalı context'i al"""
        
        max_context_length = max_context_length or RAGConfig.MAX_CONTEXT_LENGTH
        
        # Robot'un PDF'lerini al
        robot_pdfs = RobotPDF.objects.filter(
            robot_id=robot_id, 
            is_active=True
        ).values_list('id', flat=True)
        
        if not robot_pdfs:
            return "Bu robot için aktif PDF bulunamadı.", []
        
        # Benzer chunk'ları ara (fallback ile)
        similar_chunks = self.vector_service.search_with_fallback(
            query=query,
            robot_pdf_ids=list(robot_pdfs)
        )
        
        if not similar_chunks:
            return "Sorgunuzla alakalı bilgi bulunamadı.", []
        
        # Context oluştur (token limitine dikkat et)
        context_parts = []
        citations = []
        total_tokens = 0
        encoding = tiktoken.get_encoding("cl100k_base")
        
        for chunk in similar_chunks:
            chunk_text = chunk['chunk_text']
            chunk_tokens = len(encoding.encode(chunk_text))
            
            if total_tokens + chunk_tokens > max_context_length:
                break
            
            # Citation bilgisi ekle
            robot_pdf = RobotPDF.objects.get(id=chunk['robot_pdf_id'])
            
            citation = {
                'source': robot_pdf.dosya_adi,
                'content': chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                'similarity': round(chunk['similarity'], 3),
                'chunk_index': chunk['chunk_index'],
                'pdf_type': robot_pdf.pdf_type
            }
            
            citations.append(citation)
            
            # Context'e ekle
            context_parts.append(f"""
--- {robot_pdf.get_pdf_type_display()} ({robot_pdf.dosya_adi}) ---
{chunk_text}
--- BİTİŞ ---
            """.strip())
            
            total_tokens += chunk_tokens
        
        context = "\n\n".join(context_parts)
        
        if RAGConfig.DEBUG_RAG:
            logger.info(f"RAG Context oluşturuldu: {len(citations)} chunk, {total_tokens} token")
        
        return context, citations
    
    def delete_chunks_for_pdf(self, robot_pdf_id: int) -> int:
        """Belirli bir PDF'e ait tüm chunk'ları sil"""
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM pdf_chunks WHERE robot_pdf_id = %s",
                [robot_pdf_id]
            )
            deleted_count = cursor.rowcount
        
        logger.info(f"PDF ID {robot_pdf_id} için {deleted_count} chunk silindi")
        return deleted_count
    
    def process_single_pdf(self, robot_pdf: RobotPDF, scenario: str = 'medium') -> int:
        """Tek bir PDF'i işle ve chunk sayısını döndür"""
        result = self.process_pdf(robot_pdf, scenario)
        
        if result['success']:
            return result['chunks_count']
        else:
            logger.error(f"PDF işleme başarısız: {result.get('error', 'Bilinmeyen hata')}")
            return 0
    
    def update_pdf_type_metadata(self, robot_pdf_id: int, new_pdf_type: str) -> int:
        """PDF chunk'larında type metadata'sını güncelle"""
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pdf_chunks 
                SET metadata = jsonb_set(metadata, '{pdf_type}', %s)
                WHERE robot_pdf_id = %s
            """, [json.dumps(new_pdf_type), robot_pdf_id])
            
            updated_count = cursor.rowcount
        
        logger.info(f"PDF ID {robot_pdf_id} için {updated_count} chunk metadata'sı güncellendi")
        return updated_count

    def log_query(self, query: str, robot_id: int, context: str, citations: List[Dict], response: str):
        """Sorgu ve yanıtı logla (opsiyonel)"""
        if not RAGConfig.LOG_QUERIES:
            return
        
        log_data = {
            'query': query,
            'robot_id': robot_id,
            'citations_count': len(citations),
            'response_length': len(response),
            'context_length': len(context)
        }
        
        logger.info(f"RAG Query: {json.dumps(log_data, ensure_ascii=False)}") 