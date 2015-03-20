__author__ = 'mark'

from rest_framework import serializers
from convert.models import File, Conversion


class FileSerializer(serializers.HyperlinkedModelSerializer):

    # produced_by_conversion = serializers.HyperlinkedRelatedField(
    #     view_name='conversion-detail',
    #     queryset=Conversion.objects.all()
    # )

    class Meta:
        model = File
        fields = ('id', 'file_name', 'file_path', 'format', 'created')


class ConversionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Conversion
        fields = ('id', 'from_file', 'to_file', 'created', 'success')


