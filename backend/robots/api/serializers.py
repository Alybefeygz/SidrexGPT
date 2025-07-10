from rest_framework import serializers
from robots.models import Robot, RobotPDF, Brand
from robots.utils import upload_pdf_to_drive


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
    pdf_file = serializers.FileField(required=False, write_only=True, help_text='PDF dosyası yüklemek için kullanılır.')
    pdf_dosyasi = serializers.CharField(required=False, help_text='Google Drive linki olarak da gönderilebilir.')
    
    class Meta:
        model = RobotPDF
        fields = ['robot_id', 'pdf_file', 'pdf_dosyasi', 'dosya_adi', 'aciklama', 'is_active', 'pdf_type']
        extra_kwargs = {
            'pdf_file': {
                'required': False,
                'help_text': 'Yeni PDF dosyası yüklemek için.'
            },
            'pdf_dosyasi': {
                'required': False,
                'help_text': 'Google Drive linki olarak da gönderilebilir.'
            }
        }
    
    def validate(self, data):
        if not data.get('pdf_file') and not data.get('pdf_dosyasi'):
            raise serializers.ValidationError({'pdf_file': 'Yeni PDF oluştururken dosya yükleyin veya Google Drive linki girin.'})
        return data
    
    def create(self, validated_data):
        robot_id = validated_data.pop('robot_id')
        robot = Robot.objects.get(id=robot_id)
        pdf_file = validated_data.pop('pdf_file', None)
        pdf_link = validated_data.pop('pdf_dosyasi', None)
        dosya_adi = validated_data.get('dosya_adi')
        # Eğer dosya upload edildiyse Google Drive'a yükle
        if pdf_file:
            link = upload_pdf_to_drive(pdf_file, dosya_adi or pdf_file.name)
        elif pdf_link:
            link = pdf_link
        else:
            raise serializers.ValidationError({'pdf_file': 'PDF dosyası veya linki zorunludur.'})
        validated_data['pdf_dosyasi'] = link
        validated_data['robot'] = robot
        return super().create(validated_data)


class ChatMessageSerializer(serializers.Serializer):
    """Chat mesajı için serializer"""
    message = serializers.CharField(required=True, max_length=1000)
    
    def validate_message(self, value):
        """Mesaj validasyonu"""
        if not value.strip():
            raise serializers.ValidationError("Mesaj boş olamaz.")
        return value.strip() 