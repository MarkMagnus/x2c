from django.db import models
from django.utils import timezone

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
    created = models.DateTimeField(auto_now_add=True, default=timezone.now())
    deleted = models.BooleanField(default=False)

    def directory(self):
        return self.file_path.replace(self.file_name, '')

    def cascade_delete(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            self.deleted = True
            self.save()
            self.try_delete_directory()
        for conversion in Conversion.objects.all().filter(from_file=self):
            if conversion.success:
                conversion.to_file.cascade_delete()

    def try_delete_directory(self):
        if not os.path.isdir(self.directory()):
            return
        files = os.listdir(self.directory())
        if len(files) == 0:
            os.rmdir(self.directory())

    @classmethod
    def extract_format(cls, file_name):
        if file_name.lower().endswith('.' + XLS):
            return XLS
        elif file_name.lower().endswith('.' + XLSX):
            return XLSX
        elif file_name.lower().endswith('.' + CSV):
            return CSV
        elif file_name.lower().endswith('.' + ZIP):
            return ZIP
        else:
            raise FormatNotSupported(file_name + ' is invalid type')

    @classmethod
    def create_from_file(cls, file_object, file_name):

        file_format = cls.extract_format(file_name)  # raises FormatNotSupported error
        file_path = get_new_path(file_name)
        shutil.move(file_object.name, file_path)

        return cls.create(file_name, file_path, file_format)

    @classmethod
    def create(cls, file_name, file_path, file_format):

        f = cls(file_name=file_name, file_path=file_path, format=file_format)
        f.save()
        return f


class Conversion(models.Model):
    from_file = models.ForeignKey(File)
    to_file = models.OneToOneField(File, related_name='produced_by_conversion')
    success = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, default=timezone.now())

    @classmethod
    def create(cls, from_file, to_file):
        c = cls(from_file=from_file, to_file=to_file)
        c.save()
        return c


class FormatNotSupported(Exception):
    def __init__(self, message):
        self.message = message


import xlrd
from openpyxl import load_workbook
import csv
import zipfile


def unzip(zip_record):

    if zip_record.format != ZIP:
        raise FormatNotSupported('unzip functionality for ' + zip_record.file_name + ' not supported')

    f = open(zip_record.file_path, 'rb')

    unzippered = []
    with zipfile.ZipFile(f) as z:
        for info in z.infolist():

            file_name = info.filename
            file_path = zip_record.directory() + info.filename

            unpacked = open(file_path, 'w')
            unpacked.write(z.read(info.filename))
            unpacked.close()

            unzipped = File.create(file_name, file_path, File.extract_format(file_name))
            conversion = Conversion.create(zip_record, unzipped)
            unzippered.append(unzipped)
            conversion.success = True
            conversion.save()

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

        with open(worksheet.file_path, 'w') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while current_row < number_of_rows:
                line = []

                current_row += 1
                current_cell = -1
                while current_cell < number_of_columns:
                    current_cell += 1
                    cell_value = sheet.cell_value(current_row, current_cell)
                    line.append(cell_value)

                writer.writerow(line)

        conversion.success = True
        conversion.save()

        worksheets.append(worksheet)

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
            os.remove(worksheet.file_path)
        except OSError:
            pass

        sheet = wb[sheet_name]
        with open(worksheet.file_path, 'w') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in sheet.rows:
                line = []
                for cell in row:
                    if cell.value is not None:
                        line.append(cell.value)
                writer.writerow(line)

        conversion.success = True
        conversion.save()

        worksheets.append(worksheet)

    return worksheets


def convert_to_csv(file_record):
    if file_record.format == XLS:
        return convert_xls_to_csv(file_record)
    elif file_record.format == XLSX:
        return convert_xlsx_to_csv(file_record)
    else:
        raise FormatNotSupported('convert to csv functionality for ' + file_record.file_name + ' not supported')
