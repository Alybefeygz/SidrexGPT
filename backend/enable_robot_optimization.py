#!/usr/bin/env python3
"""
Script to enable optimization mode for all robots
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from robots.models import Robot

def enable_optimization_for_all_robots():
    print("🚀 Robot Optimizasyon Modları Açılıyor...")
    print("=" * 50)
    
    # Tüm robotları al
    robots = Robot.objects.all()
    
    if not robots.exists():
        print("❌ Hiç robot bulunamadı!")
        return
    
    print(f"📊 Toplam {robots.count()} robot bulundu")
    print()
    
    updated_count = 0
    
    for robot in robots:
        print(f"🤖 Robot: {robot.name} ({robot.slug})")
        print(f"   📊 Mevcut Optimizasyon: {'AÇIK' if robot.optimizasyon_modu else 'KAPALI'}")
        
        if not robot.optimizasyon_modu:
            robot.optimizasyon_modu = True
            robot.save(update_fields=['optimizasyon_modu'])
            print(f"   ✅ Optimizasyon AÇILDI!")
            updated_count += 1
        else:
            print(f"   ℹ️  Zaten açıktı")
        print()
    
    print("=" * 50)
    print(f"🎉 İşlem Tamamlandı!")
    print(f"✅ {updated_count} robot için optimizasyon açıldı")
    print(f"📊 Toplam {robots.count()} robot kontrol edildi")
    print()
    
    # Son durumu göster
    print("📋 GÜNCEL DURUM:")
    for robot in Robot.objects.all():
        status = "🟢 AÇIK" if robot.optimizasyon_modu else "🔴 KAPALI"
        print(f"   {robot.name}: {status}")

if __name__ == "__main__":
    enable_optimization_for_all_robots() 