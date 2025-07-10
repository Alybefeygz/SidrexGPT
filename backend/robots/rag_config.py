# RAG System Configuration
from django.conf import settings
import os

class RAGConfig:
    """RAG sistemi için merkezi konfigürasyon sınıfı"""
    
    # Chunklama Parametreleri
    CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '512'))
    CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '100'))
    
    # Embedding Parametreleri
    EMBEDDING_MODEL = os.getenv('RAG_EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
    EMBEDDING_DIMENSIONS = int(os.getenv('RAG_EMBEDDING_DIM', '384'))
    
    # Arama Parametreleri
    TOP_K = int(os.getenv('RAG_TOP_K', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.2'))
    
    # LLM Parametreleri
    MAX_CONTEXT_LENGTH = int(os.getenv('RAG_MAX_CONTEXT_LENGTH', '4000'))
    LLM_MODEL = os.getenv('RAG_LLM_MODEL', 'gpt-3.5-turbo')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENROUTER_API_KEY', None)
    
    # Test ve Debug
    DEBUG_RAG = os.getenv('RAG_DEBUG', 'False').lower() == 'true'
    LOG_QUERIES = os.getenv('RAG_LOG_QUERIES', 'True').lower() == 'true'
    
    @classmethod
    def get_chunk_settings(cls):
        """Chunklama ayarlarını döndürür"""
        return {
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP
        }
    
    @classmethod
    def get_embedding_settings(cls):
        """Embedding ayarlarını döndürür"""
        return {
            'model': cls.EMBEDDING_MODEL,
            'dimensions': cls.EMBEDDING_DIMENSIONS,
            'api_key': cls.OPENAI_API_KEY
        }
    
    @classmethod
    def get_search_settings(cls):
        """Arama ayarlarını döndürür"""
        return {
            'top_k': cls.TOP_K,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD
        }
    
    @classmethod
    def get_llm_settings(cls):
        """LLM ayarlarını döndürür"""
        return {
            'model': cls.LLM_MODEL,
            'api_key': cls.OPENAI_API_KEY,
            'max_context_length': cls.MAX_CONTEXT_LENGTH
        }

# Test için farklı chunk size senaryoları
CHUNK_SCENARIOS = {
    'small': {'chunk_size': 256, 'chunk_overlap': 50, 'name': 'Küçük Parçalar'},
    'medium': {'chunk_size': 512, 'chunk_overlap': 100, 'name': 'Orta Parçalar'},
    'large': {'chunk_size': 1024, 'chunk_overlap': 200, 'name': 'Büyük Parçalar'},
}

# Embedding modelleri
EMBEDDING_MODELS = {
    'openai_small': {
        'model': 'text-embedding-3-small',
        'dimensions': 1536,
        'cost_per_1k_tokens': 0.00002,
        'name': 'OpenAI Small (Hızlı & Ucuz)'
    },
    'openai_large': {
        'model': 'text-embedding-3-large',
        'dimensions': 3072,
        'cost_per_1k_tokens': 0.00013,
        'name': 'OpenAI Large (Yüksek Kalite)'
    },
    'sentence_transformer': {
        'model': 'paraphrase-multilingual-MiniLM-L12-v2',
        'dimensions': 384,
        'cost_per_1k_tokens': 0.0,
        'name': 'Sentence Transformer (Ücretsiz, Türkçe)'
    }
} 