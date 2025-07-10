from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'PostgreSQL veritabanına pgvector eklentisini kurar ve gerekli indeksleri oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut tablolar varsa zorla yeniden oluştur'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.NOTICE('🔧 pgvector kurulumu başlıyor...'))

        try:
            with connection.cursor() as cursor:
                # pgvector eklentisini kur
                self.stdout.write('📦 pgvector eklentisi kuruluyor...')
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # PDF chunk'ları için tablo oluştur
                self.stdout.write('📋 PDF chunk tablosu oluşturuluyor...')
                
                if force:
                    cursor.execute("DROP TABLE IF EXISTS pdf_chunks CASCADE;")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pdf_chunks (
                        id SERIAL PRIMARY KEY,
                        robot_pdf_id INTEGER NOT NULL,
                        chunk_text TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        embedding vector(384),
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (robot_pdf_id) REFERENCES robots_robotpdf(id) ON DELETE CASCADE
                    );
                """)
                
                # Performans için indeksler oluştur
                self.stdout.write('⚡ Vektör indeksleri oluşturuluyor...')
                
                # HNSW indeksi (cosine distance için)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_embedding_cosine_idx 
                    ON pdf_chunks USING hnsw (embedding vector_cosine_ops);
                """)
                
                # HNSW indeksi (L2 distance için)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_embedding_l2_idx 
                    ON pdf_chunks USING hnsw (embedding vector_l2_ops);
                """)
                
                # Robot PDF ID için indeks
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_robot_pdf_id_idx 
                    ON pdf_chunks (robot_pdf_id);
                """)
                
                # Metadata için GIN indeks
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_metadata_idx 
                    ON pdf_chunks USING gin (metadata);
                """)
                
                # Türkçe karakter desteği için fuzzy search
                self.stdout.write('🔍 Fuzzy text search kurulumu...')
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                
                # Text için GIN indeks (fuzzy search)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_text_gin_idx 
                    ON pdf_chunks USING gin(chunk_text gin_trgm_ops);
                """)
                
                # Normalized text için indeks
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS pdf_chunks_normalized_idx 
                    ON pdf_chunks USING gin(lower(chunk_text) gin_trgm_ops);
                """)
                
                # Güncelleme trigger'ı oluştur
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION update_pdf_chunks_updated_at()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                """)
                
                cursor.execute("""
                    DROP TRIGGER IF EXISTS update_pdf_chunks_updated_at_trigger ON pdf_chunks;
                    CREATE TRIGGER update_pdf_chunks_updated_at_trigger
                        BEFORE UPDATE ON pdf_chunks
                        FOR EACH ROW
                        EXECUTE FUNCTION update_pdf_chunks_updated_at();
                """)
                
                # Hibrit similarity search fonksiyonu oluştur (vector + text)
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION search_similar_chunks(
                        query_embedding vector(384),
                        robot_pdf_ids integer[] DEFAULT NULL,
                        limit_count integer DEFAULT 5,
                        similarity_threshold float DEFAULT 0.7
                    )
                    RETURNS TABLE(
                        id integer,
                        robot_pdf_id integer,
                        chunk_text text,
                        chunk_index integer,
                        similarity float,
                        metadata jsonb
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT 
                            pc.id,
                            pc.robot_pdf_id,
                            pc.chunk_text,
                            pc.chunk_index,
                            (1 - (pc.embedding <=> query_embedding))::float as similarity,
                            pc.metadata
                        FROM pdf_chunks pc
                        WHERE 
                            (robot_pdf_ids IS NULL OR pc.robot_pdf_id = ANY(robot_pdf_ids))
                            AND (1 - (pc.embedding <=> query_embedding)) >= similarity_threshold
                        ORDER BY 
                            (1 - (pc.embedding <=> query_embedding)) DESC
                        LIMIT limit_count;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                # Text similarity search fonksiyonu (fuzzy match için)
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION search_fuzzy_chunks(
                        search_term text,
                        robot_pdf_ids integer[] DEFAULT NULL,
                        limit_count integer DEFAULT 10,
                        similarity_threshold float DEFAULT 0.3
                    )
                    RETURNS TABLE(
                        id integer,
                        robot_pdf_id integer,
                        chunk_text text,
                        chunk_index integer,
                        text_similarity float,
                        metadata jsonb
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT 
                            pc.id,
                            pc.robot_pdf_id,
                            pc.chunk_text,
                            pc.chunk_index,
                            similarity(lower(pc.chunk_text), lower(search_term))::float as text_similarity,
                            pc.metadata
                        FROM pdf_chunks pc
                        WHERE 
                            (robot_pdf_ids IS NULL OR pc.robot_pdf_id = ANY(robot_pdf_ids))
                            AND similarity(lower(pc.chunk_text), lower(search_term)) >= similarity_threshold
                        ORDER BY 
                            similarity(lower(pc.chunk_text), lower(search_term)) DESC
                        LIMIT limit_count;
                    END;
                    $$ LANGUAGE plpgsql;
                """)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ pgvector kurulumu başarısız: {e}')
            )
            logger.error(f"pgvector kurulum hatası: {e}")
            return

        self.stdout.write(self.style.SUCCESS('✅ pgvector kurulumu tamamlandı!'))
        self.stdout.write(self.style.NOTICE('💡 Kullanım: python manage.py chunk_pdfs')) 