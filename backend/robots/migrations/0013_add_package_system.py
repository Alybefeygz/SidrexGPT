# Generated manually for Brand package system

from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta


def set_default_package_data(apps, schema_editor):
    """Mevcut Brand kayıtları için paket bilgilerini ayarla"""
    Brand = apps.get_model('robots', 'Brand')
    for brand in Brand.objects.all():
        brand.paket_turu = 'normal'
        brand.paket_suresi = 30
        brand.paket_baslangic_tarihi = timezone.now()
        brand.paket_bitis_tarihi = timezone.now() + timedelta(days=30)
        brand.request_limit = 500  # Normal paket limiti
        brand.save()


def reverse_package_data(apps, schema_editor):
    """Reverse migration için - paket verilerini temizle"""
    pass  # Reverse'da özel bir şey yapmaya gerek yok


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0012_add_request_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='paket_turu',
            field=models.CharField(
                choices=[('normal', 'Normal Paket'), ('pro', 'Pro Paket'), ('premium', 'Premium Paket')],
                default='normal',
                max_length=10,
                verbose_name='Paket Türü'
            ),
        ),
        migrations.AddField(
            model_name='brand',
            name='paket_suresi',
            field=models.PositiveIntegerField(default=30, verbose_name='Paket Süresi (Gün)'),
        ),
        migrations.AddField(
            model_name='brand',
            name='paket_baslangic_tarihi',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Paket Başlangıç Tarihi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brand',
            name='paket_bitis_tarihi',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Paket Bitiş Tarihi'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='request_limit',
            field=models.PositiveIntegerField(default=500, verbose_name='İstek Sınırı'),
        ),
        migrations.RunPython(set_default_package_data, reverse_package_data),
    ] 