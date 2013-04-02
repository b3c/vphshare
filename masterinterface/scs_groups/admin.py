
from models import AuditLog, Institution, Study, SubscriptionRequest, VPHShareSmartGroup
from django.contrib import admin

admin.site.register(Institution)
admin.site.register(Study)
admin.site.register(VPHShareSmartGroup)
admin.site.register(SubscriptionRequest)
admin.site.register(AuditLog)
