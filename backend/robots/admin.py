from django.contrib import admin
from .models import Robot, RobotPDF, Brand, RobotSystemPrompt
from django.utils.html import format_html

# Register your models here.

class RobotPDFInline(admin.TabularInline):
    model = RobotPDF
    extra = 1
    readonly_fields = ['yukleme_zamani', 'has_rules', 'has_role', 'has_info', 'has_declaration']
    fields = ['pdf_dosyasi', 'dosya_adi', 'aciklama', 'is_active', 'pdf_type', 'has_rules', 'has_role', 'has_info', 'has_declaration', 'yukleme_zamani']


class RobotSystemPromptInline(admin.TabularInline):
    model = RobotSystemPrompt
    extra = 0
    fields = ['prompt_type', 'is_active', 'priority', 'topic_keywords', 'prompt_content']
    readonly_fields = []

@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_name', 'brand', 'get_pdf_count', 'get_active_pdf_count', 'yaratilma_zamani', 'guncellenme_zamani']
    list_filter = ['brand', 'yaratilma_zamani']
    search_fields = ['name', 'product_name', 'brand__name']
    readonly_fields = ['yaratilma_zamani', 'guncellenme_zamani']
    list_editable = ['brand']
    inlines = [RobotPDFInline, RobotSystemPromptInline]
    
    def get_pdf_count(self, obj):
        return obj.pdf_dosyalari.count()
    get_pdf_count.short_description = 'Toplam PDF'
    
    def get_active_pdf_count(self, obj):
        return obj.pdf_dosyalari.filter(is_active=True).count()
    get_active_pdf_count.short_description = 'Aktif PDF'


