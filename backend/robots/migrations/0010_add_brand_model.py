# Generated manually for Brand model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0009_add_beyan_pdf_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Marka İsmi')),
                ('total_api_requests', models.PositiveIntegerField(default=0, verbose_name='Toplam API İstek Sayısı')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
            ],
            options={
                'verbose_name': 'Marka',
                'verbose_name_plural': 'Markalar',
                'ordering': ['-total_api_requests', 'name'],
            },
        ),
    ] 