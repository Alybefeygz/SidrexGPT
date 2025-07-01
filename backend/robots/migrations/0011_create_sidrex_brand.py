# Generated manually for Sidrex brand creation

from django.db import migrations


def create_sidrex_brand(apps, schema_editor):
    """Sidrex markasını oluştur"""
    Brand = apps.get_model('robots', 'Brand')
    Brand.objects.get_or_create(
        name='Sidrex',
        defaults={
            'total_api_requests': 0
        }
    )


def reverse_sidrex_brand(apps, schema_editor):
    """Sidrex markasını sil (geri alma)"""
    Brand = apps.get_model('robots', 'Brand')
    Brand.objects.filter(name='Sidrex').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0010_add_brand_model'),
    ]

    operations = [
        migrations.RunPython(create_sidrex_brand, reverse_sidrex_brand),
    ] 