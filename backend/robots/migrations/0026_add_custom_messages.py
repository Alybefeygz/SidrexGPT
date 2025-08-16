# Generated migration for custom_messages field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0025_allow_null_user_in_chat_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='robot',
            name='custom_messages',
            field=models.JSONField(blank=True, default=list, help_text='ZZEN robot için özelleştirilebilir mesajlar (maksimum 5 adet)', verbose_name='Özel Robot Mesajları'),
        ),
    ]