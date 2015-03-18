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
CSV = 'csv'
ZIP = 'zip'
ANY = 'any'
FORMAT_CHOICES = ((XLS, XLS), (XLSX, XLSX), (CSV, CSV), (ZIP, ZIP), (ANY, ANY))


class File(models.Model):
    file_name = models.CharField(max_length=200, default='')
    file_path = models.TextField(default='')
    format = models.CharField(max_length=4, default=XLS, choices=FORMAT_CHOICES)
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())

    def directory(self):
        return self.file_name.replace(self.file_name, '')

    @classmethod
    def extract_format(cls, file_name):
        if file_name.lower().endswith('.xls'):
            return XLS
        elif file_name.lower().endswith('.xlsx'):
            return XLSX
        elif file_name.lower().endswith('.csv'):
            return CSV
        else:
            raise FormatNotSupported(file_name + ' is invalid type')

    @classmethod
    def create(cls, file_object, file_name):

        file_path = get_new_path(file_name)
        shutil.move(file_object, file_path)
        file_format = cls.extract_format(file_name)

        return cls.create(file_name, file_path, file_format)

    @classmethod
    def create(cls, file_name, file_path, file_format):

        f = cls(file_name=file_name, file_path=file_path, format=file_format)
        f.save()
        return f


class Conversion(models.Model):
    from_file = models.ForeignKey(File)
    to_file = models.OneToOneField(File, related_name='produced')
    success = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())

    @classmethod
    def create(cls, from_file, to_file):
        c = cls(from_file=from_file, to_file=to_file, success=False)
        c.save()
        return c


class FormatNotSupported(Exception):
    def __init__(self, message):
        self.message = message


import xlrd
from openpyxl import load_workbook
import csv
import zipfile


def unzip(zip):

    if zip.format != ZIP:
        raise FormatNotSupported('unzip functionality for ' + zip.file_name + ' not supported')

    f = open(zip.file_path, 'rb')
    z = zipfile.ZipFile(f)
    unzippered = []
    for name in z.namelist():
        file_name = name
        file_path = zip.directory() + name
        z.extract(name, file_path)
        unzipped = File.create(file_name, file_path, File.extract_format(file_name))
        Conversion.create(zip, unzipped)
        unzippered << unzipped
    f.close()
    return unzippered


def convert_xls_to_csv(workbook):
    wb = xlrd.open_workbook(workbook.file_path)
    worksheets = []
    for sheet_name in wb.sheet_names():

        print "processing " + sheet_name
        file_name = sheet_name + '.' + CSV
        file_path = workbook.directory() + file_name
        file_format = CSV
        worksheet = File.create(file_name, file_path, file_format)
        conversion = Conversion.create(workbook, worksheet)

        try:
            os.remove(worksheet.file_path)
        except OSError:
            pass

        sheet = wb.sheet_by_name(sheet_name)
        number_of_rows = sheet.nrows - 1
        number_of_columns = sheet.ncols - 1
        current_row = -1

        with open(worksheet.file_path, 'w', newline='') as fp:
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

        conversion.success = True
        conversion.save()

        worksheets << worksheet

    return worksheets


def convert_xlsx_to_csv(workbook):
    wb = load_workbook(workbook.file_path)
    sheet_names = wb.get_sheet_names()
    worksheets = []
    for sheet_name in sheet_names:

        print "processing " + sheet_name
        file_name = sheet_name + '.' + CSV
        file_path = workbook.directory() + file_name
        file_format = CSV
        worksheet = File.create(file_name, file_path, file_format)
        conversion = Conversion.create(workbook, worksheet)

        try:
            os.remove(worksheet.sheet_path)
        except OSError:
            pass

        sheet = wb[sheet_name]
        with open(worksheet.file_path, 'w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in sheet.rows:
                line = []
                for cell in row:
                    if cell.value is not None:
                        line << cell.value
                writer.writerow(line)

        conversion.success = True
        conversion.save()

        worksheets << worksheet

    return worksheets


def convert_to_csv(file_record):
    if file_record.format == XLS:
        return convert_xls_to_csv(file_record)
    elif file_record.format == XLSX:
        return convert_xlsx_to_csv(file_record)
    else:
        raise FormatNotSupported('convert to csv functionality for ' + file_record.file_name + ' not supported')
