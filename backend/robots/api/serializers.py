from rest_framework import serializers
from robots.models import Robot, RobotPDF, Brand


class RobotPDFSerializer(serializers.ModelSerializer):
    dosya_boyutu = serializers.ReadOnlyField()
    robot = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = RobotPDF
        fields = [
            'id', 'pdf_dosyasi', 'dosya_adi', 'aciklama', 'is_active', 
            'pdf_type', 'has_rules', 'has_role', 'has_info', 'has_declaration', 'yukleme_zamani', 'dosya_boyutu', 'robot'
        ]
        read_only_fields = ['yukleme_zamani', 'dosya_boyutu', 'has_rules', 'has_role', 'has_info', 'has_declaration']


class RobotSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    pdf_dosyalari = RobotPDFSerializer(many=True, read_only=True)
    aktif_pdf_dosyalari = serializers.SerializerMethodField()
    pdf_sayisi = serializers.ReadOnlyField()
    aktif_pdf_sayisi = serializers.ReadOnlyField()
    slug = serializers.SerializerMethodField()
    brand_id = serializers.PrimaryKeyRelatedField(source='brand', read_only=True)
    
    class Meta:
        model = Robot
        fields = [
            'id', 'name', 'product_name', 'brand', 'brand_id', 'brand_name', 'slug', 'yaratilma_zamani', 'guncellenme_zamani', 'pdf_dosyalari', 'pdf_sayisi', 'aktif_pdf_sayisi', 'aktif_pdf_dosyalari'
        ]
        read_only_fields = ['slug', 'yaratilma_zamani', 'guncellenme_zamani', 'brand_name']
    
    def get_slug(self, obj):
        return obj.get_slug()
    
    def get_aktif_pdf_dosyalari(self, obj):
        """Aktif PDF dosyalarını serialize et"""
        aktif_pdfs = obj.pdf_dosyalari.filter(is_active=True)
        return RobotPDFSerializer(aktif_pdfs, many=True).data


class RobotPDFCreateSerializer(serializers.ModelSerializer):
    robot_id = serializers.IntegerField()
    pdf_dosyasi = serializers.FileField(required=False)
    
    class Meta:
        model = RobotPDF
        fields = ['robot_id', 'pdf_dosyasi', 'dosya_adi', 'aciklama', 'is_active', 'pdf_type']
        extra_kwargs = {
            'pdf_dosyasi': {
                'required': False,
                'help_text': 'Mevcut PDF dosyasını değiştirmek için yeni dosya seçin. Boş bırakırsanız mevcut dosya korunur.'
            }
        }
    
    def validate_robot_id(self, value):
        try:
            Robot.objects.get(id=value)
            return value
        except Robot.DoesNotExist:
            raise serializers.ValidationError(f"Robot ID {value} bulunamadı.")
    
    def validate(self, data):
        """Genel validation - create vs update için farklı kurallar"""
        # Update işleminde PDF dosyası opsiyonel
        if self.instance:  # Update işlemi
            return data
        
        # Create işleminde PDF dosyası zorunlu
        if not data.get('pdf_dosyasi'):
            raise serializers.ValidationError({'pdf_dosyasi': 'Yeni PDF oluştururken dosya zorunludur.'})
            
        return data
    
    def to_representation(self, instance):
        """Instance'ı serialize ederken robot_id ve PDF bilgilerini düzgün döndür"""
        representation = super().to_representation(instance)
        
        # Robot ID'yi ekle
        if hasattr(instance, 'robot') and instance.robot:
            representation['robot_id'] = instance.robot.id
        
        # PDF dosyası varsa URL'ini ekle
        if hasattr(instance, 'pdf_dosyasi') and instance.pdf_dosyasi:
            request = self.context.get('request')
            if request:
                representation['pdf_dosyasi'] = request.build_absolute_uri(instance.pdf_dosyasi.url)
            else:
                representation['pdf_dosyasi'] = instance.pdf_dosyasi.url
                
        return representation
    
    def create(self, validated_data):
        robot_id = validated_data.pop('robot_id')
        robot = Robot.objects.get(id=robot_id)
        validated_data['robot'] = robot
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Debug için log
        print(f"UPDATE PDF - Instance ID: {instance.id}, Validated Data: {validated_data}")
        
        robot_id = validated_data.pop('robot_id', None)
        if robot_id:
            try:
                robot = Robot.objects.get(id=robot_id)
                validated_data['robot'] = robot
                print(f"Robot ID {robot_id} bulundu: {robot.name}")
            except Robot.DoesNotExist:
                print(f"Robot ID {robot_id} bulunamadı!")
                raise serializers.ValidationError(f"Robot ID {robot_id} bulunamadı.")
        
        # PDF dosyası gönderilmediyse mevcut dosyayı koru
        pdf_dosyasi = validated_data.get('pdf_dosyasi', None)
        if pdf_dosyasi is None:
            validated_data.pop('pdf_dosyasi', None)
            
        # PDF türü değiştiyse ilgili alanları güncelle
        if 'pdf_type' in validated_data:
            pdf_type = validated_data['pdf_type']
            validated_data.update({
                'has_rules': pdf_type == 'kural',
                'has_role': pdf_type == 'rol',
                'has_info': pdf_type == 'bilgi',
                'has_declaration': pdf_type == 'beyan'
            })
            
        print(f"Final validated data: {validated_data}")
        return super().update(instance, validated_data)


class ChatMessageSerializer(serializers.Serializer):
    """Chat mesajı için serializer"""
    message = serializers.CharField(required=True, max_length=1000)
    
    def validate_message(self, value):
        """Mesaj validasyonu"""
        if not value.strip():
            raise serializers.ValidationError("Mesaj boş olamaz.")
        return value.strip() 