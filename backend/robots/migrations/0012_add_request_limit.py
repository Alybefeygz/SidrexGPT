# Generated manually for Brand request limit

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0011_create_sidrex_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='request_limit',
            field=models.PositiveIntegerField(default=1000, verbose_name='İstek Sınırı'),
        ),
    ] 