import openpyxl
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from ..models import User
from .all_service import check_or_create_folder
from ..models import ContactImportFiles


def file_upload_handler(file: InMemoryUploadedFile, user: User):
    start_data = get_start_data_from_imp(file)
    file_dir = f'import_file/{user.username}'
    filename = get_cure_filename(file_dir, file.name)
    check_or_create_folder(file_dir)
    write_received_excel(file_dir, filename, file)
    ContactImportFiles.objects.create(owner=user, filename=filename)
    output_data = {
        "file_name_on_serv": filename,
        "count": start_data.get("count"),
        "count_elements_in_line": start_data.get("count_elements_in_line"),
        "results": start_data.get("results")
    }
    return Response(data=output_data, status=200)


def write_received_excel(file_dir, filename, file):
    with open(f"{file_dir}/{filename}", 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def get_cure_filename(filepath, init_filename):
    count = 1
    while os.path.exists(f"{filepath}/{init_filename}"):
        init_filename = init_filename.replace(".", f"{count}.")
        count += 1
    return init_filename


def is_file_in_dir(filepath):
    return os.path.exists(filepath)


def get_start_data_from_imp(file: InMemoryUploadedFile):
    workbook = openpyxl.load_workbook(file)
    # Получаем название всех листов в файле
    sheet_names = workbook.sheetnames
    # Выбираем первый лист
    sheet = workbook[sheet_names[0]]
    results = []
    sheet_len = 0
    max_item_length = 20
    for row in sheet:
        row_len = len(row)
        if row_len < max_item_length:
            max_item_length = row_len
        if sheet_len >= 10:
            break
        sheet_len += 1
        results.append(get_new_row(row[:20]))
    return {
        "count": sheet_len,
        "count_elements_in_line": max_item_length,
        "results": results
    }


def get_new_row(row):
    result_row = []
    for i in row:
        if i.value:
            result_row.append(str(i.value))
        else:
            result_row.append("")
    return result_row
