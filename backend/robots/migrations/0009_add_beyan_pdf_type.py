# Generated manually for beyan PDF type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0007_add_has_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='robotpdf',
            name='has_declaration',
            field=models.BooleanField(default=False, verbose_name='Beyan PDF\'i mi?'),
        ),
        migrations.AlterField(
            model_name='robotpdf',
            name='pdf_type',
            field=models.CharField(
                choices=[
                    ('bilgi', 'Bilgi'), 
                    ('kural', 'Kural'), 
                    ('rol', 'Rol'), 
                    ('beyan', 'Beyan')
                ], 
                default='bilgi', 
                max_length=10, 
                verbose_name='PDF Türü'
            ),
        ),
    ] 