import xlsxwriter

from io import BytesIO


class XlsxWrapper:
    output = BytesIO()
    workbook = None
    worksheet = None
    filename = None
    content_disposition = None
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.workbook = xlsxwriter.Workbook(self.output)
        self.content_disposition = 'attachment; filename={}.xlsx'.format(self.filename)

    def create_worksheet(self, name):
        self.worksheet = self.workbook.add_worksheet(name)
        return self.worksheet

    def write(self, row, column, data):
        self.worksheet.write(row, column, data)

    def close(self):
        self.workbook.close()
        self.output.seek(0)

    def read(self):
        return self.output.getvalue()
