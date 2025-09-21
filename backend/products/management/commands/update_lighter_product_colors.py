from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Urun kartlarinin renklerini daha acik gradient renklerle gunceller'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Urun karti renklerini daha acik gradientlarla guncelleniyor...'))
        
        # Daha acik renk guncellemeleri - Imuntus/Imuntus Kids stilinde
        color_mappings = {
            # Imuntus ve Imuntus Kids ayni kaliyor
            'Imuntus': 'bg-gradient-to-br from-orange-100 via-yellow-50 to-orange-200',
            'Imuntus Kids': 'bg-gradient-to-br from-orange-100 via-yellow-50 to-orange-200',
            
            # Mag4Ever ayni kaliyor (istenmedi)
            # 'Mag4Ever': 'bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-200',
            
            # Diger urunler daha acik renkler
            'Lipo Iron Complex': 'bg-gradient-to-br from-red-100 via-pink-50 to-indigo-200',  # Kirmizi-mor acik
            'Milk Thistle Complex': 'bg-gradient-to-br from-purple-100 via-violet-50 to-cyan-200',  # Mor-turkuaz acik
            'Olivia': 'bg-gradient-to-br from-lime-100 via-yellow-50 to-amber-200',  # Sari-krem acik
            "Pro Men's Once Daily": 'bg-gradient-to-br from-green-100 via-emerald-50 to-blue-200',  # Yesil-mavi acik
            "Repro Women's Once Daily": 'bg-gradient-to-br from-fuchsia-100 via-pink-50 to-yellow-200',  # Pembe-sari acik
            'Slm-X': 'bg-gradient-to-br from-green-100 via-lime-50 to-yellow-200',  # Yesil-sari acik
            'Zzen': 'bg-gradient-to-br from-sky-100 via-blue-50 to-slate-100',  # Mavi-beyaz acik
        }
        
        # Her urun icin renk guncelle
        updated_count = 0
        for product_name, bg_color in color_mappings.items():
            try:
                product = Product.objects.get(name=product_name)
                if product.bg_color != bg_color:  # Sadece degisen renkleri guncelle
                    product.bg_color = bg_color
                    product.save()
                    self.stdout.write(f'OK {product_name} -> {bg_color}')
                    updated_count += 1
                else:
                    self.stdout.write(f'SKIP {product_name} (ayni renk)')
            except Product.DoesNotExist:
                self.stdout.write(f'ERROR {product_name} bulunamadi')
        
        self.stdout.write(self.style.SUCCESS(f'Toplam {updated_count} urun karti rengi acik gradientlarla guncellendi!'))