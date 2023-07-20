def email_check_null(instance, validated_data):
    if "contact" in validated_data:
        instance.is_checked_pass = None
        instance.checked_date = None

