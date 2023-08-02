import openpyxl
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from ..models import User
from .all_service import check_or_create_folder
from ..models import ContactImportFiles
from rest_framework import serializers, exceptions
from django.core.exceptions import ObjectDoesNotExist


def contact_import(data, user):
    pass

def contact_import_run_request_data_validate(data, user):
    # прописать валидацию номеров ячеек
    filename = data.get("filename")
    try:
        obj = ContactImportFiles.objects.get(owner=user, filename=filename)
        row_len = obj.row_len
        param_fields_name = ["id", "name", "surname", "email", "contact_group", "comment"]
        fail_params = []
        is_have_fail_params = False
        for param in param_fields_name:
            request_param = data.get(param)
            if request_param and request_param >= row_len:
                fail_params.append(param)
                is_have_fail_params = True
        if is_have_fail_params:
            raise serializers.ValidationError(
                f"Переданы индексы, которые больше чем длина строки в файле. Поля с ошибкой:{fail_params}. Должны быть индексы до {row_len}")
    except ObjectDoesNotExist:
        raise exceptions.NotFound("Такого файла нет на сервере")
    if not (data.get("phone") or data.get("email")):
        raise serializers.ValidationError("Должен быть хотя бы 1 контакт")


def file_upload_handler(file: InMemoryUploadedFile, user: User):
    start_data = get_start_data_from_imp(file)
    file_dir = f'sources/import_file/{user.username}'
    filename = get_cure_filename(file_dir, file.name)
    check_or_create_folder(file_dir)
    write_received_excel(file_dir, filename, file)
    ContactImportFiles.objects.create(owner=user, filename=filename, row_len=start_data.get("count_elements_in_line"))
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
