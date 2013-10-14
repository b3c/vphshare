from django.contrib import admin

from models import UserProfile, roles, UserAgreement

admin.site.register(UserProfile)
admin.site.register(roles)
admin.site.register(UserAgreement)