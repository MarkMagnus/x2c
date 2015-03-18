__author__ = 'mark'

from rest_framework import serializers
from convert.models import File, Conversion


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('file_name', 'file_path', 'format', 'created')


class ConversionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Conversion
        fields = ('from_file', 'to_file', 'created')


