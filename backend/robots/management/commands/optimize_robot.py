from django.core.management.base import BaseCommand
from robots.models import Robot
from robots.services import (
    toggle_optimization_mode, 
    is_optimization_enabled,
    get_optimization_stats,
    get_robot_pdf_contents_for_ai,
    get_optimized_robot_pdf_contents_for_ai
)


class Command(BaseCommand):
    help = 'Robot optimizasyonu açar/kapatır ve performans analizi yapar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--robot-id',
            type=int,
            help='Optimize edilecek robot ID\'si'
        )
        parser.add_argument(
            '--enable',
            action='store_true',
            help='Optimizasyonu aç'
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Optimizasyonu kapat'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mevcut durumu göster'
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Performans analizi yap'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🚀 SİDREX ROBOT OPTİMİZASYON YÖNETİCİSİ'))
        self.stdout.write('=' * 50)
        
        robot_id = options.get('robot_id')
        
        # Robot ID verilmediyse, tüm robotları listele
        if not robot_id:
            self.list_robots()
            return
        
        # Robot'u bul
        try:
            robot = Robot.objects.get(id=robot_id)
            self.stdout.write(f'✅ Robot bulundu: {robot.name} (ID: {robot.id})')
        except Robot.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Robot bulunamadı: ID {robot_id}'))
            return
        
        # Durum kontrolü
        if options.get('status'):
            self.show_status(robot)
        
        # Performans analizi
        if options.get('analyze'):
            self.analyze_performance(robot)
        
        # Optimizasyonu aç
        if options.get('enable'):
            self.enable_optimization(robot)
        
        # Optimizasyonu kapat
        if options.get('disable'):
            self.disable_optimization(robot)
        
        # Hiçbir aksiyon belirtilmediyse, Imuntus Kids için otomatik aç
        if not any([options.get('status'), options.get('analyze'), 
                   options.get('enable'), options.get('disable')]):
            if robot.name == 'Imuntus Kids':
                self.stdout.write('\n🎯 Log analizi sonucu Imuntus Kids için optimizasyon açılıyor...')
                self.enable_optimization(robot)
                self.analyze_performance(robot)

    def list_robots(self):
        self.stdout.write('\n📋 MEVCUT ROBOTLAR:')
        robots = Robot.objects.all()
        for robot in robots:
            status = is_optimization_enabled(robot.id)
            status_text = 'AÇIK ⚡' if status else 'KAPALI 🔄'
            self.stdout.write(f'   ID: {robot.id} - {robot.name} ({robot.get_slug()}) - {status_text}')
        
        self.stdout.write('\n💡 Kullanım:')
        self.stdout.write('   python manage.py optimize_robot --robot-id=2 --enable')
        self.stdout.write('   python manage.py optimize_robot --robot-id=2 --analyze')

    def show_status(self, robot):
        self.stdout.write(f'\n📊 ROBOT DURUMU: {robot.name}')
        self.stdout.write('-' * 30)
        
        # Optimizasyon durumu
        enabled = is_optimization_enabled(robot.id)
        status_text = 'AÇIK ⚡' if enabled else 'KAPALI 🔄'
        self.stdout.write(f'Optimizasyon: {status_text}')
        
        # PDF sayısı
        pdf_count = robot.pdf_dosyalari.filter(is_active=True).count()
        self.stdout.write(f'Aktif PDF: {pdf_count} adet')
        
        # İstatistikler
        stats = get_optimization_stats(robot.id)
        if stats:
            self.stdout.write(f'Toplam İstek: {stats.get("total_requests", 0)}')
            self.stdout.write(f'Ortalama Süre: {stats.get("avg_response_time", 0)} saniye')

    def analyze_performance(self, robot):
        self.stdout.write(f'\n📈 PERFORMANS ANALİZİ: {robot.name}')
        self.stdout.write('-' * 40)
        
        try:
            # İçerik boyutu karşılaştırması
            standard_content = get_robot_pdf_contents_for_ai(robot)
            optimized_content = get_optimized_robot_pdf_contents_for_ai(robot)
            
            standard_size = len(standard_content)
            optimized_size = len(optimized_content)
            reduction = ((standard_size - optimized_size) / standard_size) * 100 if standard_size > 0 else 0
            
            self.stdout.write(f'📄 Standart İçerik: {standard_size:,} karakter')
            self.stdout.write(f'⚡ Optimize İçerik: {optimized_size:,} karakter')
            self.stdout.write(f'📉 Azalma: {reduction:.1f}% ({standard_size - optimized_size:,} karakter)')
            
            # Token tahmini
            standard_tokens = standard_size // 3
            optimized_tokens = optimized_size // 3
            token_savings = standard_tokens - optimized_tokens
            
            self.stdout.write(f'\n🪙 TOKEN TAHMİNİ:')
            self.stdout.write(f'   Standart: ~{standard_tokens:,} token')
            self.stdout.write(f'   Optimize: ~{optimized_tokens:,} token')
            self.stdout.write(f'   Tasarruf: ~{token_savings:,} token (%{((token_savings/standard_tokens)*100):.1f})')
            
            # Hız tahmini (log'dan: 31,109 karakter = 8.25s)
            speed_ratio = 8.25 / 31109  # saniye/karakter
            estimated_standard_time = standard_size * speed_ratio
            estimated_optimized_time = optimized_size * speed_ratio
            time_savings = estimated_standard_time - estimated_optimized_time
            
            self.stdout.write(f'\n⏱️ HIZ TAHMİNİ:')
            self.stdout.write(f'   Standart: ~{estimated_standard_time:.1f} saniye')
            self.stdout.write(f'   Optimize: ~{estimated_optimized_time:.1f} saniye')
            self.stdout.write(f'   Tasarruf: ~{time_savings:.1f} saniye (%{((time_savings/estimated_standard_time)*100):.1f})')
            
            # Öneri
            if reduction > 50:
                self.stdout.write(f'\n💡 ÖNERİ: Optimizasyon ŞİDDETLE önerilir!')
                self.stdout.write(f'   🎯 Log\'daki 9.16s → ~{estimated_optimized_time + 0.9:.1f}s (toplam süre)')
            else:
                self.stdout.write(f'\n💡 ÖNERİ: Mevcut performans yeterli.')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Analiz hatası: {e}'))

    def enable_optimization(self, robot):
        self.stdout.write(f'\n⚡ OPTİMİZASYON AÇILIYOR: {robot.name}')
        
        current_status = is_optimization_enabled(robot.id)
        if current_status:
            self.stdout.write('✅ Optimizasyon zaten aktif!')
            return
        
        success = toggle_optimization_mode(robot.id, True)
        if success:
            self.stdout.write('✅ Optimizasyon başarıyla AKTİF edildi!')
            self.stdout.write('\n🧪 TEST ÖNERİSİ:')
            self.stdout.write('   Aynı mesajı tekrar gönderin: "merhaba"')
            self.stdout.write('   Yanıt süresini karşılaştırın!')
        else:
            self.stdout.write(self.style.ERROR('❌ Optimizasyon aktif edilemedi!'))

    def disable_optimization(self, robot):
        self.stdout.write(f'\n🔄 OPTİMİZASYON KAPATILIYOR: {robot.name}')
        
        current_status = is_optimization_enabled(robot.id)
        if not current_status:
            self.stdout.write('ℹ️ Optimizasyon zaten kapalı!')
            return
        
        success = toggle_optimization_mode(robot.id, False)
        if success:
            self.stdout.write('✅ Optimizasyon başarıyla KAPALI!')
        else:
            self.stdout.write(self.style.ERROR('❌ Optimizasyon kapatılamadı!')) 