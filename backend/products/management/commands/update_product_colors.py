from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Ürün kartlarının renklerini güzelleştirir'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Ürün kartı renklerini güzelleştiriliyor...'))
        
        # Imuntus Kids - Çocuk ürünü için sıcak, neşeli renkler
        imuntus_products = Product.objects.filter(name__icontains='Imuntus')
        for product in imuntus_products:
            # Gradyan turuncu-sarı arka plan
            product.bg_color = 'bg-gradient-to-br from-orange-100 via-yellow-50 to-orange-200'
            product.save()
            self.stdout.write(f'✅ {product.name} → Sıcak turuncu-sarı renk')
        
        # Mag4Ever - Magnezyum ürünü için sakin, güven veren renkler  
        mag_products = Product.objects.filter(name__icontains='Mag')
        for product in mag_products:
            # Gradyan mavi-mor arka plan
            product.bg_color = 'bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-200'
            product.save()
            self.stdout.write(f'✅ {product.name} → Sakin mavi-mor renk')
        
        # Genel Sidrex ürünleri için elegant renkler
        other_products = Product.objects.exclude(
            name__icontains='Imuntus'
        ).exclude(
            name__icontains='Mag'
        )
        for product in other_products:
            # Gradyan yeşil-mavi arka plan
            product.bg_color = 'bg-gradient-to-br from-emerald-100 via-teal-50 to-cyan-200'
            product.save()
            self.stdout.write(f'✅ {product.name} → Elegant yeşil-mavi renk')
        
        self.stdout.write(self.style.SUCCESS('🎉 Tüm ürün kartı renkleri güzelleştirildi!')) 