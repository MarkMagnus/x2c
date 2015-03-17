from django.test import TestCase
from convert.models import WorkSheet, WorkBook, convert_xls, convert_xlsx
import os


class XlsxTestCase(TestCase):

    def setUp(self):
        self.workbook = WorkBook.create(open(self.xlsx, 'test.xlsx'))

    def tearDown(self):
        for worksheet in self.worksheets:
            worksheet.delete()
            os.remove(worksheet.sheet_path)

        self.workbook.delete()
        os.remove(self.workbook.file_path)
        os.remove(self.workbook.directory())

    def test_parse_xslx_file(self):
        self.worksheets = convert_xlsx(self.workbook)
        self.assertEqual(1, self.worksheets.__len__())

        worksheet = self.worksheets[0]
        self.assertEqual(worksheet.sheet_name, 'Sheet1', 'first work sheet is ' + worksheet.sheet_name)
        self.assertEqual(worksheet.sheet_path, self.workbook.directory() + '/Sheet1.csv')


class XlsTestCase(TestCase):

    def setUp(self):
        self.workbook = WorkBook.create(open(self.xlsx, 'test.xls'))

    def tearDown(self):
        for worksheet in self.worksheets:
            worksheet.delete()
            os.remove(worksheet.sheet_path)

        self.workbook.delete()
        os.remove(self.workbook.file_path)
        os.remove(self.workbook.directory())

    def test_parse_xsl_file(self):
        self.worksheets = convert_xls(self.workbook)
        self.assertEqual(1, self.worksheets.__len__())

        worksheet = self.worksheets[0]
        self.assertEqual(worksheet.sheet_name, 'Sheet1', 'first work sheet is ' + worksheet.sheet_name)
        self.assertEqual(worksheet.sheet_path, self.workbook.directory() + '/Sheet1.csv')

