from cool_sender.celery import app
from .services.whats_app_utils import login_and_set_result, check_wa_run
from .models import User, SenderPhoneNumber


@app.task
def wa_login_task(wa_id):
    check_phone_obj = SenderPhoneNumber.objects.get(id=wa_id)
    login_and_set_result(check_phone_obj)


@app.task
def wa_login_check_task(wa_id):
    check_wa_run(wa_id)
