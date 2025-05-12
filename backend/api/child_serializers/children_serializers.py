from rest_framework import serializers
from api.models.children_model import Language, Concern

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'languages']
        extra_kwargs = {"id": {"read_only": True}}

class ChildConcernSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concern
        fields = ['id', 'title', 'description']
        extra_kwargs = {"id": {"read_only": True}}