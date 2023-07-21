def email_check_null(instance, validated_data):
    if "contact" in validated_data or "password" in validated_data:
        instance.is_check_pass = None
        instance.checked_date = None
        instance.save()


def whatsapp_check_null(instance, validated_data):
    if "contact" in validated_data:
        instance.is_login = False
        instance.login_date = None
        instance.save()
