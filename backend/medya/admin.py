from django.contrib import admin
from .models import Medya, StatikVarlik

@admin.register(Medya)
class MedyaAdmin(admin.ModelAdmin):
    list_display = ['adi', 'supabase_path', 'yuklenme_tarihi']
    list_filter = ['yuklenme_tarihi']
    search_fields = ['adi']
    readonly_fields = ['yuklenme_tarihi', 'public_url']

@admin.register(StatikVarlik)
class StatikVarlikAdmin(admin.ModelAdmin):
    list_display = ['anahtar', 'supabase_path', 'aciklama']
    search_fields = ['anahtar', 'aciklama']
    readonly_fields = ['public_url']
