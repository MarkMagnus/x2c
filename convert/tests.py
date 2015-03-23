import django
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from convert.models import File, convert_xls_to_csv, convert_xlsx_to_csv, unzip, ZIP, XLS, XLSX

import os
import io
import shutil
import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE')
django.setup()


class FileUploadAndConversionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user('root', 'root@impactdata.com.au', 'elvis')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client

    def tearDown(self):
        self.user.delete()

    def test_upload(self):

        pp = pprint.PrettyPrinter(indent=4)

        original = os.path.dirname(os.path.realpath(__file__)) + '/samples/test.zip'
        zip_file = SimpleUploadedFile("test.zip", open(original, 'rb').read(), content_type="application/zip")
        response = self.client.post('/convert/upload', {'file': zip_file})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        pp.pprint(response.data)

        file_id = int(response.data['id'])
        self.assertTrue(0 < file_id)
        self.assertEqual('test.zip', response.data['file_name'])
        self.assertEqual('zip', response.data['format'])
        self.assertTrue('/test.zip' in response.data['file_path'])
        self.assertTrue('/tmp/' in response.data['file_path'])

        response = self.client.get('/convert/file')
        pp.pprint(response.data)
        files = response.data
        self.assertEqual(1, len(files))
        file = files[0]
        self.assertEqual(file_id, file['id'])
        self.assertEqual('test.zip', file['file_name'])
        self.assertEqual('zip', file['format'])
        self.assertTrue(str(file['file_path']).endswith(u'test.zip'))
        self.assertTrue('tmp' in file['file_path'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/convert/file/' + str(file_id))
        pp.pprint(response.content)
        self.assertEqual(1, response.data['id'])
        self.assertEqual('test.zip', response.data['file_name'])
        self.assertEqual('zip', response.data['format'])
        self.assertTrue('/test.zip' in response.data['file_path'])
        self.assertTrue('/tmp/' in response.data['file_path'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/convert/file/' + str(file_id) + '/unzip')
        pp.pprint(response.content)
        files = response.data
        self.assertEqual(2, len(files))
        file = files[0]
        self.assertEqual('GDrive.xlsx', file['file_name'])
        self.assertEqual('xlsx', file['format'])
        self.assertTrue('/GDrive.xlsx' in file['file_path'])
        self.assertTrue('/tmp/' in file['file_path'])
        file = files[1]
        self.assertEqual('MSSQL_IOPS.xls', file['file_name'])
        self.assertEqual('xls', file['format'])
        self.assertTrue('/MSSQL_IOPS.xls' in file['file_path'])
        self.assertTrue('/tmp/' in file['file_path'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get('/convert/conversion')
        pp.pprint(response.content)
        self.assertEqual(2, len(response.data))
        self.assertTrue(response.data[0]['success'])
        self.assertTrue(response.data[1]['success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/convert/conversion/1')
        pp.pprint(response.content)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/convert/conversion?from_file_id=' + str(file_id))
        pp.pprint(response.content)
        self.assertEqual(2, len(response.data))
        file = files[0]
        self.assertEqual('GDrive.xlsx', file['file_name'])
        self.assertEqual('xlsx', file['format'])
        self.assertTrue('/GDrive.xlsx' in file['file_path'])
        self.assertTrue('/tmp/' in file['file_path'])
        file = files[1]
        self.assertEqual('MSSQL_IOPS.xls', file['file_name'])
        self.assertEqual('xls', file['format'])
        self.assertTrue('/MSSQL_IOPS.xls' in file['file_path'])
        self.assertTrue('/tmp/' in file['file_path'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/convert/file/2/to_csv')
        pp.pprint(response.content)
        self.assertEqual(1, len(response.data))
        self.assertEqual(u'RawData.csv', response.data[0]['file_name'])
        self.assertEqual(u'csv', response.data[0]['format'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get('/convert/file/4/download')
        buff = io.StringIO(u"".join(response.streaming_content))
        csv_file = os.path.dirname(os.path.realpath(__file__)) + '/samples/RawData.csv'
        with open(csv_file, 'wb+') as csv:
            for line in buff.readlines():
                print line
                csv.write(line)

        response = self.client.get('/convert/file/3/to_csv')
        pp.pprint(response.content)
        files = response.data
        self.assertEqual(3, len(response.data))
        file = files[0]
        self.assertEqual('Sheet1.csv', file['file_name'])
        response = self.client.get('/convert/file/5/download')
        buff = io.StringIO(u"".join(response.streaming_content))
        csv_file = os.path.dirname(os.path.realpath(__file__)) + '/samples/Sheet1.csv'
        with open(csv_file, 'wb+') as csv:
            for line in buff.readlines():
                print line
                csv.write(line)

        file = files[1]
        self.assertEqual('Sheet2.csv', file['file_name'])
        response = self.client.get('/convert/file/6/download')
        buff = io.StringIO(u"".join(response.streaming_content))
        csv_file = os.path.dirname(os.path.realpath(__file__)) + '/samples/Sheet2.csv'
        with open(csv_file, 'wb+') as csv:
            for line in buff.readlines():
                print line
                csv.write(line)

        file = files[2]
        self.assertEqual('Sheet3.csv', file['file_name'])
        response = self.client.get('/convert/file/7/download')
        buff = io.StringIO(u"".join(response.streaming_content))
        csv_file = os.path.dirname(os.path.realpath(__file__)) + '/samples/Sheet3.csv'
        with open(csv_file, 'wb+') as csv:
            for line in buff.readlines():
                print line
                csv.write(line)

        response = self.client.delete('/convert/file/3')
        pp.pprint(response.content)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.client.get('/convert/conversion')
        pp.pprint(response.content)
        conversions = response.data
        self.assertEqual(6, len(conversions))

        response = self.client.delete('/convert/conversion/16')
        pp.pprint(response.content)
        self.assertEqual("Method 'DELETE' not allowed.", response.data['detail'])
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

        response = self.client.delete('/convert/file/1')
        pp.pprint(response.content)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.client.get('/convert/file', )
        pp.pprint(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        files = response.data
        for f in files:
            self.assertTrue(f['deleted'])

    def test_list(self):
        response = self.client.get('/convert/file', )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        response = self.client.get('/convert/conversion')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class UnzipTestCase(TestCase):

    def setUp(self):
        original = 'convert/samples/test.zip'
        copy = 'convert/samples/test1.zip'
        shutil.copyfile(original, copy)
        self.from_file = File.create_from_file(open(copy), 'test1.zip')
        self.assertEqual(self.from_file.file_name, 'test1.zip', self.from_file.file_name + ' should be test1.zip')
        self.assertTrue('/tmp' in self.from_file.file_path, self.from_file.file_path + ' should start /tmp')
        self.assertTrue('/test1.zip' in self.from_file.file_path, self.from_file.file_path + ' should end /test1.zip')
        self.assertEqual(self.from_file.format, ZIP, self.from_file.format + ' should be ' + ZIP)
        self.assertTrue('/tmp' in self.from_file.directory(), self.from_file.directory() + ' should start /tmp')
        self.unzippered = []

    def tearDown(self):

        for unzipped in self.unzippered:
            if os.path.isfile(unzipped.file_path):
                os.remove(unzipped.file_path)
            unzipped.delete()

        if self.from_file:
            if os.path.isfile(self.from_file.file_path):
                os.remove(self.from_file.file_path)
            self.from_file.delete()

        shutil.rmtree(self.from_file.directory())

    def test_unzip_file(self):

        self.unzippered = unzip(self.from_file)
        self.assertEqual(2, self.unzippered.__len__())

        x = self.unzippered[0]
        self.assertEqual(x.file_name, 'GDrive.xlsx', x.file_name + ' should be GDrive.xlsx')
        self.assertTrue('/tmp' in x.file_path, '/tmp should be in ' + x.file_path)
        self.assertTrue(self.from_file.directory() in x.file_path, self.from_file.directory() + ' should be in ' + x.file_path)
        self.assertTrue('/GDrive.xlsx' in x.file_path, 'GDrive.xslx should be in ' + x.file_path)
        self.assertEqual(x.format, XLSX, x.format + ' should be ' + XLSX)
        self.assertTrue(os.path.isfile(x.file_path), x.file_path + ' file does not exist')

        x = self.unzippered[1]
        self.assertEqual(x.file_name, 'MSSQL_IOPS.xls', x.file_name + ' should be MSSQL_IOPS.xls')
        self.assertTrue('/tmp' in x.file_path, '/tmp should be in ' + x.file_path)
        self.assertTrue(self.from_file.directory() in x.file_path, self.from_file.directory() + ' should be in ' + x.file_path)
        self.assertTrue('/MSSQL_IOPS.xls' in x.file_path, 'MSSQL_IOPS.xls should be in ' + x.file_path)
        self.assertEqual(x.format, XLS, x.format + ' should be ' + XLS)
        self.assertTrue(os.path.isfile(x.file_path), x.file_path + ' file does not exist')


class XlsxTestCase(TestCase):

    def setUp(self):
        original = 'convert/samples/test.xlsx'
        copy = 'convert/samples/test1.xlsx'
        shutil.copyfile(original, copy)
        self.from_file = File.create_from_file(open(copy), 'test.xlsx')

    def tearDown(self):

        if self.conversion:
            self.conversion.delete()

        if self.from_file:
            self.from_file.delete()
            if os.path.isfile(self.from_file.file_path):
                os.remove(self.from_file.file_path)

        if self.to_file:
            self.to_file.delete()
            if os.path.isfile(self.to_file.file_path):
                os.remove(self.to_file.file_path)

        shutil.rmtree(self.from_file.directory())

    def test_parse_xslx_file(self):

        self.worksheets = convert_xlsx_to_csv(self.from_file)
        self.assertEqual(1, self.worksheets.__len__())

        self.to_file = self.worksheets[0]

        self.assertEqual(self.to_file.file_name, 'Sheet1.csv', 'first work sheet is ' + self.to_file.file_name)
        self.assertEqual(self.to_file.file_path, self.from_file.directory() + 'Sheet1.csv', 'first work sheet path is ' + self.to_file.file_path)
        self.assertTrue(os.path.isfile(self.to_file.file_path), self.to_file.file_path + ' should exist')

        self.conversion = self.to_file.produced_by_conversion
        self.assertEqual(self.to_file.id, self.conversion.to_file_id)
        self.assertEqual(self.from_file.id, self.conversion.from_file_id)
        self.assertTrue(self.conversion.success)


class XlsTestCase(TestCase):

    def setUp(self):
        original = 'convert/samples/test.xls'
        copy = 'convert/samples/test1.xls'
        shutil.copyfile(original, copy)
        self.from_file = File.create_from_file(open(copy), 'test.xls')

    def tearDown(self):

        if self.conversion:
            self.conversion.delete()

        if self.from_file:
            self.from_file.delete()
            if os.path.isfile(self.from_file.file_path):
                os.remove(self.from_file.file_path)

        if self.to_file:
            self.to_file.delete()
            if os.path.isfile(self.to_file.file_path):
                os.remove(self.to_file.file_path)

        shutil.rmtree(self.from_file.directory())

    def test_parse_xsl_file(self):

        self.worksheets = convert_xls_to_csv(self.from_file)
        self.assertEqual(1, self.worksheets.__len__())

        self.to_file = self.worksheets[0]

        self.assertEqual(self.to_file.file_name, 'Sheet1.csv', 'first work sheet is ' + self.to_file.file_name)
        self.assertEqual(self.to_file.file_path, self.from_file.directory() + 'Sheet1.csv', 'first work sheet path is ' + self.to_file.file_path)
        self.assertTrue(os.path.isfile(self.to_file.file_path), self.to_file.file_path + " should exist")

        self.conversion = self.to_file.produced_by_conversion
        self.assertEqual(self.to_file.id, self.conversion.to_file_id)
        self.assertEqual(self.from_file.id, self.conversion.from_file_id)
        self.assertTrue(self.conversion.success)

