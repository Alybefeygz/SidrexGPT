from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Ürün kartlarının renklerini özel gradient renklerle günceller'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Urun karti renklerini ozel gradientlarla guncelleniyor...'))
        
        # Renk guncellemeleri - CSS style kullanarak
        color_mappings = {
            'Imuntus': 'bg-gradient-to-br from-orange-100 via-yellow-50 to-orange-200',  # Imuntus Kids ile ayni
            'Lipo Iron Complex': 'bg-gradient-to-br from-red-500 to-indigo-800',  # #E82423 - #514F6E
            'Milk Thistle Complex': 'bg-gradient-to-br from-purple-500 to-cyan-400',  # #9F5DBA - #74C8CC
            'Olivia': 'bg-gradient-to-br from-lime-400 to-yellow-100',  # #D9E60D - #FEFEBC
            "Pro Men's Once Daily": 'bg-gradient-to-br from-green-400 to-blue-700',  # #88ED92 - #196283
            "Repro Women's Once Daily": 'bg-gradient-to-br from-fuchsia-400 to-yellow-300',  # #E78EEB - #FCCC56
            'Slm-X': 'bg-gradient-to-br from-green-500 to-yellow-400',  # #4EBA21 - #FFEF00
            'Zzen': 'bg-gradient-to-br from-sky-400 to-white',  # #5FA6E9 - #ffffff
        }
        
        # Her urun icin renk guncelle
        for product_name, bg_color in color_mappings.items():
            try:
                product = Product.objects.get(name=product_name)
                product.bg_color = bg_color
                product.save()
                self.stdout.write(f'OK {product_name} -> {bg_color}')
            except Product.DoesNotExist:
                self.stdout.write(f'ERROR {product_name} bulunamadi')
        
        self.stdout.write(self.style.SUCCESS('Tum urun karti renkleri ozel gradientlarla guncellendi!'))