from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RecipientContact, UserLetterText, UserSenders, ContactGroup, SenderPhoneNumber, SenderEmail, \
    ContactImportFiles, UserSendersContactStatistic, AdminData


class MyUserAdmin(UserAdmin):
    model = User
    list_display = (
        'username', 'email', "phone", "field_of_activity", "subscription", "activation_date", "subscription_days",
        "end_of_subscription")

    add_fieldsets = (*UserAdmin.add_fieldsets,
                     (
                         None,
                         {
                             'fields': (
                                 "subscription", "activation_date",
                                 "subscription_days",
                                 "end_of_subscription")}
                     ),
                     )

    fieldsets = ((*UserAdmin.fieldsets[0],),
                 (
                     None,
                     {
                         'fields': (
                             "subscription", "activation_date",
                             "subscription_days",
                             "end_of_subscription")}
                 ),
                 (*UserAdmin.fieldsets[3],)
                 )


admin.site.register(User, MyUserAdmin)
admin.site.register(RecipientContact)
admin.site.register(UserLetterText)
admin.site.register(UserSenders)
admin.site.register(ContactGroup)
admin.site.register(SenderPhoneNumber)
admin.site.register(SenderEmail)
admin.site.register(ContactImportFiles)
admin.site.register(UserSendersContactStatistic)
admin.site.register(AdminData)
