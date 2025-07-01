# Generated manually for user-brand relationship

from django.db import migrations, models
import django.db.models.deletion


def assign_users_to_brand(apps, schema_editor):
    """Mevcut kullanıcıları Sidrex markasına bağla"""
    Brand = apps.get_model('robots', 'Brand')
    Profil = apps.get_model('profiller', 'Profil')
    
    # Sidrex markasını bul
    try:
        sidrex_brand = Brand.objects.get(name='Sidrex')
        # Tüm profilleri Sidrex markasına bağla
        Profil.objects.filter(brand__isnull=True).update(brand=sidrex_brand)
        print(f"Tüm kullanıcılar {sidrex_brand.name} markasına (ID: {sidrex_brand.id}) bağlandı")
    except Brand.DoesNotExist:
        print("Sidrex markası bulunamadı!")


def reverse_user_brand_assignment(apps, schema_editor):
    """Geri alma işlemi"""
    Profil = apps.get_model('profiller', 'Profil')
    Profil.objects.all().update(brand=None)


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0014_add_brand_to_robot'),
        ('profiller', '0002_alter_profil_options_alter_profildurum_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='brand',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='users',
                to='robots.brand',
                verbose_name='Marka'
            ),
        ),
        # Data migration - kullanıcıları Sidrex markasına bağla
        migrations.RunPython(assign_users_to_brand, reverse_user_brand_assignment),
    ] 