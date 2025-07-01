from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages

from profiller.models import Profil, ProfilDurum
# Register your models here.


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_active_status', 'brand', 'brand_user_status', 'bio', 'foto']
    list_filter = ['brand', 'user__is_active']
    search_fields = ['user__username', 'user__email', 'brand__name']
    list_editable = ['brand']
    ordering = ['user__username']
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'brand', 'brand_info_display')
        }),
        ('Profil Bilgileri', {
            'fields': ('bio', 'foto')
        }),
    )
    
    readonly_fields = ['brand_info_display']
    
    def user_active_status(self, obj):
        """Kullanıcının aktif durumunu göster"""
        if obj.user.is_active:
            return "✅ Aktif"
        else:
            return "❌ Pasif"
    user_active_status.short_description = 'Kullanıcı Durumu'
    
    def brand_user_status(self, obj):
        """Markanın kullanıcı durumunu göster"""
        if obj.brand:
            return obj.brand.user_status()
        return "Marka Yok"
    brand_user_status.short_description = 'Marka Durumu'
    
    def brand_info_display(self, obj):
        """Marka bilgilerini detaylı göster"""
        if not obj.brand:
            return "❌ Marka atanmamış"
        
        brand = obj.brand
        info = f"""
        📊 Marka: {brand.name}
        📦 Paket: {brand.get_paket_turu_display()}
        👥 Kullanıcı Limiti: {brand.get_user_limit()}
        🔢 Aktif Kullanıcı: {brand.active_users_count()}
        📈 Durum: {brand.user_status()}
        """
        
        if brand.get_user_limit() == 0:
            info += "\n⚠️ Normal pakette kullanıcı atanamaz!"
        elif not brand.can_add_user() and obj.pk:
            # Mevcut bir profil editleniyorsa ve limit doluysa
            current_brand = Profil.objects.get(pk=obj.pk).brand
            if current_brand != brand:  # Marka değişiyorsa
                info += "\n🔴 Bu markaya yeni kullanıcı atanamaz (limit dolu)!"
        
        return info
    brand_info_display.short_description = 'Marka Bilgileri'
    
    def save_model(self, request, obj, form, change):
        """Profil kaydedilirken kullanıcı sınırını kontrol et"""
        try:
            # Model'in clean metodunu çağır (kullanıcı sınır kontrolü)
            obj.full_clean()
            super().save_model(request, obj, form, change)
            
            if obj.brand:
                messages.success(
                    request, 
                    f"✅ Kullanıcı '{obj.user.username}' başarıyla '{obj.brand.name}' markasına atandı. "
                    f"Marka durumu: {obj.brand.user_status()}"
                )
        except ValidationError as e:
            # Validation hatası varsa kullanıcıya göster
            error_message = str(e.message) if hasattr(e, 'message') else str(e)
            messages.error(request, f"❌ {error_message}")
            
            # Form'u tekrar göster (save işlemini iptal et)
            raise ValidationError(error_message)
    
    def get_form(self, request, obj=None, **kwargs):
        """Form'da marka seçeneklerini filtrele ve yardım metni ekle"""
        form = super().get_form(request, obj, **kwargs)
        
        # Brand field'ına yardım metni ekle
        if 'brand' in form.base_fields:
            help_texts = []
            
            # Mevcut marka durumlarını göster
            from robots.models import Brand
            for brand in Brand.objects.all():
                status_icon = "✅" if brand.can_add_user() else "🔴"
                if brand.get_user_limit() == 0:
                    status_icon = "🚫"
                
                help_texts.append(
                    f"{status_icon} {brand.name} ({brand.get_paket_turu_display()}): "
                    f"{brand.active_users_count()}/{brand.get_user_limit()} kullanıcı"
                )
            
            form.base_fields['brand'].help_text = (
                "Kullanıcıyı bir markaya atayın. Marka durumları:\n" + 
                "\n".join(help_texts) + 
                "\n\n🚫 = Kullanıcı atanamaz, 🔴 = Limit dolu, ✅ = Kullanılabilir"
            )
        
        return form


admin.site.register(ProfilDurum)