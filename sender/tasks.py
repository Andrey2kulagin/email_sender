from cool_sender.celery import app
from .services.whats_app_utils import login_and_set_result, check_wa_run
from .services.WA_sender_service import sender_handler
from .models import User, SenderPhoneNumber


@app.task
def wa_login_task(wa_id):
    check_phone_obj = SenderPhoneNumber.objects.get(id=wa_id)
    login_and_set_result(check_phone_obj)


@app.task
def wa_login_check_task(wa_id):
    check_wa_run(wa_id)


@app.task
def sender_run(validated_data, user_id, cure_sender_obj_id):
    user = User.objects.get(id=user_id)
    sender_handler(validated_data, user, cure_sender_obj_id)
