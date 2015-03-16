__author__ = 'mark'

from django.test import TestCase
from openpyxl import load_workbook
import os.path

class XlsxTestCase(TestCase):

    def setUp(self):
        self.xlsx = 'test/test.xlsx'
        self.csv = 'test.csv'
        self.assertTrue(os.path.isfile(self.xlsx), self.xlsx + ' should exist')
        self.assertFalse(os.path.isfile(self.csv), self.csv + ' should not yet exist')

    def tearDown(self):
        self.assertTrue(os.path.isfile(self.xlsx), self.xlsx + ' should not be deleted during operation')
        self.assertTrue(os.path.isfile(self.csv), self.csv + ' should be created during operation')

    def test_parse_xslx_file(self):
        wb = load_workbook(filename=self.xlsx)
        sheet_names = wb.get_sheet_names()
        for sheet_name in sheet_names:
            print "reading " + sheet_name
            sheet = wb[sheet_name]
            print sheet["A1"].value
