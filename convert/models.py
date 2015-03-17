from django.db import models
import datetime

import string
import random
import shutil
import os


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_new_path(file_name):
    directory = '/tmp/' + id_generator() + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + file_name


XLS = 'xls'
XLSX = 'xlsx'
FORMAT_CHOICES = ((XLS, XLS), (XLSX, XLSX))


class WorkBook(models.Model):
    file_name = models.CharField(max_length=200, default='')
    file_path = models.TextField(default='')
    format = models.CharField(max_length=4, default=XLS, choices=FORMAT_CHOICES)
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())

    def directory(self):
        return self.file_name.replace(self.file_name, '')

    @classmethod
    def create(cls, file_object, file_name):

        file_path = get_new_path(file_name)
        shutil.move(file_object, file_path)

        if file_path.lower().endswith('.xls'):
            file_format = XLS
        elif file_path.lower().endswith('.xlsx'):
            file_format = XLSX
        else:
            raise FormatNotSupported(file_name + ' is invalid type')

        workbook = cls(file_name=file_name, file_path=file_path, format=file_format)
        workbook.save()
        return workbook


class WorkSheet(models.Model):
    work_book = models.ForeignKey(WorkBook)
    sheet_name = models.CharField(default='', max_length=200)
    sheet_path = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())

    @classmethod
    def create(cls, workbook, sheet_name):
        sheet_path = workbook.directory() + sheet_name + '.csv'
        worksheet = cls(workbook=workbook, sheet_name=sheet_name, sheet_path=sheet_path)
        worksheet.save()
        return worksheet


class FormatNotSupported(Exception):
    def __init__(self, message):
        self.message = message


import xlrd
from openpyxl import load_workbook
import csv


def convert_xls(workbook):
    wb = xlrd.open_workbook(workbook.file_path)
    worksheets = []
    for sheet_name in wb.sheet_names():

        print "processing " + sheet_name
        worksheet = WorkSheet.create(workbook, sheet_name)

        try:
            os.remove(worksheet.sheet_path)
        except OSError:
            pass

        sheet = wb.sheet_by_name(sheet_name)
        number_of_rows = sheet.nrows - 1
        number_of_columns = sheet.ncols - 1
        current_row = -1

        with open(worksheet.sheet_path, 'w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while current_row < number_of_rows:
                line = []

                current_row += 1
                current_cell = -1
                while current_cell < number_of_columns:
                    current_cell += 1
                    cell_value = sheet.cell_value(current_row, current_cell)
                    line << cell_value

                writer.writerow(line)

        worksheets << worksheet
    return worksheets

def convert_xlsx(workbook):
    wb = load_workbook(workbook.file_path)
    sheet_names = wb.get_sheet_names()
    worksheets = []
    for sheet_name in sheet_names:

        print "reading " + sheet_name
        worksheet = WorkSheet.create(workbook, sheet_name)

        try:
            os.remove(worksheet.sheet_path)
        except OSError:
            pass

        sheet = wb[sheet_name]
        with open(worksheet.sheet_path, 'w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in sheet.rows:
                line = []
                for cell in row:
                    if cell.value is not None:
                        line << cell.value
                writer.writerow(line)

        worksheets << worksheet

    return worksheets


def convert(workbook):
    if workbook.format == XLS:
        return convert_xls(workbook)
    elif workbook.format == XLSX:
        return convert_xlsx(workbook)
    else:
        raise FormatNotSupported(workbook.format + " not supported")
