__author__ = 'mark'

from rest_framework import serializers
from convert.models import WorkBook, WorkSheet

class WorkBookSerializer(serializers.Serializer):
    class Meta:
        model = WorkBook

    def create(self, validated_data):
        return WorkBook.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.file_name = validated_data.get('file_name', instance.file_name)
        instance.file_path = validated_data.get('file_path', instance.file_path)
        instance.save
        return instance

class WorkSheetSerializer(serializers.Serializer):
    class Meta:
        model = WorkSheet

    def create(self, validated_data):
        return WorkSheet.objects.create(**validated_data)

    def update(self, instance, validated_data):

