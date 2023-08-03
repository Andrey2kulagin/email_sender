import openpyxl
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from ..models import User, RecipientContact, ContactGroup
from .all_service import check_or_create_folder
from ..models import ContactImportFiles
from rest_framework import serializers, exceptions
from django.core.exceptions import ObjectDoesNotExist
import copy
from .contact_service import email_validate, phone_validate


def contact_import(validate_data: dict, user: User):
    filename = validate_data.get("filename")
    if filename:
        error_rows = []
        mask = copy.deepcopy(validate_data)
        del mask["filename"]
        workbook = openpyxl.load_workbook(f"sources/{user}/{filename}")
        sheet = workbook.active
        for row in sheet.iter_rows(values_only=True):
            import_contact_row_handler(row, mask, user, error_rows)
    # обработка самого файла построчно

    # валидация строки
    # запись контакта в БД
    # запись данных об ошибках в файл
    pass


def import_contact_row_handler(row: list[str], mask: dict[str: int], user: User, error_rows: list[list[str]]):
    cure_values = get_cure_value(row, mask)
    if cure_values.get("id"):
        # обрабатываем update
        validate_result = import_contact_update_validate(cure_values, user)
        import_update(row, validate_result, user, error_rows)
    else:
        validate_result = import_contact_create_validate(cure_values, user)


def import_update(cure_values: list[str], validate_result: dict, user: User, error_rows: list[list[str]]):
    status = validate_result.get("status", "")
    errors = validate_result.get("errors")
    comment = validate_result.get("comment")
    if status in ["OK", "PF"]:


    elif status == "FF":
        pass


def save_contact(user, cure_values):
    contact = RecipientContact()
    contact.owner = user
    for key in cure_values:
        value = cure_values.get(key)
        if value:
            setattr(contact, key, value)
    contact.save()


def import_contact_update_validate(cure_values, user):
    # здесь будем возвращать строку из 3 статусов - OK, FF(full fail), PF(partial fail)
    # если что-то хотя бы 1 параметр валиден, а остальные - нет, то возвращаем PF(обновляем только то, что валидно)
    errors = {}
    contact_id = cure_values.get("id", "")
    contact_objs = RecipientContact.objects.filter(owner=user, id=contact_id)
    if len(contact_objs) != 0:
        errors["id"] = "У вас нет контакта с таким id"
        return {"status": "FF", "errors": errors, "comment": None}
    add_email_phone_errors(cure_values, user, errors)
    if len(errors) == 0:
        return {"status": "OK", "errors": None, "comment": None}
    return {"status": "PF", "errors": errors, "comment": None}


def add_email_phone_errors(cure_values, user, errors):
    try:
        phone_validate(cure_values, "Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7",
                       user)
    except serializers.ValidationError as e:
        errors["phone"] = e.__str__()
    try:
        email_validate(cure_values, "Введите правильный email", user)
    except serializers.ValidationError as e:
        errors["email"] = e.__str__()


def import_contact_create_validate(cure_values, user):
    # здесь будем возвращать строку из 3 статусов - OK, FF(full fail), PF(partial fail)
    # Классическая ситуация с валидацией. Должен быть хотя бы 1 рабочий контакт
    errors = {}
    add_email_phone_errors(cure_values, user, errors)
    input_phone = cure_values.get("phone")
    phone_errors = errors.get("phone")
    input_email = cure_values.get("email")
    email_errors = errors.get("email")
    if input_phone is None and email_errors:
        return {"status": "FF", "errors": errors, "comment": "Добавьте хотя бы 1 валидный контакт", }
    if input_email is None and phone_errors:
        return {"status": "FF", "errors": errors, "comment": "Добавьте хотя бы 1 валидный контакт", }
    if phone_errors and email_errors:
        return {"status": "FF", "errors": errors, "comment": "Добавьте хотя бы 1 валидный контакт", }
    add_groups_errors(cure_values, user, errors)
    if len(errors) == 0:
        return {"status": "OK", "errors": None, "comment": None}
    else:
        return {"status": "PF", "errors": errors, "comment": None}


def add_groups_errors(cure_values, user, errors):
    groups_str = cure_values.get("contact_group")
    if groups_str and groups_str != "DELETE_ALL":
        groups = groups_str.split(";")
        for group in groups:
            try:
                ContactGroup.objects.get(user=user, title=group.strip())
            except ObjectDoesNotExist:
                errors[f"group {group}"] = "У вас нет такой группы"


def get_cure_value(row: list[str], mask: dict[str: int]):
    cure_values = {}
    for key in mask:
        index = mask[key]
        try:
            cure_values[key] = row[index]
        except IndexError:
            cure_values[key] = None
    return cure_values


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


def file_upload_handler(file: InMemoryUploadedFile, user: User, is_contains_headers: bool):
    start_data = get_start_data_from_imp(file)
    file_dir = f'sources/import_file/{user.username}'
    filename = get_cure_filename(file_dir, file.name)
    check_or_create_folder(file_dir)
    write_received_excel(file_dir, filename, file)
    ContactImportFiles.objects.create(owner=user, filename=filename, row_len=start_data.get("count_elements_in_line"),
                                      is_contains_headers=is_contains_headers)
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
