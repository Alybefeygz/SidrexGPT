from rest_framework import serializers
from medya.models import Medya, StatikVarlik

class MedyaSerializer(serializers.ModelSerializer):
    # Model'deki property'yi kullanarak public URL'i okuma için ekliyoruz.
    public_url = serializers.ReadOnlyField()
    
    # Yükleme için geçici bir alan oluşturuyoruz. Bu alan veritabanına yazılmayacak.
    dosya = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Medya
        fields = ['id', 'adi', 'public_url', 'yuklenme_tarihi', 'dosya']

    def create(self, validated_data):
        # Gelen dosyayı model instance'ına `dosya_gecici` olarak ekliyoruz.
        # Modelin save metodu gerisini halledecek.
        dosya = validated_data.pop('dosya')
        instance = super().create(validated_data)
        instance.dosya_gecici = dosya
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        if 'dosya' in validated_data:
            dosya = validated_data.pop('dosya')
            instance.dosya_gecici = dosya
        
        return super().update(instance, validated_data)


class StatikVarlikSerializer(serializers.ModelSerializer):
    public_url = serializers.ReadOnlyField()
    
    class Meta:
        model = StatikVarlik
        fields = ['anahtar', 'public_url', 'aciklama'] 