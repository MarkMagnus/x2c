import os
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import get_object_or_404
from convert.models import File, Conversion, FormatNotSupported, convert_to_csv, unzip
from convert.serializers import FileSerializer, ConversionSerializer
from rest_framework import status, views, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):

        try:
            file_record = File.create_from_file(request.data['file'], filename)
            serializer = FileSerializer(file_record)
            return Response(serializer.data)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class FileViewSet(viewsets.ModelViewSet):

    queryset = File.objects.all()
    serializer_class = FileSerializer

    @detail_route(method=['get'])
    def to_csv(self, request, pk=None):
        queryset = File.objects.all()
        file_record = get_object_or_404(queryset, pk=pk)
        try:
            files = convert_to_csv(file_record)
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(method=['get'])
    def unzip(self, request, pk=None):
        queryset = File.object.all()
        file_record = get_object_or_404(queryset, pk=pk)
        try:
            files = unzip(file_record)
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(method=['get'])
    def download(self, request, pk=None):
        queryset = File.objects.all()
        file_record = get_object_or_404(queryset, pk=pk)
        response = StreamingHttpResponse(FileWrapper(open(file_record.file_path), 8192), content_type="text/csv")
        response['Content-Length'] = os.path.getsize(file_record.file_path)
        response['Content-Disposition'] = "attachment; filename=%s" % file_record.file_name
        return response


class ConversionViewSet(viewsets.ModelViewSet):

    queryset = Conversion.objects.all()
    serializer_class = ConversionSerializer


