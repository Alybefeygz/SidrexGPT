# Generated manually for robot-brand relationship

from django.db import migrations, models
import django.db.models.deletion


def set_default_brand(apps, schema_editor):
    """Mevcut robotları Sidrex markasına bağla"""
    Brand = apps.get_model('robots', 'Brand')
    Robot = apps.get_model('robots', 'Robot')
    
    # Sidrex markasını al veya oluştur
    sidrex_brand, created = Brand.objects.get_or_create(
        name='Sidrex',
        defaults={
            'total_api_requests': 0,
            'paket_turu': 'normal',
            'paket_suresi': 30
        }
    )
    
    # Tüm mevcut robotları Sidrex markasına bağla
    Robot.objects.filter(brand__isnull=True).update(brand=sidrex_brand)


def reverse_brand_assignment(apps, schema_editor):
    """Geri alma işlemi - brand field'ını NULL yap"""
    Robot = apps.get_model('robots', 'Robot')
    Robot.objects.all().update(brand=None)


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0013_add_package_system'),
    ]

    operations = [
        # Önce field'ı null olarak ekle
        migrations.AddField(
            model_name='robot',
            name='brand',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='robots',
                to='robots.brand',
                verbose_name='Marka'
            ),
        ),
        # Data migration - robotları Sidrex markasına bağla
        migrations.RunPython(set_default_brand, reverse_brand_assignment),
        # Field'ı not null yap
        migrations.AlterField(
            model_name='robot',
            name='brand',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='robots',
                to='robots.brand',
                verbose_name='Marka'
            ),
        ),
    ] 