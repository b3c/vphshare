from workflows.models import Workflow, State, Transition, WorkflowPermissionRelation, StatePermissionRelation
from permissions.models import Permission, Role
try:
    # Managed Roles

    resource_owner, created = Role.objects.get_or_create(name='Owner')
    resource_manager, created = Role.objects.get_or_create(name='Manager')
    resource_reader, created = Role.objects.get_or_create(name="Reader")
    resource_editor, created = Role.objects.get_or_create(name="Editor")

    # RESOURCE REQUEST WORKFLOW
    ResourceRequestWorkflow, created = Workflow.objects.get_or_create(name="ResourceRequestWorkflow")

    request_pending, created = State.objects.get_or_create(name="Pending", workflow=ResourceRequestWorkflow)
    request_accepted, created = State.objects.get_or_create(name="Accepted", workflow=ResourceRequestWorkflow)
    request_refused, created = State.objects.get_or_create(name="Refused", workflow=ResourceRequestWorkflow)

    request_can_manage, created = Permission.objects.get_or_create(name="Can manage Resource requests", codename="can_manage_request")

    request_accept_transition, created = Transition.objects.get_or_create(name="Accept request", workflow=ResourceRequestWorkflow, destination=request_accepted)
    request_refuse_transition, created = Transition.objects.get_or_create(name="Refuse request", workflow=ResourceRequestWorkflow, destination=request_refused)

    request_pending.transitions.add(request_accept_transition)
    request_pending.transitions.add(request_refuse_transition)
    request_refused.transitions.add(request_accept_transition)
    request_accepted.transitions.add(request_refuse_transition)

    ResourceRequestWorkflow.initial_state = request_pending
    WorkflowPermissionRelation.objects.get_or_create(workflow=ResourceRequestWorkflow, permission=request_can_manage)

    StatePermissionRelation.objects.get_or_create(state=request_pending, permission=request_can_manage, role=resource_manager)
    StatePermissionRelation.objects.get_or_create(state=request_pending, permission=request_can_manage, role=resource_owner)

    ResourceRequestWorkflow.save(force_update=True)

    # RESOURCE WORKFLOW

    ResourceWorkflow, created = Workflow.objects.get_or_create(name="ResourceWorkflow")

    resource_published, created = State.objects.get_or_create(name="Published", workflow=ResourceWorkflow)

    resource_can_read, created = Permission.objects.get_or_create(name="Can read Resource", codename="can_read_resource")
    resource_can_edit, created = Permission.objects.get_or_create(name="Can edit Resource", codename="can_edit_resource")
    resource_can_manage, created = Permission.objects.get_or_create(name="Can manage Resource", codename="can_manage_resource")

    WorkflowPermissionRelation.objects.get_or_create(workflow=ResourceWorkflow, permission=resource_can_manage)
    WorkflowPermissionRelation.objects.get_or_create(workflow=ResourceWorkflow, permission=resource_can_read)
    WorkflowPermissionRelation.objects.get_or_create(workflow=ResourceWorkflow, permission=resource_can_edit)

    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_manage, role=resource_manager)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_manage, role=resource_owner)

    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_edit, role=resource_manager)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_edit, role=resource_owner)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_edit, role=resource_editor)

    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_read, role=resource_manager)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_read, role=resource_owner)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_read, role=resource_editor)
    StatePermissionRelation.objects.get_or_create(state=resource_published, permission=resource_can_read, role=resource_reader)

    ResourceWorkflow.initial_state = resource_published

    ResourceWorkflow.save(force_update=True)
except Exception, e:
    resource_owner = None
    resource_manager = None
    resource_reader = None
    resource_editor = None
    ResourceRequestWorkflow = None

    request_pending = None
    request_accepted = None
    request_refused = None

    request_can_manage = None

    request_accept_transition = None
    request_refuse_transition = None

    ResourceWorkflow = None

    resource_published = None

    resource_can_read = None
    resource_can_edit = None
    resource_can_manage = None
    pass