import xlwt
import datetime
from django.http import HttpResponse


def FormatoExcel(columns, obj, name_doc, name_sheet):
    response = HttpResponse()
    response["content_type"] = "application/vnd.ms-excel"
    response["Content-Disposition"] = f'attachment; filename="{name_doc}.xls"'

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet(name_sheet)
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = columns

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = obj

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            if isinstance(row[col_num], datetime.date):
                date = f"{row[col_num].day}/{row[col_num].month}/{row[col_num].year}"
                ws.write(row_num, col_num, date, font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response
