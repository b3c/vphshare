
from models import AuditLog, Institution, Study, SubscriptionRequest
from django.contrib import admin

admin.site.register(Institution)
admin.site.register(Study)
admin.site.register(SubscriptionRequest)
admin.site.register(AuditLog)
