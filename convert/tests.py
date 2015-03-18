from django.test import TestCase
from convert.models import File, convert_xls_to_csv, convert_xlsx_to_csv, unzip, ZIP, CSV, XLS, XLSX
import os
import shutil


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

