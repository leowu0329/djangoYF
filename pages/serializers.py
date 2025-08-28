from rest_framework import serializers
from .models import OfficialDocuments

class OfficialDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialDocuments
        fields = '__all__'
