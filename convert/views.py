from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import get_object_or_404
from convert.models import File, Conversion, FormatNotSupported, convert_to_csv, unzip
from convert.serializers import FileSerializer, ConversionSerializer
from rest_framework import status, views, viewsets, permissions, mixins, generics
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

import os
import logging
import pprint


logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser, MultiPartParser, FormParser)
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):

        uploaded_file = request.FILES['file']
        logger.info('uploaded file ' + uploaded_file.name)

        tmp_file_name = '/tmp/'+uploaded_file.name
        with open(tmp_file_name, 'wb+') as t:
            for chunk in uploaded_file.chunks():
                t.write(chunk)

        logger.info('tmp file written ' + tmp_file_name)

        try:
            file_record = File.create_from_file(open(tmp_file_name), uploaded_file.name)
            pp.pprint(file_record)

            serializer = FileSerializer(file_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class FileViewSet(viewsets.ModelViewSet):

    queryset = File.objects.all()
    serializer_class = FileSerializer

    def destroy(self, request, *args, **kwargs):
        file_record = self.get_object()
        file_record.cascade_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'])
    def to_csv(self, request, pk=None):
        queryset = File.objects.all()
        file_record = get_object_or_404(queryset, pk=pk)
        try:
            files = convert_to_csv(file_record)
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(methods=['get'])
    def unzip(self, request, pk=None):
        queryset = File.objects.all()
        file_record = get_object_or_404(queryset, pk=pk)
        try:
            files = unzip(file_record)
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(methods=['get'])
    def download(self, request, pk=None):
        queryset = File.objects.all()
        file_record = get_object_or_404(queryset, pk=pk)
        response = StreamingHttpResponse(FileWrapper(open(file_record.file_path), 8192), content_type="text/csv")
        response['Content-Length'] = os.path.getsize(file_record.file_path)
        response['Content-Disposition'] = "attachment; filename=%s" % file_record.file_name
        return response


class ConversionViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Conversion.objects.all()
    serializer_class = ConversionSerializer


