from django.contrib import admin

from models import AuditLog, Institution, Study, SubscriptionRequest, VPHShareSmartGroup
from forms import VPHShareSmartGroupAdmin, InstitutionAdmin, StudyAdmin


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(VPHShareSmartGroup, VPHShareSmartGroupAdmin)
admin.site.register(SubscriptionRequest)
admin.site.register(AuditLog)