@admin.register(RobotPDF)
class RobotPDFAdmin(admin.ModelAdmin):
    list_display = ['robot', 'dosya_adi', 'is_active', 'pdf_type', 'has_rules', 'has_role', 'has_info', 'has_declaration', 'pdf_link', 'yukleme_zamani']
    list_filter = ['is_active', 'pdf_type', 'has_rules', 'has_role', 'has_info', 'has_declaration', 'yukleme_zamani', 'robot']
    search_fields = ['robot__name', 'dosya_adi']
    readonly_fields = ['yukleme_zamani', 'has_rules', 'has_role', 'has_info', 'has_declaration', 'pdf_link']
    list_editable = ['is_active', 'pdf_type']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('robot')

    def pdf_link(self, obj):
        if obj.pdf_dosyasi:
            return format_html('<a href="{}" target="_blank">PDF Linki</a>', obj.pdf_dosyasi)
        return "-"
    pdf_link.short_description = "PDF Linki (Google Drive)"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'paket_turu', 'total_api_requests', 'request_limit', 'user_count_display', 'user_limit_display', 'remaining_requests_display', 'remaining_days_display', 'package_status_display', 'created_at']
    list_filter = ['paket_turu', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'remaining_requests_display', 'remaining_days_display', 'package_status_display', 'user_count_display', 'user_limit_display', 'user_status_display', 'active_users_list', 'paket_bitis_tarihi', 'request_limit']
    ordering = ['-total_api_requests', 'name']
    list_editable = ['paket_turu']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'total_api_requests', 'request_limit')
        }),
        ('Paket Bilgileri', {
            'fields': ('paket_turu', 'paket_suresi', 'paket_baslangic_tarihi', 'paket_bitis_tarihi')
        }),
        ('Kullanıcı Yönetimi', {
            'fields': ('user_count_display', 'user_limit_display', 'user_status_display', 'active_users_list'),
            'description': 'Marka paketine göre kullanıcı sınırları ve mevcut kullanıcılar'
        }),
        ('Durum Bilgileri', {
            'fields': ('remaining_requests_display', 'remaining_days_display', 'package_status_display')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def remaining_requests_display(self, obj):
        """Kalan istek sayısını göster"""
        remaining = obj.remaining_requests()
        if remaining == 0:
            return f"❌ {remaining}"
        elif remaining < 50:
            return f"⚠️ {remaining}"
        else:
            return f"✅ {remaining}"
    remaining_requests_display.short_description = 'Kalan İstek'
    
    def remaining_days_display(self, obj):
        """Kalan gün sayısını göster"""
        days = obj.remaining_days()
        if days == 0:
            return "⏰ Süresi Doldu"
        elif days < 3:
            return f"⏳ {days} gün"
        else:
            return f"✅ {days} gün"
    remaining_days_display.short_description = 'Kalan Süre'
    
    def package_status_display(self, obj):
        """Paket durumu göstergesi"""
        return obj.package_status()
    package_status_display.short_description = 'Paket Durumu'
    
    def user_count_display(self, obj):
        """Aktif kullanıcı sayısını göster"""
        count = obj.active_users_count()
        if count == 0:
            return "👤 0"
        else:
            return f"👥 {count}"
    user_count_display.short_description = 'Aktif Kullanıcı'
    
    def user_limit_display(self, obj):
        """Kullanıcı limitini göster"""
        limit = obj.get_user_limit()
        if limit == 0:
            return "🚫 Kullanıcı Yok"
        else:
            return f"👤 Max {limit}"
    user_limit_display.short_description = 'Kullanıcı Limiti'
    
    def user_status_display(self, obj):
        """Kullanıcı durumunu göster"""
        return obj.user_status()
    user_status_display.short_description = 'Kullanıcı Durumu'
    
    def active_users_list(self, obj):
        """Aktif kullanıcıların listesini göster"""
        from django.utils.html import format_html
        active_users = obj.users.filter(user__is_active=True).select_related('user')
        
        if not active_users.exists():
            return "Aktif kullanıcı yok"
        
        user_info = []
        for profil in active_users:
            user = profil.user
            status_icon = "🔹" if user.is_staff else "👤"
            user_info.append(f"{status_icon} {user.username} ({user.email})")
        
        return format_html("<br>".join(user_info))
    active_users_list.short_description = 'Aktif Kullanıcılar'
    
    def save_model(self, request, obj, form, change):
        """Marka kaydedilirken kullanıcı sınırını kontrol et"""
        if change and 'paket_turu' in form.changed_data:
            # Paket türü değiştiği için kullanıcı bilgilendirmesi
            old_limit = Brand.objects.get(pk=obj.pk).get_user_limit()
            new_limit = obj.get_user_limit()
            
            if new_limit < old_limit:
                from django.contrib import messages
                active_count = obj.active_users_count()
                if active_count > new_limit:
                    excess_count = active_count - new_limit
                    messages.warning(
                        request, 
                        f"⚠️ Paket düşürülürken {excess_count} kullanıcı pasif hale getirilecek!"
                    )
        
        super().save_model(request, obj, form, change)
        
        # Paket değişikliği sonrası bilgilendirme
        if change and 'paket_turu' in form.changed_data:
            from django.contrib import messages
            messages.success(
                request, 
                f"✅ Paket başarıyla değiştirildi. Kullanıcı durumu: {obj.user_status()}"
            )
    
    def has_delete_permission(self, request, obj=None):
        # Sidrex markasının silinmesini engelle
        if obj and obj.name == 'Sidrex':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(RobotSystemPrompt)
class RobotSystemPromptAdmin(admin.ModelAdmin):
    list_display = ['robot', 'prompt_type', 'is_active', 'priority', 'get_keywords_preview', 'created_at']
    list_filter = ['prompt_type', 'is_active', 'robot', 'created_at']
    search_fields = ['robot__name', 'prompt_content', 'topic_keywords']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'priority']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('robot', 'prompt_type', 'is_active', 'priority')
        }),
        ('Konu Hedefleme', {
            'fields': ('topic_keywords',),
            'description': 'Bu prompt hangi konularda kullanılacak? (virgülle ayırın)'
        }),
        ('Prompt İçeriği', {
            'fields': ('prompt_content',),
            'classes': ['wide']
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_keywords_preview(self, obj):
        """Anahtar kelimelerin önizlemesi"""
        keywords = obj.get_keywords_list()
        if keywords:
            preview = ', '.join(keywords[:3])
            if len(keywords) > 3:
                preview += f" (+{len(keywords)-3})"
            return preview
        return "Tüm konular"
    get_keywords_preview.short_description = 'Anahtar Kelimeler'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('robot')
