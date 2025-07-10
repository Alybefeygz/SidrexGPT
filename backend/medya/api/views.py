from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from medya.models import Medya, StatikVarlik
from .serializers import MedyaSerializer, StatikVarlikSerializer

class MedyaViewSet(viewsets.ModelViewSet):
    queryset = Medya.objects.all()
    serializer_class = MedyaSerializer

# Tüm statik varlıkları bir sözlük olarak döndüren view
class StatikVarliklarView(views.APIView):
    permission_classes = [AllowAny]  # Herkes erişebilir
    
    def get(self, request, *args, **kwargs):
        varliklar = StatikVarlik.objects.all()
        # Veriyi { anahtar: public_url } formatında bir sözlüğe çeviriyoruz
        data = {varlik.anahtar: varlik.public_url for varlik in varliklar}
        return Response(data) 