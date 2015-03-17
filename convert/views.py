import os
from django.http import StreamingHttpResponse, HttpResponse
from django.core.servers.basehttp import FileWrapper
from convert.models import WorkBook, WorkSheet, FormatNotSupported, convert
from convert.serializers import WorkBookSerializers, WookSheetSerializer
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.decorators import api_view, parser_classes


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename):

        try:
            workbook = WorkBook.create(request.data['file'], filename)
            convert(workbook)
            serializer = WorkBookSerializers(workbook)
            return Response(serializer.data)
        except FormatNotSupported:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET', 'POST'])
@parser_classes((JSONParser,FileUploadParser ))
def workbooks_list(request):

    if request.method == 'GET':
        workbooks = WorkBook.objects.all()
        serializer = WorkBookSerializer(workbooks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = FileUploadParser.parse(request)
        serializer = WorkBookSerializers(workbook, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@parser_classes((JSONParser, ))
def workbook_detail(request, pk):
    """
    List all code snippets, or create a new snippet.
    """
    try:
        workbook = WorkBook.objects.get(pk=pk)
    except WorkBook.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WorkBookSerializers(workbook)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        workbook.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def worksheet_detail(request, pk):

    try:
        worksheet = WorkSheet.objects.get(pk=pk)
    except WorkSheet.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        response = StreamingHttpResponse(FileWrapper(open(worksheet.sheet_path), 8192), content_type="text/csv")
        response['Content-Length'] = os.path.getsize(worksheet.sheet_path)
        response['Content-Disposition'] = "attachment; filename=%s" % worksheet.sheet_name
        return response

def index(request):
    return HttpResponse("Hi Converter")


