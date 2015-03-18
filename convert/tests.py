from django.test import TestCase
from convert.models import File, convert_xls_to_csv, convert_xlsx_to_csv, unzip
import os


class UnzipTestCase(TestCase):

    def setUp(self):
        self.from_file = File.create(open('convert/samples/test.zip'), 'test.zip')

    def tearDown(self):

        for unzipped in self.unzippered:
            os.remove(unzipped.file_path)
            unzipped.delete()
        self.from_file.delete()
        os.remove(self.from_file.directory())

    def test_unzip_file(self):

        self.unzippered = unzip(self.from_file)
        self.assertEqual(2, self.unzippered.__len__())



class XlsxTestCase(TestCase):

    def setUp(self):
        self.from_file = File.create(open('convert/samples/test.xlsx'), 'test.xlsx')

    def tearDown(self):

        self.conversion.delete()
        self.from_file.delete()
        self.to_file.delete()

        os.remove(self.from_file.file_path)
        if self.to_file:
            os.remove(self.to_file.file_path)
        os.remove(self.from_file.directory())

    def test_parse_xslx_file(self):

        self.worksheets = convert_xlsx_to_csv(self.file)
        self.assertEqual(1, self.worksheets.__len__())

        self.to_file = self.worksheets[0]

        self.assertEqual(self.to_file.file_name, 'Sheet1', 'first work sheet is ' + self.to_file.file_name)
        self.assertEqual(self.to_file.file_path, self.workbook.directory() + '/Sheet1.csv', 'first work sheet path is ' + self.to_file.file_path)

        self.conversion = self.to_file.conversion
        self.assertEqual(self.to_file.id, self.conversion.to_file_id)
        self.assertEqual(self.from_file.id, self.conversion.from_file_id)
        self.assertTrue(self.conversion.success)


class XlsTestCase(TestCase):

    def setUp(self):
        self.workbook = File.create(open('convert/samples/test.xls'), 'test.xls')

    def tearDown(self):
        self.conversion.delete()
        self.from_file.delete()
        self.to_file.delete()

        os.remove(self.from_file.file_path)
        if self.to_file:
            os.remove(self.to_file.file_path)
        os.remove(self.from_file.directory())

    def test_parse_xsl_file(self):

        self.worksheets = convert_xls_to_csv(self.file)
        self.assertEqual(1, self.worksheets.__len__())

        self.to_file = self.worksheets[0]

        self.assertEqual(self.to_file.file_name, 'Sheet1', 'first work sheet is ' + self.to_file.file_name)
        self.assertEqual(self.to_file.file_path, self.workbook.directory() + '/Sheet1.csv', 'first work sheet path is ' + self.to_file.file_path)

        self.conversion = self.to_file.conversion
        self.assertEqual(self.to_file.id, self.conversion.to_file_id)
        self.assertEqual(self.from_file.id, self.conversion.from_file_id)
        self.assertTrue(self.conversion.success)

